from logging.config import fileConfig
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from alembic import context
import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(override=True)

from app.database import Base
from app import models

config = context.config
database_url = os.getenv("DATABASE_URL")
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online() -> None:
    connectable = create_engine(os.getenv("DATABASE_URL"))
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    pass
else:
    run_migrations_online()

  