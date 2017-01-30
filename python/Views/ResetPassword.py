import bcrypt
from uuid import uuid4
from sqlalchemy import and_

import Config
from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import db_insert


class GetMailHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        try:
            mail = self.get_argument('mail')
            uid = None
            for row in session.query(User).filter(User.mail == mail):
                uid = row.id

            if uid:
                session.query(SetPasswordToken).filter(SetPasswordToken.id == uid).delete()

                token = uuid4()
                instance = SetPasswordToken(uid = uid, token = token)
                db_insert(session, instance)

                url = 'http://%s/spt/set_password/?id=%s&token=%s' % (Config.HOST, uid, str(token))
                with open('mail_template/set_password.mail') as f:
                    plain_content = f.read() % url
                with open('mail_template/set_password.html') as f:
                    html_content = f.read() % (url, url)

                smtp = SMTPMail()
                smtp.send(mail, '[2017 資訊之芽] 重設密碼', plain_content, html_content)
                self.return_status(self.STATUS_SUCCESS)
            else:
                self.return_status(self.STATUS_FAILED)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()


class SetHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        try:
            uid = self.get_argument('id')
            token = self.get_argument('token')
            password = self.get_argument('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            res = session.query(SetPasswordToken) \
                .filter(and_(SetPasswordToken.uid == uid, SetPasswordToken.token == token))

            if res.count() > 0:
                for row in session.query(User).filter(User.id == uid):
                    row.password = str(hashed)
                session.commit()

                session.query(SetPasswordToken) \
                    .filter(and_(SetPasswordToken.uid == uid, SetPasswordToken.token == token)) \
                    .delete()
                session.commit()
                self.return_status(self.STATUS_SUCCESS)
            else:
                self.return_status(self.STATUS_FAILED)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()
