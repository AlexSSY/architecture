import asyncio
import event


db1 = [
    {'id': 1, 'username': 'Bob', 'meta': 'Sqlalchemy'}
]


db2 = [
    {'id': 1, 'username': 'Bob', 'meta': 'Tortoise'}
]


db3 = [
    {'id': 1, 'username': 'Bob', 'meta': 'Pewee'}
]


# @event.respond_to('db.retrieve')
async def sqlalchemy_db_retrieve(table: str, by: str, value):
    return list([record for record in db1 if record[by] == value])


@event.respond_to('db.retrieve')
async def tortoise_db_retrieve(table: str, by: str, value):
    return list([record for record in db2 if record[by] == value])


# @event.respond_to('db.retrieve')
async def pewee_db_retrieve(table: str, by: str, value):
    return list([record for record in db3 if record[by] == value])


class UserRepository:
    @staticmethod
    async def get_user_by_id(id: int) -> dict:
        return await event.request('db.retrieve', 'users', 'id', id)
    
    async def get_record_by(column_name: str, value):
        ...

    async def get_user_by(**key_val):
        ...


async def main():
    print(await UserRepository.get_user_by_id(1))


if __name__ == '__main__':
    asyncio.run(main())
