from sqlalchemy import Column, String, Integer, Double, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Flower(Base):
    __tablename__ = 'flowers'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(length=255), unique=True)
    plant_id = Column(ForeignKey('plants.id'))

    plant = relationship('Plant', back_populates='flowers')

    def __repr__(self):
        return self.name


class Plant(Base):
    __tablename__ = 'plants'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(length=255), unique=True)
    x_cord = Column(Double)
    y_cord = Column(Double)

    flowers = relationship('Flower', back_populates='plant')

    def __repr__(self):
        return self.name

from db import engine
Base.metadata.create_all(engine)
