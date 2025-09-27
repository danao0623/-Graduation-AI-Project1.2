import asyncio
import contextlib
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import make_url
from typing import Type, Dict, Tuple
from core.environment import Environment

class Database:
    """
    Database class that handles database initialization, connection management, and session lifecycle.
    Allows flexible configuration of the database URL and the declarative base model.
    """
    _instances: Dict[Tuple[str, Type[DeclarativeMeta]], 'Database'] = {}

    @classmethod
    async def initialize(cls):
        """
        Initializes all database instances based on URLs found in the Environment configuration.
        Creates all databases and tables for each instance.
        """
        database_urls = Environment.retrieve("DATABASE")
        if not isinstance(database_urls, dict):
            raise ValueError("Invalid database configuration in Environment. Expected a dictionary of database URLs.")

        # Create and initialize all database instances
        tasks = []
        for key, database_url in database_urls.items():
            try:
                db_instance = cls(database_url)
                tasks.append(db_instance.create_db_and_tables())
            except Exception as e:
                logger = Environment.logger("DATABASE")
                logger.error(f"Failed to initialize database for key '{key}': {e}".replace("\n", ""))

        # Run all tasks asynchronously
        await asyncio.gather(*tasks)
    
    @classmethod
    def singleton(cls, keyword: str):
        """
        Create a Database singleton using a keyword to fetch the database URL from the Environment configuration.

        :param keyword: The keyword used to retrieve the database URL from the system configuration.
        :return: An instance of the Database class associated with the fetched URL.
        :raises KeyError: If the keyword does not correspond to any entry in the configuration.
        """
        # Fetch the database URL from the Environment configuration
        database_url = Environment.retrieve("DATABASE", keyword)
        if database_url is None:
            raise KeyError(f"Database URL for keyword '{keyword}' not found in the configuration.")
        
        # Return an existing or new Database instance based on the URL
        return cls(database_url)
    
    def __new__(cls, database_url: str):
        if database_url not in cls._instances:
            instance = super(Database, cls).__new__(cls)
            instance.init(database_url)
            cls._instances[database_url] = instance
        return cls._instances[database_url]


    def init(self, database_url: str):
        """
        Initializes the DBMS object with the given database URL.

        :param database_url: The URL string for the database connection.
        :raises ValueError: If the database URL is not provided.
        """
        self.logger = Environment.logger("DATABASE")
        self.database_url = database_url

        if not self.database_url:
            self.logger.error("DATABASE_URL not provided.")
            raise ValueError("DATABASE_URL is required for initialization.")

        self.url = make_url(self.database_url)
        self.engine_options = {
            "echo": False,  # Disable SQL logging by default
            "future": True  # Enable SQLAlchemy 2.0 style
        }

        # Configure specific options based on the database type
        if self.url.get_backend_name() == 'sqlite':
            self.engine_options["connect_args"] = {"check_same_thread": False}
        else:
            self.engine_options["pool_size"] = 10
            self.engine_options["max_overflow"] = 5

        # Async engine and session maker
        self.async_engine = create_async_engine(self.database_url, **self.engine_options)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False)
        
        # Sync engine and session maker
        self.sync_engine = create_engine(self.database_url, **self.engine_options)
        self.sync_session_maker = sessionmaker(self.sync_engine, expire_on_commit=False)
        
        self.Base: Type[DeclarativeMeta] = declarative_base()

    async def create_db_and_tables(self):
        """
        Asynchronously create database and tables based on the declarative base.
        
        :raises Exception: If any error occurs during the table creation process.
        """
        self.logger.info("Starting database and table creation.")
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(self.Base.metadata.create_all)
            self.logger.info("Database and tables created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating database and tables: {e}".replace("\n", ""))
            raise

    async def drop_db_and_tables(self):
        """
        Asynchronously drop all database tables based on the declarative base.

        :raises Exception: If any error occurs during the table deletion process.
        """
        self.logger.info("Starting database and table deletion.")
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(self.Base.metadata.drop_all)
            self.logger.info("Database and tables dropped successfully.")
        except Exception as e:
            self.logger.error(f"Error dropping database and tables: {e}".replace("\n", ""))
            raise

    def get_session(self):
        """
        Provides a context manager for a synchronous session generator.

        :yields: An instance of Session for database operations.
        :raises Exception: If an error occurs during session handling.
        """
        try:
            with self.sync_session_maker() as session:
                yield session
        except Exception as e:
            self.logger.error(f"Error during session handling: {e}".replace("\n", ""))
            raise

    def get_session_context(self):
        """
        Returns a context manager for handling a synchronous database session.

        :return: A context manager that yields a synchronous session.
        """
        return contextlib.contextmanager(self.get_session)()

    async def get_async_session(self):
        """
        Provides a context manager for an asynchronous session generator.

        :yields: An instance of AsyncSession for database operations.
        :raises Exception: If an error occurs during session handling.
        """
        try:
            async with self.async_session_maker() as session:
                yield session
        except Exception as e:
            self.logger.error(f"Error during session handling: {e}".replace("\n", ""))
            raise

    def get_async_session_context(self):
        """
        Returns a context manager for handling a database session.

        :return: A context manager that yields an asynchronous session.
        """
        return contextlib.asynccontextmanager(self.get_async_session)()
    
    def get_base(self):
        """
        Returns the Base attribute of the Database class.
        """
        return self.Base        

    async def dispose_engine(self):
        """
        Asynchronously dispose of the database engine, releasing all resources.

        :raises Exception: If an error occurs while disposing of the engine.
        """
        self.logger.info("Disposing engine and releasing resources.")
        try:
            await self.async_engine.dispose()
            self.logger.info("Asynchronous engine disposed successfully.")
            await self.sync_engine.dispose()
            self.logger.info("Synchronous engine disposed successfully.")            
        except Exception as e:
            self.logger.error(f"Error disposing engine: {e}".replace("\n", ""))
            raise

