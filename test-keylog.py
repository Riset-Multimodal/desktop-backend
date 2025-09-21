import sys
import time
import json
import threading
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pynput import keyboard, mouse
from collections import deque
import math

# --- Konfigurasi ---
PROCESSING_INTERVAL = 5
PAUSE_THRESHOLD = 1.0
API_ENDPOINT = "http://localhost:8000/log"
MOUSE_SAMPLE_INTERVAL = 0.25  # 250ms untuk sampling posisi mouse
SAMPLES_PER_INTERVAL = int(PROCESSING_INTERVAL / MOUSE_SAMPLE_INTERVAL)  # 20 sampel


def calculate_distance(x1, y1, x2, y2):
    """Menghitung jarak Euclidean antara dua titik."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_velocity(positions, timestamps):
    """Menghitung kecepatan dari serangkaian posisi dan timestamp."""
    if len(positions) < 2:
        return []

    velocities = []
    for i in range(1, len(positions)):
        x1, y1 = positions[i - 1]
        x2, y2 = positions[i]
        dt = timestamps[i] - timestamps[i - 1]

        if dt > 0:
            distance = calculate_distance(x1, y1, x2, y2)
            velocity = distance / dt  # pixels per second
            velocities.append(velocity)

    return velocities


def calculate_acceleration(velocities, timestamps):
    """Menghitung akselerasi dari serangkaian kecepatan."""
    if len(velocities) < 2:
        return []

    accelerations = []
    for i in range(1, len(velocities)):
        dv = velocities[i] - velocities[i - 1]
        dt = timestamps[i] - timestamps[i - 1]

        if dt > 0:
            acceleration = dv / dt  # pixels per second^2
            accelerations.append(acceleration)

    return accelerations


def calculate_jerkiness(positions, timestamps):
    """
    Menghitung jerkiness sebagai RMS dari magnitude jerk vector.
    Implementasi berdasarkan Flash & Hogan (1985) minimum jerk principle.

    Jerk adalah turunan ketiga dari posisi (derivative of acceleration).
    Formula: jerk = d³r/dt³ dimana r adalah position vector
    """
    if len(positions) < 4 or len(timestamps) < 4:
        return 0.0

    # Step 1: Hitung velocity vectors
    velocities = []
    vel_timestamps = []
    for i in range(1, len(positions)):
        dt = timestamps[i] - timestamps[i - 1]
        if dt > 0:
            vx = (positions[i][0] - positions[i - 1][0]) / dt
            vy = (positions[i][1] - positions[i - 1][1]) / dt
            velocities.append((vx, vy))
            vel_timestamps.append((timestamps[i] + timestamps[i - 1]) / 2)  # Mid-point time

    if len(velocities) < 2:
        return 0.0

    # Step 2: Hitung acceleration vectors
    accelerations = []
    acc_timestamps = []
    for i in range(1, len(velocities)):
        dt = vel_timestamps[i] - vel_timestamps[i - 1]
        if dt > 0:
            ax = (velocities[i][0] - velocities[i - 1][0]) / dt
            ay = (velocities[i][1] - velocities[i - 1][1]) / dt
            accelerations.append((ax, ay))
            acc_timestamps.append((vel_timestamps[i] + vel_timestamps[i - 1]) / 2)

    if len(accelerations) < 2:
        return 0.0

    # Step 3: Hitung jerk vectors
    jerks = []
    for i in range(1, len(accelerations)):
        dt = acc_timestamps[i] - acc_timestamps[i - 1]
        if dt > 0:
            jx = (accelerations[i][0] - accelerations[i - 1][0]) / dt
            jy = (accelerations[i][1] - accelerations[i - 1][1]) / dt
            # Magnitude of jerk vector
            jerk_magnitude = np.sqrt(jx ** 2 + jy ** 2)
            jerks.append(jerk_magnitude)

    if not jerks:
        return 0.0

    # Step 4: RMS jerk (Root Mean Square)
    # Ini adalah standard approach dalam motor control literature
    rms_jerk = np.sqrt(np.mean([j ** 2 for j in jerks]))
    return rms_jerk


def estimate_wpm(key_events, interval_duration_seconds=PROCESSING_INTERVAL):
    """
    Mengestimasi Words Per Minute (WPM) berdasarkan keystroke patterns.

    Menggunakan beberapa metode estimasi:
    1. Character-based: Asumsi rata-rata 5 karakter per kata (standar typing test)
    2. Space-based: Menghitung jumlah kata berdasarkan spasi yang diketik
    3. Adjusted for corrections: Mengurangi estimasi berdasarkan backspace/delete

    Referensi:
    - Standar typing test menggunakan 5 karakter = 1 kata
    - Vizer et al. (2009) untuk keystroke dynamics dalam stress detection
    """
    press_events = [e for e in key_events if e[0] == 'press']

    if not press_events:
        return 0.0

    # Hitung berbagai jenis keystroke
    total_keystrokes = len(press_events)
    space_count = sum(1 for _, key, _ in press_events if key == keyboard.Key.space)
    backspace_count = sum(1 for _, key, _ in press_events if key == keyboard.Key.backspace)
    delete_count = sum(1 for _, key, _ in press_events if key == keyboard.Key.delete)

    # Method 1: Character-based estimation (5 chars = 1 word)
    # Kurangi backspace/delete karena itu bukan productive typing
    productive_keystrokes = max(0, total_keystrokes - backspace_count - delete_count)
    estimated_chars = productive_keystrokes * 0.8  # 80% assumption for actual characters (exclude function keys, etc.)
    words_char_based = estimated_chars / 5.0

    # Method 2: Space-based estimation (lebih akurat jika banyak spasi)
    words_space_based = space_count  # Jumlah spasi ≈ jumlah kata - 1, tapi kita approximate

    # Method 3: Combined approach (lebih robust)
    # Jika ada cukup spasi, gunakan space-based, otherwise gunakan char-based
    if space_count >= 3:  # Minimal 3 spasi dalam interval
        estimated_words = max(words_space_based, words_char_based * 0.7)
    else:
        estimated_words = words_char_based

    # Konversi ke WPM (words per minute)
    minutes = interval_duration_seconds / 60.0
    wpm = estimated_words / minutes if minutes > 0 else 0.0

    # Clamp WPM ke range yang masuk akal (0-200 WPM)
    wpm = max(0.0, min(200.0, wpm))

    return wpm


def calculate_typing_rhythm_consistency(press_events):
    """
    Menghitung konsistensi ritme mengetik sebagai indikator stress.
    Stress cenderung membuat typing rhythm menjadi tidak konsisten.

    Referensi: Vizer et al. (2009) - keystroke dynamics untuk stress detection
    """
    if len(press_events) < 3:
        return 1.0  # Perfect consistency for insufficient data

    # Hitung interval antar keystroke
    intervals = []
    for i in range(1, len(press_events)):
        interval = press_events[i][2] - press_events[i - 1][2]  # timestamp difference
        if 0.01 <= interval <= 2.0:  # Filter reasonable intervals (10ms to 2s)
            intervals.append(interval)

    if len(intervals) < 2:
        return 1.0

    # Konsistensi = 1 - (coefficient of variation)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    if mean_interval == 0:
        return 1.0

    coefficient_of_variation = std_interval / mean_interval
    consistency = max(0.0, 1.0 - coefficient_of_variation)

    return consistency


def calculate_mouse_accuracy(positions):
    """
    Menghitung mouse accuracy berdasarkan Banholzer et al. (2021).
    Accuracy = proporsi kejadian dimana arah gerakan tidak berubah.
    Semakin tinggi nilai accuracy, semakin sedikit koreksi arah yang dilakukan.
    """
    if len(positions) < 3:
        return 1.0  # Perfect accuracy for insufficient data

    direction_changes = 0
    total_moves = len(positions) - 1

    for i in range(2, len(positions)):
        # Previous direction
        prev_dx = positions[i - 1][0] - positions[i - 2][0]
        prev_dy = positions[i - 1][1] - positions[i - 2][1]

        # Current direction
        curr_dx = positions[i][0] - positions[i - 1][0]
        curr_dy = positions[i][1] - positions[i - 1][1]

        # Check if direction changed (sign change)
        if (np.sign(prev_dx) != np.sign(curr_dx) and curr_dx != 0) or \
                (np.sign(prev_dy) != np.sign(curr_dy) and curr_dy != 0):
            direction_changes += 1

    # Accuracy = 1 - (proportion of direction changes)
    accuracy = 1.0 - (direction_changes / max(total_moves - 1, 1))
    return max(0.0, accuracy)  # Ensure non-negative


def format_sequence(sequence, precision=2):
    """
    Format sequence menjadi string yang compact dan mudah dibaca.
    Contoh: [100.23, 105.45, 110.67] -> "100.23,105.45,110.67"
    """
    if not sequence:
        return ""

    return ",".join([f"{val:.{precision}f}" for val in sequence])


def calculate_features(events, mouse_counters, mouse_positions, mouse_timestamps):
    """
    Menghitung semua fitur dari buffer event keyboard dan mouse.
    """
    key_events = [e for e in events if e[0] in ('press', 'release')]
    press_events_only = [e for e in key_events if e[0] == 'press']

    keystroke_count = len(press_events_only)

    # Menghitung ketukan tombol spesifik
    backspace_count = sum(1 for _, key, _ in press_events_only if key == keyboard.Key.backspace)
    delete_count = sum(1 for _, key, _ in press_events_only if key == keyboard.Key.delete)
    space_count = sum(1 for _, key, _ in press_events_only if key == keyboard.Key.space)

    error_rate = ((backspace_count + delete_count) / keystroke_count) if keystroke_count > 0 else 0

    dwell_times, flight_times, digraph_times = [], [], []
    key_press_times = {}
    last_press_time = None
    last_release_time = None

    for event_type, key, timestamp in key_events:
        if event_type == 'press':
            if last_press_time: digraph_times.append(timestamp - last_press_time)
            if last_release_time: flight_times.append(timestamp - last_release_time)
            key_press_times[str(key)] = timestamp
            last_press_time = timestamp
        elif event_type == 'release':
            if str(key) in key_press_times:
                dwell_times.append(timestamp - key_press_times.pop(str(key), timestamp))
            last_release_time = timestamp

    pauses, burst_lengths = [], []
    current_burst_length = 0
    last_t = key_events[0][2] if key_events else None

    for _, _, timestamp in key_events:
        if last_t and (timestamp - last_t) > PAUSE_THRESHOLD:
            pauses.append(timestamp - last_t)
            if current_burst_length > 0: burst_lengths.append(current_burst_length)
            current_burst_length = 0
        else:
            current_burst_length += 1
        last_t = timestamp
    if current_burst_length > 0: burst_lengths.append(current_burst_length)

    # === TYPING DYNAMICS FEATURES ===
    wpm = estimate_wpm(key_events)
    typing_rhythm_consistency = calculate_typing_rhythm_consistency(press_events_only)

    # === MOUSE DYNAMICS FEATURES ===
    mouse_speed = 0.0
    mouse_jerkiness = 0.0
    mouse_accuracy = 1.0  # Perfect accuracy as default
    raw_x_sequence = ""
    raw_y_sequence = ""

    if len(mouse_positions) >= 2 and len(mouse_timestamps) >= 2:
        # Menghitung kecepatan mouse
        velocities = calculate_velocity(mouse_positions, mouse_timestamps)
        if velocities:
            mouse_speed = np.mean(velocities)

        # Menghitung accuracy berdasarkan Banholzer et al. (2021)
        mouse_accuracy = calculate_mouse_accuracy(mouse_positions)

        # Menghitung jerkiness (variabilitas dari jerk - turunan ketiga posisi)
        if len(mouse_positions) >= 4:
            mouse_jerkiness = calculate_jerkiness(mouse_positions, mouse_timestamps)

        # Membuat raw sequences dari posisi yang di-sample setiap 250ms
        x_coords = [pos[0] for pos in mouse_positions]
        y_coords = [pos[1] for pos in mouse_positions]

        raw_x_sequence = format_sequence(x_coords)
        raw_y_sequence = format_sequence(y_coords)

    # Menggunakan np.errstate untuk menghindari warning saat membagi dengan nol
    with np.errstate(divide='ignore', invalid='ignore'):
        return {
            "timestamp": datetime.now().isoformat(),
            "keystroke_count": keystroke_count,
            "left_click_count": mouse_counters.get('left_click', 0),
            "right_click_count": mouse_counters.get('right_click', 0),
            "scroll_up": mouse_counters.get('scroll_up', 0),
            "scroll_down": mouse_counters.get('scroll_down', 0),
            "space_count": space_count,
            "error_rate": error_rate,
            "mean_dwell_time_ms": np.nanmean(dwell_times) * 1000 if dwell_times else 0,
            "std_dev_dwell_time_ms": np.nanstd(dwell_times) * 1000 if dwell_times else 0,
            "mean_flight_time_ms": np.nanmean(flight_times) * 1000 if flight_times else 0,
            "std_dev_flight_time_ms": np.nanstd(flight_times) * 1000 if flight_times else 0,
            "mean_digraph_time_ms": np.nanmean(digraph_times) * 1000 if digraph_times else 0,
            "std_dev_digraph_time_ms": np.nanstd(digraph_times) * 1000 if digraph_times else 0,
            "pause_count": len(pauses),
            "mean_pause_duration_ms": np.nanmean(pauses) * 1000 if pauses else 0,
            "mean_burst_length": np.nanmean(burst_lengths) if burst_lengths else 0,
            # Typing dynamics features
            "words_per_minute": float(wpm),
            "typing_rhythm_consistency": float(typing_rhythm_consistency),
            # Mouse dynamics features
            "mouse_speed": float(mouse_speed),
            "mouse_accuracy": float(mouse_accuracy),  # Fitur baru dari Banholzer et al.
            "mouse_jerkiness": float(mouse_jerkiness),
            "raw_x_sequence": raw_x_sequence,
            "raw_y_sequence": raw_y_sequence
        }


def post_data_to_api(flat_json_data):
    """Mengirim data ke API."""
    try:
        requests.post(API_ENDPOINT, json=flat_json_data, timeout=2)
        print(f"Successfully posted data to {API_ENDPOINT}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"API post failed: {e}", file=sys.stderr)


class MonitoringService:
    def __init__(self):
        self.is_monitoring = False
        self.events_buffer = []
        self.session_feature_vectors = []
        self.processing_thread = None
        self.mouse_sampling_thread = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self.lock = threading.Lock()
        self.mouse_counters = {"left_click": 0, "right_click": 0, "scroll_up": 0, "scroll_down": 0}

        # Mouse dynamics tracking
        self.current_mouse_pos = (0, 0)
        self.mouse_positions_buffer = deque(maxlen=SAMPLES_PER_INTERVAL)
        self.mouse_timestamps_buffer = deque(maxlen=SAMPLES_PER_INTERVAL)

    def on_press(self, key):
        if self.is_monitoring:
            with self.lock:
                self.events_buffer.append(('press', key, time.time()))

    def on_release(self, key):
        if self.is_monitoring:
            with self.lock:
                self.events_buffer.append(('release', key, time.time()))

    def on_click(self, x, y, button, pressed):
        if self.is_monitoring and pressed:
            with self.lock:
                if button == mouse.Button.left:
                    self.mouse_counters["left_click"] += 1
                elif button == mouse.Button.right:
                    self.mouse_counters["right_click"] += 1

    def on_scroll(self, x, y, dx, dy):
        if self.is_monitoring:
            with self.lock:
                if dy > 0:
                    self.mouse_counters["scroll_up"] += 1
                elif dy < 0:
                    self.mouse_counters["scroll_down"] += 1

    def on_move(self, x, y):
        """Event handler untuk pergerakan mouse."""
        if self.is_monitoring:
            self.current_mouse_pos = (x, y)

    def mouse_sampling_loop(self):
        """
        Thread terpisah untuk sampling posisi mouse setiap 250ms.
        Ini memastikan kita mendapat sampel yang konsisten terlepas dari frekuensi pergerakan mouse.
        """
        while self.is_monitoring:
            current_time = time.time()
            current_pos = self.current_mouse_pos

            with self.lock:
                self.mouse_positions_buffer.append(current_pos)
                self.mouse_timestamps_buffer.append(current_time)

            time.sleep(MOUSE_SAMPLE_INTERVAL)

    def start_monitoring(self):
        if self.is_monitoring:
            return

        self.is_monitoring = True

        # Listener untuk keyboard
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        # Listener untuk mouse (termasuk on_move untuk tracking posisi)
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll,
            on_move=self.on_move
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

        # Thread untuk processing utama
        self.processing_thread = threading.Thread(target=self.process_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()

        # Thread untuk sampling mouse positions
        self.mouse_sampling_thread = threading.Thread(target=self.mouse_sampling_loop)
        self.mouse_sampling_thread.daemon = True
        self.mouse_sampling_thread.start()

    def process_loop(self):
        while self.is_monitoring:
            time.sleep(PROCESSING_INTERVAL)
            if not self.is_monitoring:
                break

            with self.lock:
                # Copy buffer events
                events_this_interval = self.events_buffer.copy()
                mouse_counters_this_interval = self.mouse_counters.copy()

                # Copy mouse positions and timestamps
                mouse_positions_this_interval = list(self.mouse_positions_buffer)
                mouse_timestamps_this_interval = list(self.mouse_timestamps_buffer)

                # Clear buffers
                self.events_buffer.clear()
                self.mouse_counters = {key: 0 for key in self.mouse_counters}
                self.mouse_positions_buffer.clear()
                self.mouse_timestamps_buffer.clear()

            # Hitung features
            feature_data = calculate_features(
                events_this_interval,
                mouse_counters_this_interval,
                mouse_positions_this_interval,
                mouse_timestamps_this_interval
            )
            feature_data['type'] = 'realtime'

            self.session_feature_vectors.append(feature_data)
            # post_data_to_api(feature_data)  # Uncomment jika ingin kirim ke API
            print(json.dumps(feature_data), flush=True)

    def stop_and_analyze(self):
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        time.sleep(0.1)

        if not self.session_feature_vectors:
            final_data = {"type": "final", "message": "Tidak ada data yang direkam."}
            print(json.dumps(final_data), flush=True)
            return

        df = pd.DataFrame(self.session_feature_vectors)
        numeric_df = df.drop(columns=['type', 'timestamp', 'raw_x_sequence', 'raw_y_sequence'], errors='ignore')
        average_features = numeric_df.mean().to_dict()

        final_output = {
            "type": "final",
            **average_features
        }
        print(json.dumps(final_output), flush=True)


# --- Loop Utama ---
if __name__ == "__main__":
    service = MonitoringService()
    service.start_monitoring()
    print("Enhanced keylogger with mouse dynamics monitoring started.", file=sys.stderr)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop_and_analyze()
        print("Keylogger stopped.", file=sys.stderr)