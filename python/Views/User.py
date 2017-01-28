import bcrypt

from Views.Base import RequestHandler
from Views.Utils import get_user


class LoginHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = self.get_argument('password')
            uid = None
            async for row in db.execute(
                'SELECT "id", "password", "power" FROM "user" WHERE "mail"=%s',
                (mail, )
            ):
                uid = row.id
                hashed = eval(row.password)
                power = row.power
            if uid != None and bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed:
                if power >= 0:
                    self.set_secure_cookie('uid', str(uid))
                    self.write({'status': 'SUCCESS'})
                else:
                    self.write({'status': 'PERMISSION DENIED'})
            else:
                self.write({'status': 'FAILED'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class LogoutHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        self.clear_cookie('uid')
        self.write({'status': 'SUCCESS'})


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
