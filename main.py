from importlib import import_module
import event
from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loader import Loader
import asyncio


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event('startup')
async def startup_event():
    config = {
        'services': [
            'models_storage',
            'logger_worker',
            'model_metadata_worker',
            'forms',
            'models',
            'services.templating',
        ]
    }
    await Loader.load(config)


@app.get('/')
async def dashboard(request: Request):
    templating = await event.request('templating.get')
    return templating.TemplateResponse(request, 'dashboard.html', {})


@app.get('/favicon.ico')
async def favicon():
    return RedirectResponse('/static/favicon.ico')


@app.get('/x/models')
async def render_template(request: Request):
    templating = await event.request('templating.get')
    registered_models = await event.request('storage.models')
    return templating.TemplateResponse(request, '_models.html', {'models': registered_models})


@app.get('/x/records/{model_name}')
async def render_records(request: Request, model_name: str, offset: int = 0, limit: int = 8):
    offset = max(offset, 0)
    limit = max(limit, 1)
    templating = await event.request('templating.get')
    model_meta = await event.request('describe_model', model_name=model_name)
    records = await event.request('model_records', model_name, offset, limit)
    total = await event.request('records.count', model_name)
    records_context = []
    for r in records:
        columns_data = []
        for c in model_meta['columns']:
            columns_data.append(getattr(r, c['name']))
        records_context.append(columns_data)
    
    context = {
        'model_name': model_name,
        'model_columns': list([(c['name'], idx) for idx, c in enumerate(model_meta['columns'])]),
        'records': records_context,
        'total': total,
        'offset': offset,
        'limit': limit,
        'showing': min(limit, total),
    }
    await asyncio.sleep(1)
    return templating.TemplateResponse(request, 'index/records/records.html', context)


# @app.get('/test')
# async def test(request: Request): 
#     form_html = await event.request('form_html', name='Form', method='post', action='/test')
#     return (await event.request('templating.get')).TemplateResponse(request, 'test.html', {'form_html': form_html})


# @app.post('/test')
# async def post_test(request: Request):  
#     return await request.form()


@app.get('/{model_name}')
async def index(request: Request, model_name):
    # model_admin = await event.request('storage.model', model_name=model)
    # model_meta = await event.request('describe_model', model_name=model_name)
    templating = await event.request('templating.get')

    context = {
        'model_name': model_name,
    }

    return templating.TemplateResponse(request, 'index.html', context)


@app.get('/{model_name}/new')
async def new(request: Request, model_name: str):
    templating = await event.request('templating.get')
    form_html = await event.request('form_html', name='Form', method='post', action='/test')

    context = {
        'model_name': model_name,
        'form_html': form_html,
    }

    return templating.TemplateResponse(request, 'new.html', context)


@app.post('/{model}')
async def create(request: Request, model):
    form_data = await request.form()
    await event.request('model_save', model=model, data=[form_data])
    return RedirectResponse('/', status_code=303)
