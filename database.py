
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import db_url_object

metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    tool_id = sq.Column(sq.Integer, primary_key=True)



def add_profile(engine, profile_id, tool_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, tool_id=tool_id)
        session.add(to_bd)
        session.commit()


def check_profile(engine, profile_id, tool_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.tool_id == tool_id
        ).first()
        return True if from_bd else False

if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    add_profile(engine, 2113 , 124512)
    res = check_profile(engine, 2112, 1245121)
    print(res)

