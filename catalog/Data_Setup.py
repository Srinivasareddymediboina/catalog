import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class PerfumeCompanyName(Base):
    __tablename__ = 'perfumecompanyname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="perfumecompanyname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class PerfumeName(Base):
    __tablename__ = 'pefumename'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    flavour = Column(String(150))
    color = Column(String(150))
    cost = Column(String(150))
    rlink = Column(String(500))
    date = Column(DateTime, nullable=False)
    perfumecompanynameid = Column(Integer, ForeignKey('perfumecompanyname.id'))
    perfumecompanyname = relationship(
        PerfumeCompanyName, backref=backref('pefumename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="pefumename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'flavour': self. flavour,
            'cost': self. cost,
            'color': self. color,
            'rlink': self.rlink,
            'date': self. date,
            'id': self. id
        }

engine = create_engine('sqlite:///perfumes.db')
Base.metadata.create_all(engine)
