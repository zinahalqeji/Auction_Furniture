from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from config import DATABASE

url = URL.create(
    drivername="postgresql+psycopg2",
    host=DATABASE["host"],
    port=DATABASE["port"],
    username=DATABASE["username"],
    password=DATABASE["password"],
    database=DATABASE["database"]
)

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)
