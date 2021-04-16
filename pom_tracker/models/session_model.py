from sqlalchemy import Column, Integer, Text, DateTime
from ..dependencies.database_manager import dbm


class SessionModel(dbm.Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    hash = Column(Text, nullable=False, unique=True)
    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Session(id='%s', hash='%s', created='%s', modified='%s')>" % (
            self.id, self.hash, self.created, self.modified)
