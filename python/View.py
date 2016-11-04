import re
import tornado.web
import hashlib
import json
from uuid import uuid4
from Model import SMTPMail
import Config


DEBUG = True

# Utils

async def get_user(db, id):
    async for row in db.execute(
        'SELECT * FROM "user" WHERE "id"=%s',
        (id, )
    ):
        return row
    return None


# RequestHandlers

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
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
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


class PollDeleteHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
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


class PollAddHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
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


class QaHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                data = []
                async for row in db.execute(
                    'SELECT * FROM "qa" WHERE "status"=1'
                    ' ORDER BY "order"'
                ):
                    element = {}
                    for key in row:
                        element[key] = row[key]
                    data.append(element)
                self.write({'status': 'SUCCESS', 'data': data})
        await db.close()


class QaDeleteHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
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
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                try:
                    qa_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    question = self.get_argument('question')
                    answer = self.get_argument('answer')
                    if qa_id != -1:
                        await db.execute(
                            'UPDATE "qa" SET "order"=%s, "question"=%s, "answer"=%s'
                            ' WHERE "id"=%s AND "status"=1',
                            (order, question, answer, qa_id)
                        )
                    else:
                        await db.execute(
                            'INSERT INTO "qa" ("order", "question", "answer", "status")'
                            ' VALUES (%s, %s, %s, 1)',
                            (order, question, answer)
                        )
                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()

        
class ManageHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power != 1:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                self.write({'status': 'SUCCESS'})
        await db.close()


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


class LogoutHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        self.clear_cookie('uid')
        self.write({'status': 'SUCCESS'})

class RegisterHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()

            # Check email format
            if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', mail):
                self.write({'status': 'WRONG MAIL'})
            else:

                # Check if this mail be registered or not
                uid = None
                async for row in db.execute(
                    'SELECT "id" FROM "user" WHERE "mail"=%s',
                    (mail, )
                ):
                    uid = row.id

                if uid:
                    self.write({'status': 'FAILED'})
                else:
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
                        'INSERT INTO "auth_token" ("uid", "token") VALUES (%s, %s)',
                        (lastrowid, token)
                    )

                    url = 'http://%s/spt/register/?id=%s&token=%s' % (Config.HOST, lastrowid, str(token))
                    with open('mail_template/register.mail') as f:
                        plain_content = f.read() % url
                    with open('mail_template/register.html') as f:
                        html_content = f.read() % (url, url)
                
                    smtp = SMTPMail()
                    smtp.send(mail, '[2017 資訊之芽] 註冊帳號確認信', plain_content, html_content)

                    self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class ForgetHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            uid = None
            async for row in db.execute(
                'SELECT "id" FROM "user" WHERE "mail"=%s',
                (mail, )
            ):
                uid = row.id

            if uid:
                await db.execute(
                    'DELETE FROM "set_password_token" WHERE "uid"=%s',
                    (uid, )
                )

                token = uuid4()
                await db.execute(
                    'INSERT INTO "set_password_token" ("uid", "token") VALUES (%s, %s)',
                    (uid, token)
                )

                url = 'http://%s/spt/set_password/?id=%s&token=%s' % (Config.HOST, uid, str(token))
                with open('mail_template/set_password.mail') as f:
                    plain_content = f.read() % url
                with open('mail_template/set_password.html') as f:
                    html_content = f.read() % (url, url)
                
                smtp = SMTPMail()
                smtp.send(mail, '[2017 資訊之芽] 重設密碼', plain_content, html_content)
                self.write({'status': 'SUCCESS'})
            else:
                self.write({'status': 'FAILED'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class SetPasswordHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            uid = self.get_argument('id')
            token = self.get_argument('token')
            password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()

            legal = False
            async for row in db.execute(
                'SELECT * FROM "set_password_token" WHERE "uid"=%s AND "token"=%s',
                (uid, token)
            ):
                legal = True

            if legal:
                await db.execute(
                    'UPDATE "user" SET "password"=%s WHERE "id"=%s',
                    (password, uid)
                )
                await db.execute(
                    'DELETE FROM "set_password_token" WHERE "uid"=%s AND "token"=%s',
                    (uid, token)
                )
                self.write({'status': 'SUCCESS'})
            else:
                self.write({'status': 'FAILED'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()


class RegisterOptionsHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        data = {}
        try:
            data['gender'] = []
            async for row in db.execute('SELECT * FROM "gender_option"'):
                obj = {'id': row.id, 'value': row.value}
                data['gender'].append(obj)

            data['school_type'] = []
            async for row in db.execute('SELECT * FROM "school_type_option"'):
                obj = {'id': row.id, 'value': row.value, 'max_grade': row.max_grade}
                data['school_type'].append(obj)
            self.write({'status': 'SUCCESS', 'data': data})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'}) 
        await db.close()


class RegisterDataHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            uid = int(self.get_argument('id'))
            token = self.get_argument('token')
            full_name = self.get_argument('full_name')
            gender = int(self.get_argument('gender'))
            school = self.get_argument('school')
            school_type = int(self.get_argument('school_type'))
            grade = int(self.get_argument('grade'))
            address = self.get_argument('address')
            phone = self.get_argument('phone')
            
            legal = False
            async for row in db.execute(
                'SELECT * FROM "auth_token" WHERE "uid"=%s AND "token"=%s',
                (uid, token)
            ):
                legal = True

            if legal:
                await db.execute(
                    'INSERT INTO "user_data"'
                    ' ("uid", "full_name", "gender", "school", "school_type", "grade", "address", "phone")'
                    ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (uid, full_name, gender, school, school_type, grade, address, phone)
                )
                await db.execute(
                    'UPDATE "user" SET "power"=0 WHERE "id"=%s',
                    (uid, )
                )
                await db.execute(
                    'DELETE FROM "auth_token" WHERE "uid"=%s AND "token"=%s',
                    (uid, token)
                )
                self.write({'status': 'SUCCESS'})
            else:
                self.write({'status': 'FAILED'})
        except Exception as e:
            if DEBUG:
                print(e)
        await db.close()


class IndividualDataHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')
        if uid:
            uid = int(uid)
            data = {}
            async for row in db.execute(
                'SELECT u.*, g."value" as "gender_value", s."value" as "school_type_value"'
                ' FROM "user_data" u'
                ' JOIN "gender_option" g ON u."gender"=g."id"'
                ' JOIN "school_type_option" s ON u."school_type"=s."id"'
                ' WHERE u."id"=%s',
                (uid, )
            ):
                for key in row:
                    data[key] = row[key]
            self.write({'status': 'SUCCESS', 'data': data})
        else:
            self.write({'status': 'NOT LOGINED'})
        await db.close()


class ModifyIndividualDataHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')
        if uid:
            uid = int(uid)
            try:
                address = self.get_argument('address')
                phone = self.get_argument('phone')
                await db.execute(
                    'UPDATE "user_data" SET "address"=%s, "phone"=%s WHERE "id"=%s',
                    (address, phone, uid)
                )
                self.write({'status': 'SUCCESS'})
            except Exception as e:
                if DEBUG:
                    print(e)
                self.write({'status': 'ERROR'})
        else:
            self.write({'status': 'NOT LOGINED'})
        await db.close()

