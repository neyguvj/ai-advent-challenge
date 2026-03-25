import datetime
import enum

from sqlalchemy import (
    create_engine,
    Column,
    Enum,
    Integer,
    Text,
    ForeignKey,
    UUID,
    Time,
    inspect,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DictSerialisable:
    def to_dict(self):
        """Returns a dictionary representation of the ORM model instance."""
        mapper = inspect(self).mapper
        data = {}
        for column in mapper.attrs:
            attr_name = column.key
            value = getattr(self, attr_name)

            if isinstance(value, enum.Enum):
                data[attr_name] = value.name
            elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                data[attr_name] = value.isoformat()
            else:
                data[attr_name] = value

        return data


class User(DictSerialisable, Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)


class Session(DictSerialisable, Base):
    __tablename__ = "sessions"
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)


class Role(enum.Enum):
    system = 0
    assistant = 1
    human = 2


class Message(DictSerialisable, Base):
    __tablename__ = "messages"
    id = Column(UUID, primary_key=True)
    session_id = Column(
        UUID, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    timestamp = Column(Time)
    role = Column(Enum(Role))
    content = Column(Text, nullable=False)


class Statistics(DictSerialisable, Base):
    __tablename__ = "statistics"
    session_id = Column(
        UUID,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    last_input_tokens = Column(Integer, default=0)
    last_output_tokens = Column(Integer, default=0)
