from sqlalchemy import select
from sqlalchemy.orm import Session
from db_engine import sync_engine
from models import User


def seed_user_if_needed():
    with Session(sync_engine) as session:
        with session.begin():
            if session.execute(select(User)).first() is not None:
                print("At least one user already exists, skipping seeding")
                return
            print("Seeding user")
            session.add(User(name="Alice"))
            session.add(User(name="Robby", is_agent=True))
            session.commit()
