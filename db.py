from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import event


engine = create_engine('sqlite:///./database.sqlite')
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    try:
        session = Session()
        yield session
    finally:
        session.close()


@event.respond_to('get_session')
async def _get_session():
    return next(get_session())
