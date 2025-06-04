from importlib import import_module
import event


class Loader:
    _template_dirs = ['templates']

    @staticmethod
    async def load(config):
        for worker in config.get('services', []):
            try:
                import_module(worker)
                print(f'\t{worker} loaded')
            except Exception as e:
                _msg = f'\t{worker} error! {e}'
                print(_msg)
        
        await event.publish('loader.complete')
        
    @staticmethod
    async def get_template_dirs():
        return Loader._template_dirs


event.register_responder('loader.template_dirs', Loader.get_template_dirs)
