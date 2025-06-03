import models
from event import event_bus
from db import get_session


async def get_sa_model(data):
    model_name = data['model_name']
    looking_model = models.__dict__.get(model_name)
    return looking_model


event_bus.respond_to('get_sa_model', get_sa_model)


async def model_records(data):
    model = data['model']
    offset = data.get('offset')
    limit = data.get('limit')

    sa_model = await event_bus.request('get_sa_model', {'model_name': model})
    if not sa_model:
        return []
    
    session = next(get_session())
    return session.query(sa_model).limit(limit).offset(offset).all()


event_bus.respond_to('model_records', model_records)


async def model_save(data):
    model = data['model']
    data = data['data']

    sa_model = await event_bus.request('get_sa_model', {'model_name': model})
    if not sa_model:
        return []
    
    session = next(get_session())

    try:
        for model_data in data:
            session.add(sa_model(**model_data))
        session.commit()
    except Exception as e:
        await event_bus.request('log', e)
        return False

    return True


event_bus.respond_to('model_save', model_save)


async def model_update(data):
    model = data['model']
    pk = data['pk']
    data_ = data['data']

    sa_model = await event_bus.request('get_sa_model', {'model_name': model})
    if not sa_model:
        return []

    session = next(get_session())
    try:
        obj = session.get(sa_model, pk)
        for key, val in data_.items():
            setattr(obj, key, val)
        session.commit()
    except Exception as e:
        await event_bus.publish('log', data={'msg': e})
        return False
    
    return True


event_bus.respond_to('model_update', model_update)
