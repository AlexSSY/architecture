from importlib import import_module
import asyncio
from event import event_bus
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templating = Jinja2Templates('templates')


async def render_template_handler(data):
    template_path = data['path']
    context = data['context']
    template = templating.get_template(template_path)
    return template.render(context)


event_bus.respond_to('render_template', render_template_handler)


WORKERS = [
    'models_storage',
    'logger_worker',
    'model_metadata_worker',
    'forms',
    'models',
]


async def load_workers():
    print('')
    print('---IMPORT WORKERS---')
    print('')
    for worker in WORKERS:
        try:
            import_module(worker)
            print(f'\tWorker: {worker} imported')
        except Exception as e:
            _msg = f'\tWorker: {worker} import error! {e}'
            print(_msg)
    print('')
    print('---END IMPORT WORKERS---')
    print('')


app = FastAPI()


@app.on_event('startup')
async def startup_event():
    await load_workers()


@app.get('/')
async def index(request: Request):
    models = ['Flower', 'Plant']
    return templating.TemplateResponse(request, 'index.html', {'models': models})


@app.get('/test')
async def test(request: Request):
    form_html = await event_bus.request('form_html', data={
        'name': 'Form',
        'method': 'post',
        'action': '/test'
    })
    return templating.TemplateResponse(request, 'test.html', {'form_html': form_html})


@app.post('/test')
async def post_test(request: Request):
    return await request.form()


@app.get('/Flower')
async def flower(request: Request):
    return templating.TemplateResponse(request, 'flower.html', {})


@app.get('/{model}')
async def model(request: Request, model):
    model_meta = await event_bus.request('describe_model', {'model_name': model})
    return templating.TemplateResponse(request, '_form.html', {'model': model_meta})


@app.post('/{model}')
async def create(request: Request, model):
    form_data = await request.form()
    await event_bus.request('model_save', data={'model': model, 'data': [form_data]})
    return RedirectResponse('/', status_code=303)




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
