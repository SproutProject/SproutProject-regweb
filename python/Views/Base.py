import tornado.web

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        # Get arguments
        self.db_engine = kwargs.pop('db_engine')
        self.g_sheet = kwargs.pop('g_sheet')
        self.session_maker = kwargs.pop('session_maker')

        super().__init__(*args, **kwargs)

        # Initialize header settings
        self.set_header('Content-Type', 'application/json')

    async def get_db(self):
        return await self.db_engine.acquire()

    def get_session(self):
        return self.session_maker()

    STATUS_SUCCESS = 'SUCCESS'
    STATUS_PERMISSION_DENIED = 'PERMISSION DENIED'
    STATUS_FAILED = 'FAILED'
    STATUS_ERROR = 'ERROR'
    STATUS_LOGINED = 'LOGINED'
    STATUS_NOT_LOGINED = 'NOT LOGINED'
    STATUS_WRONG = 'WRONG'
    STATUS_DEADLINE = 'DEADLINE'

    def return_status(self, status, data=None):
        if data:
            self.write({'status': status, 'data': data})
        else:
            self.write({'status': status})
        self.finish()