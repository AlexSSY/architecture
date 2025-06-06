import event
from sqlalchemy import asc, desc

from db import get_session


_registered_models = {}


@event.respond_to('get_sa_model')
async def get_sa_model(model_name):
    looking_model = _registered_models.get(model_name)
    looking_model_instance = looking_model()
    return looking_model_instance.__class__.model


# @event.respond_to('storage.models.register')
def register_model_admin(model_admin_cls):
    name = model_admin_cls.__name__.replace('Admin', '')
    _registered_models[name] = model_admin_cls


@event.respond_to('storage.models')
async def get_all_models():
    return _registered_models


@event.respond_to('storage.model')
async def get_one_model(model_name):
    return _registered_models.get(model_name)


@event.respond_to('records.count')
async def records_count(model_name):
    sa_model = await event.request('get_sa_model', model_name=model_name)
    if not sa_model:
        return 0
    
    session = next(get_session())
    return session.query(sa_model).count()


@event.respond_to('model_records')
async def model_records(model, offset=0, limit=8, sort_col_name=None, _desc=False):
    sa_model = await event.request('get_sa_model', model_name=model)
    if not sa_model:
        return []
    
    column_name = 'name'
    column = getattr(sa_model, column_name)
    
    session = next(get_session())
    return session.query(sa_model).order_by(desc(column)).limit(limit).offset(offset).all()


@event.respond_to('model_save')
async def model_save(model, data):
    sa_model = await event.request('get_sa_model', model_name=model)
    if not sa_model:
        return []
    
    session = next(get_session())

    try:
        for model_data in data:
            session.add(sa_model(**model_data))
        session.commit()
    except Exception as e:
        await event.request('log', e)
        return False

    return True


@event.respond_to('model_update')
async def model_update(model, pk, data):
    sa_model = await event.request('get_sa_model', model_name=model)
    if not sa_model:
        return []

    session = next(get_session())
    try:
        obj = session.get(sa_model, pk)
        for key, val in data.items():
            setattr(obj, key, val)
        session.commit()
    except Exception as e:
        await event.publish('log', data={'msg': e})
        return False
    
    return True
