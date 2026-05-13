from sqlalchemy.engine import Engine


def get_connection(engine: Engine):
    return engine.connect()
