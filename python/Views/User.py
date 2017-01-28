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


class GetIndividualDataHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            data = {}
            async for row in db.execute(
                'SELECT u.*, g."value" as "gender_value", s."value" as "school_type_value"'
                ' FROM "user_data" u'
                ' JOIN "gender_option" g ON u."gender"=g."id"'
                ' JOIN "school_type_option" s ON u."school_type"=s."id"'
                ' WHERE u."uid"=%s',
                (uid, )
            ):
                for key in row:
                    data[key] = row[key]

            data['rule_test'] = user.rule_test
            data['pre_test'] = user.pre_test
            data['signup_status'] = user.signup_status

            self.write({'status': 'SUCCESS', 'data': data})
        await db.close()


class ModifyIndividualDataHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            try:
                address = self.get_argument('address')
                phone = self.get_argument('phone')
                await db.execute(
                    'UPDATE "user_data" SET "address"=%s, "phone"=%s WHERE "uid"=%s',
                    (address, phone, uid)
                )
                self.write({'status': 'SUCCESS'})
            except Exception as e:
                if DEBUG:
                    print(e)
                self.write({'status': 'ERROR'})
        await db.close()
