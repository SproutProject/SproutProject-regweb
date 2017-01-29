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


class CheckAdminHandler(RequestHandler):
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
                self.write({'status': 'SUCCESS'})
        await db.close()


class SetPowerHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)

            if user.power < 2:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                try:
                    mail = self.get_argument('mail')
                    power = self.get_argument('power')
                    await db.execute(
                        'UPDATE "user" SET "power"=%s WHERE "mail"=%s',
                        (power, mail)
                    )
                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class GetAllUserDataHandler(RequestHandler):
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
                data = []
                async for row in db.execute(
                    'SELECT u."id", u."mail", u."power", u."rule_test", u."pre_test", u."signup_status",'
                    ' g."value" as "gender_value", s."value" as "school_type_value",'
                    ' d."full_name", d."gender", d."school", d."school_type", d."grade", d."phone", d."address"'
                    ' FROM "user" u'
                    ' JOIN "user_data" d ON u."id"=d."uid"'
                    ' JOIN "gender_option" g ON d."gender"=g."id"'
                    ' JOIN "school_type_option" s ON d."school_type"=s."id"'
                ):
                    element = {}
                    for key in row:
                        element[key] = row[key]
                    data.append(element)
                self.write({'status': 'SUCCESS', 'data': data})
        await db.close()
