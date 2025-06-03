from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from event import event_bus


engine = create_engine('sqlite:///./database.sqlite')
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    try:
        session = Session()
        yield session
    finally:
        session.close()


async def _get_session(data):
    return next(get_session())


event_bus.respond_to('get_session', _get_session)
