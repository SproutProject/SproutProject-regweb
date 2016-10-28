import tornado.web
import json
from uuid import uuid4
from Model import SMTPMail

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


class PollViewerHandler(RequestHandler):
    async def post(self):
        db = await self.get_db()
        example = json.dumps({'data': [{'Id': 123, 'Subject': 'test1', 'Body': 'test2'}, {'Id': 456, 'Subject': 'test3', 'Body': 'test3'}]})
        self.set_header('Content-Type', 'application/json')
        self.write(example)
        await db.close()


class ManageHandler(RequestHandler):
    async def post(self):
        example = json.dumps({'status': 'SUCCES'})
        self.set_header('Content-Type', 'application/json')
        self.write(example)


class ManageQaHandler(RequestHandler):
    async def post(self): 
        example = json.dumps({'data': [{'Id': 123, 'Subject': 'test1', 'Order': 'test2'}, {'Id': 456, 'Subject': 'test3', 'Order': 'test3'}]})
        self.set_header('Content-Type', 'application/json')
        self.write(example)


class ManagePollHandler(RequestHandler):
    async def post(self): 
        example = json.dumps({'data': [{'Id': 123, 'Subject': 'test1', 'Order': 'test2'}, {'Id': 456, 'Subject': 'test3', 'Order': 'test3'}]})
        self.set_header('Content-Type', 'application/json')
        self.write(example)


class ManageRequestHandler(RequestHandler):
    async def post(self): 
        example = json.dumps({'data': [{'Id': 123, 'Subject': 'test1', 'Order': 'test2'}, {'Id': 456, 'Subject': 'test3', 'Order': 'test3'}]})
        self.set_header('Content-Type', 'application/json')
        self.write(example)


class RegisterHandler(RequestHandler):
    async def post(self):
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = self.get_argument('password')
        except Exception as e:
            self.write({'status': 'error'})
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
        self.write({'status': 'success'})

