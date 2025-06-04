from fastapi.templating import Jinja2Templates

import event


_templating = None


@event.respond_to('templating.get')
async def get_templating():
    global _templating
    if _templating is None:
        raise ValueError('Template engine is not initialized')
    return _templating


@event.subscribe('loader.complete')
async def template_dirs_collected():
    template_dirs = await event.request('loader.template_dirs')
    global _templating
    _templating = Jinja2Templates(template_dirs)


@event.respond_to('templating.render')
async def render_template(template_path, context):
    template = _templating.get_template(template_path)
    return template.render(context)
