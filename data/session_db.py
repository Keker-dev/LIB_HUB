from .db_session import global_init, create_session

global_init("db/main.db")
db_sess = create_session()
