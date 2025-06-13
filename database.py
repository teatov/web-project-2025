import sqlalchemy
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

Base = dec.declarative_base()

__factory = None


def _lower(arg: str) -> str:
    return arg.lower()


def global_init(sqlite_path):
    global __factory

    if __factory:
        return

    if not sqlite_path:
        raise Exception("Отсутствует файл БД")

    url = f"sqlite:///{sqlite_path}?check_same_thread=False"
    print(f"Подключение к базе данных по адресу {url}")

    engine = sqlalchemy.create_engine(url, echo=True)

    @sqlalchemy.event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        dbapi_connection.create_function("lower", 1, _lower)

    __factory = sqlalchemy.orm.sessionmaker(bind=engine)

    import models

    Base.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
