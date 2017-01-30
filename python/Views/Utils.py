from Model import *


def get_user(session, id):
    res = session.query(User).filter(User.id == id)
    for row in res:
        return row
    return None

def db_insert(session, instance):
    session.add(instance)
    session.commit()