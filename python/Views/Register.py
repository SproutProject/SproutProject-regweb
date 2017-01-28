import bcrypt
import re
from uuid import uuid4

import Config
from Model import SMTPMail
from Views.Base import RequestHandler
from Views.Utils import get_user


class FirstHandler(RequestHandler):
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


class SecondHandler(RequestHandler):
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


class GetOptionsHandler(RequestHandler):
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
