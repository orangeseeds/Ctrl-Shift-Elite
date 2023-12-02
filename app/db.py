from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# 2.-Turn on database engine
# ensure this is the correct path for the sqlite file.
engine = create_engine('sqlite:///sqlite.db')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
