from importlib import import_module
import event
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loader import Loader


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
async def index(request: Request):
    models = ['Flower', 'Plant']
    return (await event.request('templating.get')).TemplateResponse(request, 'index.html', {'models': models})


@app.get('/partials/{template_name}')
async def render_template(request: Request):
    templating = await event.request('templating.get')
    return templating.Render


@app.get('/test')
async def test(request: Request):
    form_html = await event.request('form_html', name='Form', method='post', action='/test')
    return (await event.request('templating.get')).TemplateResponse(request, 'test.html', {'form_html': form_html})


@app.post('/test')
async def post_test(request: Request):  
    return await request.form()


@app.get('/Flower')
async def flower(request: Request):
    templating = await event.request('templating.get')
    return templating.TemplateResponse(request, 'flower.html', {})


@app.get('/{model}')
async def model(request: Request, model):
    model_meta = await event.request('describe_model', model_name=model)
    return (await event.request('templating.get')).TemplateResponse(request, '_form.html', {'model': model_meta})


@app.post('/{model}')
async def create(request: Request, model):
    form_data = await request.form()
    await event.request('model_save', model=model, data=[form_data])
    return RedirectResponse('/', status_code=303)
