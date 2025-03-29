from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()

from models import *


class Database:

    database_url: str
    create_session: sessionmaker[Session]
    engine: Engine
    metadata = MetaData()
    connected = False

    def __init__(self):
        pass

    def set_url(self, database_url: str):
        """
        Sets the Postgres database url.

        Args:
            database_url: The Postgres database url
        """
        self.database_url = database_url

    def connect(self) -> bool:
        """
        Connects to the database.

        Returns: True if the connection was successful, False otherwise.

        """
        try:
            self.engine = create_engine(self.database_url)
            self.create_session = sessionmaker(bind=self.engine)
            self.metadata.reflect(bind=self.engine)
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    def close(self):
        """
        Closes the database connection.
        """
        self.engine.dispose()
