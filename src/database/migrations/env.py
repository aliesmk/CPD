from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv
import os
from alembic import context  # ایمپورت context
from src.database.models import Base  # ایمپورت Base از models.py

# لود متغیرهای محیطی
load_dotenv()

# تنظیم Alembic Config object
config = context.config

# تنظیم URL دیتابیس از .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# تنظیم لاگ‌ها
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# تنظیم metadata برای autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """اجرای migrations در حالت آفلاین"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """اجرای migrations در حالت آنلاین"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()