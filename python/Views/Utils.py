async def get_user(db, id):
    async for row in db.execute(
        'SELECT * FROM "user" WHERE "id"=%s',
        (id, )
    ):
        return row
    return None