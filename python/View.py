import tornado.web
import json

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
        example = json.dumps({'data': [{'Id': 123, 'Subject': 'test1', 'Body': 'test2'}, {'Id': 456, 'Subject': 'test3', 'Body': 'test3'}]})
        db = await self.get_db()
        self.set_header('Content-Type', 'application/json')
        self.write(example)
