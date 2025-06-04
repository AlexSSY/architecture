from sqlalchemy.inspection import inspect
from sqlalchemy.sql.schema import UniqueConstraint, Index
import event


from sqlalchemy.inspection import inspect
from sqlalchemy.schema import UniqueConstraint

async def describe_model(model):
    mapper = inspect(model)
    table = model.__table__

    # Колонки
    columns = []
    for column in mapper.columns:
        columns.append({
            'name': column.key,
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'default': str(column.default.arg) if column.default is not None else None,
            'foreign_keys': [str(fk.column) for fk in column.foreign_keys],
            'unique': column.unique,
        })

    # Связи
    relationships = []
    for rel in mapper.relationships:
        data = {
            'name': rel.key,
            'target_model': rel.mapper.class_.__name__,
            'direction': rel.direction.name,
            'uselist': rel.uselist,
            'back_populates': rel.back_populates,
            'choices': [],
        }

        if rel.direction.name == 'MANYTOONE':
            # Подгружаем записи из связанной таблицы
            target_model = rel.mapper.class_
            try:
                session = await event.request('get_session')
                choices = session.query(target_model).all()
                data['choices'] = [
                    {'id': getattr(obj, 'id'), 'label': str(obj)} for obj in choices
                ]
            except Exception:
                pass  # На случай если таблица пустая или модель не настроена

        relationships.append(data)

    # Уникальные ограничения
    unique_constraints = [
        [col.name for col in constraint.columns]
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    # Индексы
    indexes = [
        {'name': index.name, 'columns': [col.name for col in index.columns], 'unique': index.unique}
        for index in table.indexes
    ]

    return {
        'table_name': table.name,
        'columns': columns,
        'relationships': relationships,
        'unique_constraints': unique_constraints,
        'indexes': indexes,
    }


@event.respond_to('describe_model')
async def worker(model_name):
    sa_model = await event.request('get_sa_model', model_name=model_name)
    if sa_model:
        return await describe_model(sa_model)
    return {}
