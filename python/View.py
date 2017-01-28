import bcrypt
import codecs
import re
import tornado.web
import hashlib
import json
import random
import requests
import time
from uuid import uuid4
from Model import SMTPMail
import Config
from datetime import datetime


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
        self.g_sheet = kwargs.pop('g_sheet')
        self.session_maker = kwargs.pop('session_maker')

        super().__init__(*args, **kwargs)

    async def get_db(self):
        return await self.db_engine.acquire()

    def get_session(self):
        return self.session_maker()


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


class QaHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()

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
            if user.power < 1:
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
            if user.power < 1:
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
            if user.power < 1:
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

class RegisterHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            mail = self.get_argument('mail')
            password = self.get_argument('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()

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
                        'INSERT INTO "user" ("mail", "password", "power", "rule_test", "pre_test", "signup_status")'
                        ' VALUES (%s, %s, %s, 0, 0, 0)',
                        (mail, str(hashed), -1)
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

                    # Insert empty userdata
                    await db.execute(
                        'INSERT INTO "user_data" ("uid", "gender", "school_type") VALUES (%s, 1, 1)',
                        (lastrowid, )
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
            # password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()
            password = self.get_argument('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            legal = False
            async for row in db.execute(
                'SELECT * FROM "set_password_token" WHERE "uid"=%s AND "token"=%s',
                (uid, token)
            ):
                legal = True

            if legal:
                await db.execute(
                    'UPDATE "user" SET "password"=%s WHERE "id"=%s',
                    (str(hashed), uid)
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
                    'UPDATE "user_data" SET "full_name"=%s, "gender"=%s, "school"=%s,'
                    ' "school_type"=%s, "grade"=%s, "address"=%s, "phone"=%s'
                    ' WHERE "uid"=%s',
                    (full_name, gender, school, school_type, grade, address, phone, uid)
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


class RuleQuestionHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        response_is_answer = False
        uid = self.get_secure_cookie('uid')

        if uid:
            uid = int(uid)
            user = await get_user(db, uid)
            if user.power >= 1:
                response_is_answer = True

        questions = {}
        async for row in db.execute(
            'SELECT q.*, a."id" as "aid", a."description" AS "answer", a."is_answer"'
            ' FROM "rule_question" q'
            ' JOIN "rule_answer" a'
            ' ON q."id"=a."qid"'
            ' WHERE q."status"=1 AND a."status"=1'
        ):
            questions[row.id] = questions.get(row.id, {'order': row.order, 'description': row.description, 'options': []})
            option = {'aid': row.aid, 'answer': row.answer}
            if response_is_answer:
                option['is_answer'] = row.is_answer
            questions[row.id]['options'].append(option)

        data = []
        for qid in questions:
            questions[qid]['id'] = qid
            if not response_is_answer:
                random.shuffle(questions[qid]['options'])
            data.append(questions[qid])
        data = sorted(data, key=lambda x : x['order'])

        self.write({'status': 'SUCCESS', 'data': data})
        await db.close()


class RuleTestHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        response_is_answer = False
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)

            if user.power < 0:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                try:
                    data = json.loads(self.get_argument('data'))
                    correct = True
                    async for row in db.execute(
                        'SELECT q."id", a."id" as "aid"'
                        ' FROM "rule_question" q'
                        ' JOIN "rule_answer" a'
                        ' ON q."id"=a."qid"'
                        ' WHERE a."is_answer"=1 AND q."status"=1 AND a."status"=1'
                    ):
                        if str(row.id) not in data:
                            correct = False
                        elif data[str(row.id)] != str(row.aid):
                            correct = False

                    if not correct:
                        self.write({'status': 'WRONG'})
                    else:
                        await db.execute(
                            'UPDATE "user" SET "rule_test"=1 WHERE "id"=%s',
                            (uid, )
                        )
                        self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class RuleQuestionAddHandler(RequestHandler):
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
                    qid = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    description = self.get_argument('description')
                    options = {}
                    for arg in self.request.arguments:
                        obj = re.match(r'options\[(\d+?)\]\[(.+?)\]', arg)
                        if obj:
                            idx = obj.groups()[0]
                            val = obj.groups()[1]
                            options[idx] = options.get(idx, {})
                            options[idx][val] = self.get_argument(arg)

                    if qid == -1:
                        await db.execute(
                            'INSERT INTO "rule_question"'
                            ' ("order", "description", "status")'
                            ' VALUES (%s, %s, 1)',
                            (order, description)
                        )

                        # maybe race condition for get insert lastrowid
                        async for row in db.execute(
                            'SELECT "id" FROM "rule_question" ORDER BY "id" DESC LIMIT 1'
                        ):
                            qid = row.id
                    else:
                        # clear old optionss
                        await db.execute(
                            'UPDATE "rule_answer" SET "status"=0 WHERE "qid"=%s',
                            (qid, )
                        )

                        await db.execute(
                            'UPDATE "rule_question"'
                            ' SET "order"=%s, "description"=%s'
                            ' WHERE "id"=%s',
                            (order, description, qid)
                        )

                    for key in options:
                        option = options[key]
                        await db.execute(
                            'INSERT INTO "rule_answer"'
                            ' ("qid", "description", "is_answer", status)'
                            ' VALUES (%s, %s, %s, 1)',
                            (qid, option['answer'], 1 if ('is_answer' in option) else 0)
                        )
                    self.write({'status': "SUCCESS"})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class RuleQuestionDeleteHandler(RequestHandler):
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
                    qid = self.get_argument('id')
                    await db.execute(
                        'UPDATE "rule_question" SET "status"=0 WHERE "id"=%s',
                        (qid, )
                    )
                    await db.execute(
                        'UPDATE "rule_answer" SET "status"=0 WHERE "qid"=%s',
                        (qid, )
                    )
                    self.write({'status': "SUCCESS"})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class UserDataHandler(RequestHandler):
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


class ApplicationHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')
        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)

            try:
                class_type = int(self.get_argument('class_type'))
                data = []
                if user.signup_status & (1 << (class_type - 1)):
                    id_records = {}
                    async for row in db.execute(
                        'SELECT q."id", q."order", q."description", a."description" as "answer" FROM "application_question" q'
                        ' JOIN "application_answer" a'
                        ' ON q."id"=a."qid"'
                        ' WHERE q."class_type"=%s AND a."uid"=%s AND q."status"=1'
                        ' ORDER BY q."order"',
                        (class_type, uid)
                    ):
                        element = {}
                        for key in row:
                            element[key] = row[key]
                        data.append(element)
                        id_records[row.id] = True

                    async for row in db.execute(
                        'SELECT * FROM "application_question"'
                        ' WHERE "class_type"=%s AND "status"=1'
                        ' ORDER BY "order"',
                        (class_type, )
                    ):
                        if row.id not in id_records:
                            element = {}
                            for key in row:
                                element[key] = row[key]
                            data.append(element)

                else:
                    async for row in db.execute(
                        'SELECT * FROM "application_question"'
                        ' WHERE "class_type"=%s AND "status"=1'
                        ' ORDER BY "order"',
                        (class_type, )
                    ):
                        element = {}
                        for key in row:
                            element[key] = row[key]
                        data.append(element)
                self.write({'status': 'SUCCESS', 'data': data})
            except Exception as e:
                if DEBUG:
                    print(e)
                self.write({'status': 'ERROR'})
        await db.close()


class ApplicationAddHandler(RequestHandler):
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
                    app_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    class_type = self.get_argument('class_type')
                    description = self.get_argument('description')

                    if app_id == -1:
                        await db.execute(
                            'INSERT INTO "application_question"'
                            ' ("order", "class_type", "description", "status")'
                            ' VALUES (%s, %s, %s, 1)',
                            (order, class_type, description)
                        )
                    else:
                        await db.execute(
                            'UPDATE "application_question"'
                            ' SET "order"=%s, "class_type"=%s, "description"=%s'
                            ' WHERE "id"=%s',
                            (order, class_type, description, app_id)
                        )

                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class ApplicationDeleteHandler(RequestHandler):
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
                    app_id = int(self.get_argument('id'))

                    await db.execute(
                        'UPDATE "application_question" SET "status"=0 WHERE "id"=%s',
                        (app_id, )
                    )

                    self.write({'status': 'SUCCESS'})
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.write({'status': 'ERROR'})
        await db.close()


class ApplicationAnswerHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.write({'status': 'NOT LOGINED'})
        else:
            uid = int(uid)
            user = await get_user(db, uid)

            try:
                class_type = int(self.get_argument('class_type'))


                if datetime.now() > Config.DEADLINE:
                    self.write({'status': 'DEADLINE'})
                    return

                if not user.rule_test:
                    self.write({'status': 'PERMISSION DENIED'})
                elif class_type == 3 and not user.pre_test:
                    self.write({'status': 'PERMISSION DENIED'})
                else:                
                    data = json.loads(self.get_argument('data'))
                    for obj in data:
                        legal = False
                        async for row in db.execute(
                            'SELECT * FROM "application_question"'
                            ' WHERE "class_type"=%s AND "id"=%s',
                            (class_type, obj['id'])
                        ):
                            legal = True
                        if legal:
                            exist = False
                            async for row in db.execute(
                                'SELECT * FROM "application_answer"'
                                ' WHERE "uid"=%s AND "qid"=%s',
                                (uid, obj['id'])
                            ):
                                exist = True
                            if exist:
                                await db.execute(
                                    'UPDATE "application_answer"'
                                    ' SET "description"=%s'
                                    ' WHERE "uid"=%s AND "qid"=%s',
                                    (obj['answer'], uid, obj['id'])
                                )
                            else:
                                await db.execute(
                                    'INSERT INTO "application_answer" ("uid", "qid", "description")'
                                    ' VALUES (%s, %s, %s)',
                                    (uid, obj['id'], obj['answer'])
                                )
                    if (user.signup_status & (1 << (class_type - 1))) == 0:
                        await db.execute(
                            'UPDATE "user" SET "signup_status"=%s WHERE "id"=%s',
                            (user.signup_status | (1 << (class_type - 1)), uid)
                        )
                    self.write({'status': 'SUCCESS'})
            except Exception as e:
                if DEBUG:
                    print(e)
                self.write({'status': 'ERROR'})
        await db.close()


class UpdateGoogleSheetHandler(RequestHandler):
    async def post(self):
        db = await self.get_db()
        try:
            key = self.get_argument('key')
            if key != Config.SECRET_KEY:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                sheet_names = ['Sheet1', 'C', 'Python', 'Algorithm', 'Count']

                # Update userdata
                value_order = ['id', 'mail', 'full_name', 'gender_value', 'school',
                    'school_type_value', 'grade', 'address', 'phone',
                    'power', 'rule_test', 'pre_test', 'signup_status']

                values = []
                async for row in db.execute(
                    'SELECT u."id", u."mail", u."power", u."rule_test", u."pre_test", u."signup_status",'
                    ' g."value" as "gender_value", s."value" as "school_type_value",'
                    ' d."full_name", d."gender", d."school", d."school_type", d."grade", d."phone", d."address"'
                    ' FROM "user" u'
                    ' JOIN "user_data" d ON u."id"=d."uid"'
                    ' JOIN "gender_option" g ON d."gender"=g."id"'
                    ' JOIN "school_type_option" s ON d."school_type"=s."id"'
                    ' ORDER BY u."id"'
                ):
                    value = []
                    for key in value_order:
                        if key == 'rule_test' or key == 'pre_test':
                            value.append('v' if row[key] else '')
                        elif key == 'power':
                            power_list = ['一般', '管理者', '神']
                            if row[key] == -1:
                                value.append('未完成註冊')
                            else:
                                value.append(power_list[row[key]])
                        elif key == 'signup_status':
                            for i in range(3):
                                value.append('v' if row[key] & (1 << i) else '')
                        else:
                            value.append("'" + str(row[key]))
                    values.append(value)

                self.g_sheet.update(values, sheet_names[0] + '!A2:O')

                # For counting
                count_values = [[0, 0], [0, 0], [0, 0], [0, 0]]

                # Update Application
                for class_type in range(1, 4):
                    values = []

                    question_list = []
                    value = ['id', '姓名', '性別', '學校', '年級']
                    async for row in db.execute(
                        'SELECT * FROM "application_question" WHERE "class_type"=%s AND "status"=1 ORDER BY "order"',
                        (class_type)
                    ):
                        question_list.append(row)
                        value.append(row.description)
                    values.append(value)

                    async for user in db.execute(
                        'SELECT u."id", d."full_name", d."school", d."grade", d."gender" FROM "user" u'
                        ' JOIN "user_data" d'
                        ' ON u."id"=d."uid"'
                        ' WHERE (u."signup_status" & %s) > 0'
                        ' ORDER BY u."id"',
                        (1 << (class_type - 1), )
                    ):
                        answer = {}
                        async for row in db.execute(
                            'SELECT * FROM "application_answer" WHERE "uid"=%s',
                            (user.id, )
                        ):
                            answer[row.qid] = row.description

                        value = []
                        value.append(user.id)
                        value.append(user.full_name)
                        value.append('女' if user.gender == 1 else '男')
                        value.append(user.school)
                        value.append(user.grade)

                        if user.id > 28:
                            if class_type > 1:
                                count_values[class_type][0] += 1
                                if user.gender == 1:
                                    count_values[class_type][1] += 1

                        for question in question_list:
                            if question.id in answer:
                                value.append(answer[question.id])
                            else:
                                value.append('')

                            if user.id > 28 and question.id == 42 and question.id in answer:
                                if answer[question.id].find('竹') >= 0:
                                    count_values[0][0] += 1
                                    if user.gender == 1:
                                        count_values[0][1] += 1
                                if answer[question.id].find('北') >= 0:
                                    count_values[1][0] += 1
                                    if user.gender == 1:
                                        count_values[1][1] += 1

                        values.append(value)
                    self.g_sheet.update(values, sheet_names[class_type] + '!A1:Z')

                self.g_sheet.update(count_values, sheet_names[4] + '!B2:C')

                self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
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


class GetCmsTokenHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            uid = self.get_secure_cookie('uid')
            if uid is None:
                self.write({'status': 'NOT LOGINED'})
                return
                
            uid = int(uid)
            user = await get_user(db, uid)

            if user.rule_test == 0:
                self.write({'status': 'FAILED'})
                return
            
            h = hashlib.new('sha512')
            h.update((Config.PRETEST_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            hh = hashlib.new('ripemd160')
            hh.update((Config.PRETEST_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            url = 'http://%s/user_score' % Config.PRETEST_HOST
            res = requests.get(url, params={'username': user.mail, 'password': hh.hexdigest()}, timeout=0.5)
            # print(res.url)
            try:
                score = float(res.text.split('\n')[0].replace('*', ''))
            except Exception as e:
                if DEBUG:
                    print(e)
                    print(res.text)
                # self.write({'status': 'ERROR'})
                # return
                score = -1
            # print(res.text)

            if score >= Config.PRETEST_THRESHOLD:
                await db.execute(
                    'UPDATE "user" SET "pre_test"=1 WHERE "id"=%s',
                    (uid, )
                )
            else:
                await db.execute(
                    'UPDATE "user" SET "pre_test"=0 WHERE "id"=%s',
                    (uid, )
                )

            async for row in db.execute(
                'SELECT "full_name" FROM "user_data" WHERE "uid"=%s',
                (uid, )
            ):
                realname = row.full_name
                
            redirect_url = 'http://%s/redirect_login' % Config.PRETEST_HOST

            self.write({
                'status': 'SUCCESS',
                'username': user.mail,
                'password': h.hexdigest(),
                'realname': realname,
                'url': redirect_url,
                'score': score,
            })
        finally:
            await db.close()

class GetEntranceTokenHandler(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'application/json')
        db = await self.get_db()
        try:
            uid = self.get_secure_cookie('uid')
            if uid is None:
                self.write({'status': 'NOT LOGINED'})
                return
                
            uid = int(uid)
            user = await get_user(db, uid)

            if (user.signup_status & 4) == 0:
                self.write({'status': 'FAILED'})
                return

            print(user.mail)
            print(self.request.headers.get('Remote-Addr'))
            
            h = hashlib.new('sha512')
            h.update((Config.ENTRANCE_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            async for row in db.execute(
                'SELECT "full_name" FROM "user_data" WHERE "uid"=%s',
                (uid, )
            ):
                realname = row.full_name
                
            redirect_url = 'http://%s/redirect_login' % Config.ENTRANCE_HOST

            self.write({
                'status': 'SUCCESS',
                'username': user.mail,
                'password': h.hexdigest(),
                'realname': realname,
                'url': redirect_url,
            })
        finally:
            await db.close()
