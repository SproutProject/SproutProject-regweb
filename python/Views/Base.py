import tornado.web

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_engine = kwargs.pop('db_engine')
        self.g_sheet = kwargs.pop('g_sheet')
        self.session_maker = kwargs.pop('session_maker')

        super().__init__(*args, **kwargs)

    async def get_db(self):
        return await self.db_engine.acquire()

    def get_session(self):
        return self.session_maker()