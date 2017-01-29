from Model import *

async def get_user(db, id):
    async for row in db.execute(
        'SELECT * FROM "user" WHERE "id"=%s',
        (id, )
    ):
        return row
    return None


def get_user_new(session, id):
    res = session.query(User).filter(User.id == id)
    for row in res:
        return row
    return None
