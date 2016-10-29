import tornado.web
import hashlib
import json
from uuid import uuid4
from Model import SMTPMail


DEBUG = True


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_engine = kwargs.pop('db_engine')

        super().__init__(*args, **kwargs)

    async def get_db(self):
        return await self.db_engine.acquire()


class IndexHandler(RequestHandler):
    async def get(self):
        db = await self.get_db()
        self.write("Ello World")


class PollHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        data = []
        async for row in db.execute(
            'SELECT * FROM "poll" WHERE "status"=1'
            'ORDER BY "year" DESC, "order"'
        ):
            element = {}
            for key in row:
                element[key] = row[key]
            data.append(element)
        self.write({'data': data})
        await db.close()


class PollDeleteHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
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


class PollAddHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            poll_id = int(self.get_argument('id'))
            order = self.get_argument('order')
            year = self.get_argument('year')
            subject = self.get_argument('subject')
            body = self.get_argument('body')
            if poll_id != -1:
                await db.execute(
                    'UPDATE "poll" SET "order"=%s, "year"=%s, "subject"=%s, "body"=%s '
                    'WHERE "id"=%s AND "status"=1',
                    (order, year, subject, body, poll_id)
                )
            else:
                await db.execute(
                    'INSERT INTO "poll" ("order", "year", "subject", "body", "status") '
                    'VALUES (%s, %s, %s, %s, 1)',
                    (order, year, subject, body)
                )
            self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class QaHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        data = []
        async for row in db.execute(
            'SELECT * FROM "qa" WHERE "status"=1'
            'ORDER BY "order"'
        ):
            element = {}
            for key in row:
                element[key] = row[key]
            data.append(element)
        self.write({'data': data})
        await db.close()


class QaDeleteHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            poll_id = self.get_argument('id')
            await db.execute(
                'UPDATE "qa" SET "status"=0 WHERE "id"=%s',
                (poll_id, )
            )
            self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class QaAddHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            qa_id = int(self.get_argument('id'))
            order = self.get_argument('order')
            question = self.get_argument('question')
            answer = self.get_argument('answer')
            if qa_id != -1:
                await db.execute(
                    'UPDATE "qa" SET "order"=%s, "question"=%s, "answer"=%s '
                    'WHERE "id"=%s AND "status"=1',
                    (order, question, answer, qa_id)
                )
            else:
                await db.execute(
                    'INSERT INTO "qa" ("order", "question", "answer", "status") '
                    'VALUES (%s, %s, %s, 1)',
                    (order, question, answer)
                )
            self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})

        
class ManageHandler(RequestHandler):
    async def post(self):
        example = json.dumps({'status': 'SUCCESS'})
        self.set_header('Content-Type', 'application/json')
        self.write(example)


class CheckLoginHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')
        if uid:
            self.write({'status': 'LOGINED'})
        else:
            self.write({'status': 'NOT LOGINED'})
        await db.close()


class LoginHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()
            uid = None
            async for row in db.execute(
                'SELECT "id", "password" FROM "user" WHERE "mail"=%s',
                (mail, )
            ):
                uid = row.id
                real_password = row.password
            if uid != None and password == real_password:
                self.set_secure_cookie('uid', str(uid))
                self.write({'status': 'SUCCESS'})
            else:
                self.write({'status': 'FAILED'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()

class RegisterHandler(RequestHandler):
    async def post(self):
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()
            await db.execute(
                'INSERT INTO "user" ("mail", "password", "power") VALUES (%s, %s, %s)',
                (mail, password, -1)
            )

            async for row in db.execute(
                'SELECT "id" FROM "user" WHERE "mail"=%s',
                (mail, )
            ):
                lastrowid = row.id

            token = uuid4()
            await db.execute(
                'INSERT INTO "authtoken" ("uid", "token") VALUES (%s, %s)',
                (lastrowid, token)
            )

            smtp = SMTPMail()
            smtp.send(mail, 'auth', token)
            self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})

