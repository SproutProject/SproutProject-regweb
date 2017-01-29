import bcrypt
import re
from uuid import uuid4
from sqlalchemy import and_

import Config
from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import db_insert


class FirstHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        try:
            mail = self.get_argument('mail')
            password = self.get_argument('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # password = hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()

            # Check email format
            if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', mail):
                self.return_status(self.STATUS_WRONG)
            else:

                # Check if this mail be registered or not
                uid = None
                for row in session.query(User).filter(User.mail == mail):
                    uid = row.id

                if uid:
                    self.return_status(self.STATUS_FAILED)
                else:
                    instance = User(mail = mail, password = str(hashed), power = -1 \
                        , rule_test = 0, pre_test = 0, signup_status = 0)
                    db_insert(session, instance)

                    for row in session.query(User).filter(User.mail == mail):
                        lastrowid = row.id

                    token = uuid4()
                    instance = AuthToken(uid = lastrowid, token = token)
                    db_insert(session, instance)

                    instance = UserData(uid = lastrowid, gender = 1, school_type = 1)
                    db_insert(session, instance)

                    url = 'http://%s/spt/register/?id=%s&token=%s' % (Config.HOST, lastrowid, str(token))
                    with open('mail_template/register.mail') as f:
                        plain_content = f.read() % url
                    with open('mail_template/register.html') as f:
                        html_content = f.read() % (url, url)

                    smtp = SMTPMail()
                    smtp.send(mail, '[2017 資訊之芽] 註冊帳號確認信', plain_content, html_content)
                    self.return_status(self.STATUS_SUCCESS)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()


class SecondHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
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

            res = session.query(AuthToken).filter(and_(AuthToken.uid == uid, AuthToken.token == token))

            if res.count() > 0:
                for row in session.query(UserData).filter(UserData.uid == uid):
                    row.full_name = full_name
                    row.gender = gender
                    row.school = school
                    row.school_type = school_type
                    row.grade = grade
                    row.address = address
                    row.phone = phone
                session.commit()

                for row in session.query(User).filter(User.id == uid):
                    row.power = 0
                session.commit()

                session.query(AuthToken).filter(and_(AuthToken.uid == uid, AuthToken.token == token)).delete()
                session.commit()

                self.return_status(self.STATUS_SUCCESS)
            else:
                self.return_status(self.STATUS_FAILED)
        except Exception as e:
            if DEBUG:
                print(e)
        session.close()


class GetOptionsHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        data = {}
        try:
            data['gender'] = []
            for row in session.query(GenderOption):
                obj = {'id': row.id, 'value': row.value}
                data['gender'].append(obj)

            data['school_type'] = []
            for row in session.query(SchoolTypeOption):
                obj = {'id': row.id, 'value': row.value, 'max_grade': row.max_grade}
                data['school_type'].append(obj)

            self.return_status(self.STATUS_SUCCESS, data=data)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()
