from importlib import import_module
import asyncio
from event import event_bus
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templating = Jinja2Templates('templates')


WORKERS = [
    'models_storage',
    'logger_worker',
    'model_metadata_worker',
]


print('')
print('---IMPORT WORKERS---')
print('')
for worker in WORKERS:
    try:
        import_module(worker)
        print(f'\tWorker: {worker} imported')
    except:
        _msg = f'\tWorker: {worker} import error!'
        event_bus.request('log', _msg)
        print(_msg)
print('')
print('---END IMPORT WORKERS---')
print('')


app = FastAPI()


@app.get('/')
async def index(request: Request):
    models = ['Flower', 'Plant']
    return templating.TemplateResponse(request, 'index.html', {'models': models})


@app.get('/{model}')
async def model(request: Request, model):
    model_meta = await event_bus.request('describe_model', {'model_name': model})
    return templating.TemplateResponse(request, '_form.html', {'model': model_meta})


@app.post('/{model}')
async def create(request: Request, model):
    form_data = await request.form()
    await event_bus.request('model_save', data={'model': model, 'data': [form_data]})
    return RedirectResponse('/', status_code=304)


# from pprint import pprint


# def home():
    # parameters = {'model': "Flower", 'data':[{'name': 'Budiak'}]}
    # await event_bus.request('model_save', data=parameters)
    # parameters = {'model': 'Flower', 'pk': 2, 'data': {'name': 'Bezsmertnik', 'plant': None}}
    # print(await event_bus.request('model_update', parameters))
    # request_data = { 'model': 'Flower', 'offset': 0, 'limit': 5 }
    # records = await event_bus.request('model_records', data=request_data)
    # print(records)
    # pprint(await event_bus.request('describe_model', {'model_name': 'Flower'}))
