from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Optional


class Venue(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    category: str
    address: str
    region: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    distance: int


sqlite_file_name = "Venues.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def insert_data(new_venue_data):
    new_venue = Venue(**new_venue_data)
    with Session(engine) as session:
        session.add(new_venue)
        session.commit()
