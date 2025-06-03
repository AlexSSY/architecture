import asyncio
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from pprint import pprint
from models import Flower
from db import get_session
from event import event_bus


class FlowerSchema(SQLAlchemySchema):
    class Meta:
        model = Flower
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    name = auto_field()
    plant_id = auto_field()
    plant = auto_field()


class FlowerAdmin:
    fields = '__all__'
    readonly_fields = ['id']
    model = Flower


# flower_schema = FlowerSchema()
# session = next(get_session())
# pprint(flower_schema.validate({'name': 'Pink', 'plant_id': 1}, session=session))

# from model_metadata_worker import describe_model

# async def main():
#     pprint( await describe_model(Flower))

# asyncio.run(main())


{
    'name': '',
    'type': '',
    'value': '',
    'choices': [],
    'value': '',
    'errors': [],
}


class FormField:
    pass


class TextField(FormField):
    def __init__(
            self,
            name,
            input_extra={},
            label_extra={},
            value=None,
            errors=[],
            label=None,
            placeholder=None,
            required=False,
            template='form/text_input.html',
        ):
        self.name = name
        self.label = label if label else name
        self.placeholder = placeholder
        self.required = required
        self.value = value
        self.errors = errors
        self.input_extra = input_extra
        self.label_extra = label_extra
        self.template = template

    def input_html_attributes(self):
        html_attributes = {
            'id': self.name,
            'name': self.name,
            'type': 'text'
        }

        if self.placeholder:
            html_attributes['placeholder'] = self.placeholder

        if self.required:
            html_attributes['required'] = None

        html_attributes.update(self.input_extra)

        return html_attributes
    
    def label_html_attributes(self):
        html_attributes = {
            'for': self.name
        }

        html_attributes.update(self.label_extra)

        return html_attributes
    
    def input_context(self):
        context = {
            'html_attributes': self.input_html_attributes(),
            'value': self.value,
            'errors': self.errors,
        }

        return context

    def label_context(self):
        context = {
            'html_attributes': self.label_html_attributes(),
            'value': self.label
        }

        return context

    def context(self):
        return {
            'input': self.input_context(),
            'label': self.label_context(),
        }
    

class Form:
    first_name = TextField('first_name')
    last_name = TextField('last_name')

    def context(self):
        return {
            'action': 'post',
            'fields': list([f.context() for f in self.__class__.__dict__.values() if issubclass(type(f), FormField)]),
        }


# import main
from markupsafe import Markup
async def do():
    text_field = TextField(
        'name', 
        input_extra={'class': 'form-control'},
        label_extra={'class': 'form-label'}
    )
    text_field_context = text_field.context()
    pprint(text_field_context)
    print('')
    print('')
    print('')
    print('')
    rendered_text_field = await event_bus.request(
        'render_template',
        {'path': text_field.template, 'context': text_field_context}
    )
    return Markup(rendered_text_field)

pprint(Form().context())
# asyncio.run(do())
