from sqlalchemy import Column, String, Integer, Double, ForeignKey
from sqlalchemy.orm import relationship
from models_storage import register_model_admin

from db import Base


class Flower(Base):
    __tablename__ = 'flowers'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(length=255), unique=True, nullable=False)
    plant_id = Column(ForeignKey('plants.id'))

    plant = relationship('Plant', back_populates='flowers')

    def __repr__(self):
        return self.name


class Plant(Base):
    __tablename__ = 'plants'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(length=255), unique=True, nullable=False)
    x_cord = Column(Double)
    y_cord = Column(Double)

    flowers = relationship('Flower', back_populates='plant')

    def __repr__(self):
        return self.name


class ModelAdmin:
    list_display = '__all__'
    fields = '__all__'
    readonly_fields = ()
    model = None


class FlowerAdmin(ModelAdmin):
    model = Flower


class PlantAdmin(ModelAdmin):
    model = Plant


_model_admin_registry = {'FlowerAdmin': FlowerAdmin}


import event
@event.respond_to('model_admin')
async def model_admin(data):
    name = data['name']
    return _model_admin_registry[name]


@event.respond_to('model_admin_meta')
async def model_admin_meta(data):
    model_admin_name = data['name']
    model_admin_class = await event.request('model_admin', name=model_admin_name)
    model_admin_instance = model_admin_class()


register_model_admin(FlowerAdmin)
register_model_admin(PlantAdmin)

from db import engine
Base.metadata.create_all(engine)
