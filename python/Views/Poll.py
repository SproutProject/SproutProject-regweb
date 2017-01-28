from Views.Base import RequestHandler
from Views.Utils import get_user


class GetAllHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()

        data = []
        async for row in db.execute(
            'SELECT * FROM "poll" WHERE "status"=1'
            ' ORDER BY "year" DESC, "order"'
        ):
            element = {}
            for key in row:
                element[key] = row[key]
            data.append(element)
        self.write({'status': 'SUCCESS', 'data': data})

        await db.close()


class DeleteHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power < 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                try:
                    poll_id = self.get_argument('id')
                    await db.execute(
                        'UPDATE "poll" SET "status"=0 WHERE "id"=%s',
                        (poll_id, )
                    )
                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class AddHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power < 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                try:
                    poll_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    year = self.get_argument('year')
                    subject = self.get_argument('subject')
                    body = self.get_argument('body')
                    if poll_id != -1:
                        await db.execute(
                            'UPDATE "poll" SET "order"=%s, "year"=%s, "subject"=%s, "body"=%s'
                            ' WHERE "id"=%s AND "status"=1',
                            (order, year, subject, body, poll_id)
                        )
                    else:
                        await db.execute(
                            'INSERT INTO "poll" ("order", "year", "subject", "body", "status")'
                            ' VALUES (%s, %s, %s, %s, 1)',
                            (order, year, subject, body)
                        )
                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()
