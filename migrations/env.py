# migrations/env.py
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# 1) load Base from your app models
from app.models import Base

# 2) load DATABASE_URL from your app settings (which reads .env)
try:
    from app.core.config import settings
    db_url = settings.DATABASE_URL
except Exception:
    import os
    db_url = os.getenv("DATABASE_URL")

config = context.config
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
