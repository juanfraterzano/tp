from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:dbcoding1$L_@localhost:5432/tpLab"

class DataBase():
    def __init__(self, connection_string: str = DATABASE_URL, echo: bool = True):
        self.engine = create_engine(connection_string, echo=echo)

    @property
    def SessionLocal(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_all(self):
        ORMBase.metadata.create_all(self.engine)


    def drop_all(self): 
        ORMBase.metadata.drop_all(bind=self.engine)


ORMBase = declarative_base()

db_instance = DataBase()