import asyncio
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from pprint import pprint
from models import Flower
from db import get_session
import event


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
            label_template='form/label.html',
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
        self.label_template = label_template

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
    class Meta:
        pass

    def fields(self):
       return list([f for f in self.__class__.__dict__.values() if issubclass(type(f), FormField)])


class FirstLastForm(Form):
    first_name = TextField('first_name', label='First Name', label_extra={'style': 'font-weight: bold;'})
    last_name = TextField('last_name', label='Last Name')

    class Meta:
        template = 'form/form.html'
        extra_html_attributes = {
            'class': 'm-auto w-50',
        }


_forms = {
    'Form': FirstLastForm,
}


@event.respond_to('form_html')
async def form_handler(name, method, action):
    form_class = _forms[name]

    form = form_class()

    # render form fields
    fields_html = []

    fields_context = form.fields()
    for form_field in fields_context:
        form_field_context = form_field.context()
        input_html = await event.request(
                'render_template',
                {'path': form_field.template, 'context': form_field_context['input']}
            )
        label_html = await event.request(
                'render_template',
                {'path': form_field.label_template, 'context': form_field_context['label']}
            )
        fields_html.append({
            'label': label_html,
            'input': input_html,
        })

    form_context = {
        'action': action,
        'method': method,
    }

    if hasattr(form.Meta, 'extra_html_attributes'):
        form_context['html_attributes'] = form.Meta.extra_html_attributes

    context = {
        'form': form_context,
        'fields_html': fields_html,
    }

    rendered_form = await event.request(
        'render_template',
        {'path': form.Meta.template, 'context': context}
    )

    return rendered_form
