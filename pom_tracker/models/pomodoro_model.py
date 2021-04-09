from sqlalchemy import Column, Integer, Text, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database.db import Base


class PomodoroModel(Base):
    __tablename__ = 'pomodoro'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    task = Column(Text, nullable=False)
    review = Column(Text, nullable=False)
    created = Column(Date, nullable=False)
    distractions = Column(Integer, nullable=False)
    pom_success = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    flags = relationship('PomFlagsModel', back_populates="pom")

    __table_args__ = (UniqueConstraint('created', 'start_time', 'user_id',
                                       name='user_date_start_time_uc',
                                       ),
                      )

    def __repr__(self):
        return "<Pomodoro(id='%s', user_id='%s', task='%s', review='%s', " \
               "flags=%s, created='%s', distractions='%s', pom_success='%s'," \
               " start_time='%s', end_time='%s')>" % (
                   self.id, self.user_id, self.task, self.review, self.flags,
                   self.created, self.distractions, self.pom_success,
                   self.start_time, self.end_time)
