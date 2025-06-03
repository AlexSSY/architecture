import asyncio
from collections import defaultdict


class EventBus:

    def __init__(self, strict=False):
        self._subscribers = defaultdict(list)
        self._responders = {}
        self._strict = strict

    def subscribe(self, event_name, handler):
        self._subscribers[event_name].append(handler)

    def respond_to(self, event_name, handler):
        if self._strict and event_name in self._responders:
            raise ValueError(f"Responder for event '{event_name}' already registered")
        self._responders[event_name] = handler

    async def publish(self, event_name, data):
        for handler in self._subscribers[event_name]:
            asyncio.create_task(handler(data))
    
    async def request(self, event_name, data):
        handler = self._responders.get(event_name)
        if not handler:
            raise ValueError(f"No responder registered for event '{event_name}'")
        return await handler(data)


event_bus = EventBus()
