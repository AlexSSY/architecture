import models
import event
from db import get_session


@event.respond_to('get_sa_model')
async def get_sa_model(model_name):
    looking_model = models.__dict__.get(model_name)
    return looking_model


@event.respond_to('model_records')
async def model_records(model, offset, limit):
    sa_model = await event.request('get_sa_model', {'model_name': model})
    if not sa_model:
        return []
    
    session = next(get_session())
    return session.query(sa_model).limit(limit).offset(offset).all()


@event.respond_to('model_save')
async def model_save(model, data):
    sa_model = await event.request('get_sa_model', {'model_name': model})
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
    sa_model = await event.request('get_sa_model', {'model_name': model})
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
