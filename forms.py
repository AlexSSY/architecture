import asyncio
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from pprint import pprint
from models import Flower
from db import get_session


class FlowerSchema(SQLAlchemySchema):
    class Meta:
        model = Flower
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    name = auto_field()
    plant_id = auto_field()
    plant = auto_field()


class FlowerAdmin:
    fields = '__all__'
    readonly_fields = ['id']
    model = Flower


flower_schema = FlowerSchema()
session = next(get_session())
pprint(flower_schema.validate({'name': 'Pink', 'plant_id': 1}, session=session))

from model_metadata_worker import describe_model

async def main():
    pprint( await describe_model(Flower))

asyncio.run(main())
