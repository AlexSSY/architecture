import asyncio
from collections import defaultdict


_subscribers = defaultdict(list)
_responders = {}
_strict = True


def subscribe(event_name, handler):
    _subscribers[event_name].append(handler)



def register_responder(event_name, handler):
    if _strict and event_name in _responders:
        raise ValueError(f"Responder for event '{event_name}' already registered")
    _responders[event_name] = handler


def respond_to(event_name):
    def wrapper(fn):
        register_responder(event_name, fn)
        return fn
    return wrapper


def _wrap_handler(handler):
    async def wrapper(*args, **kwargs):
        try:
            await handler(*args, **kwargs)
        except Exception as e:
            print(f"[EventBus] Error in handler {handler}: {e}")
    return wrapper


async def publish(event_name, *args, **kwargs):
    for handler in _subscribers[event_name]:
        asyncio.create_task(_wrap_handler(handler)(*args, **kwargs))


async def request(event_name, *args, **kwargs):
    handler = _responders.get(event_name)
    if not handler:
        raise ValueError(f"No responder registered for event '{event_name}'")
    return await handler(*args, **kwargs)
