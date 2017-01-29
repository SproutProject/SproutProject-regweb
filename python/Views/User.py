import bcrypt

from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user_new


class LoginHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        try:
            mail = self.get_argument('mail')
            password = self.get_argument('password')
            uid = None

            res = session.query(User).filter(User.mail == mail)

            for row in res:
                uid = row.id
                hashed = eval(row.password)
                power = row.power

            if uid != None and bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed:
                if power >= 0:
                    self.set_secure_cookie('uid', str(uid))
                    self.return_status(self.STATUS_SUCCESS)
                else:
                    self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                self.return_status(self.STATUS_FAILED)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()


class LogoutHandler(RequestHandler):
    async def post(self):
        self.clear_cookie('uid')
        self.return_status(self.STATUS_SUCCESS)


class CheckLoginHandler(RequestHandler):
    async def post(self):
        uid = self.get_secure_cookie('uid')
        if uid:
            self.return_status(self.STATUS_LOGINED)
        else:
            self.return_status(self.STATUS_NOT_LOGINED)


class GetIndividualDataHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user_new(session, uid)
            data = {}

            res = session.query(UserData, GenderOption, SchoolTypeOption) \
                    .filter(UserData.gender == GenderOption.id) \
                    .filter(UserData.school_type == SchoolTypeOption.id) \
                    .filter(UserData.uid == uid)

            for row in res:
                data = row[0].as_dict()
                data['gender_value'] = row[1].value
                data['school_type_value'] = row[2].value

            data['rule_test'] = user.rule_test
            data['pre_test'] = user.pre_test
            data['signup_status'] = user.signup_status

            self.return_status(self.STATUS_SUCCESS, data=data)
        session.close()


class ModifyIndividualDataHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)

            try:
                address = self.get_argument('address')
                phone = self.get_argument('phone')
                user_data = None

                res = session.query(UserData).filter(UserData.uid == uid)
                for row in res:
                    row.address = address
                    row.phone = phone

                session.commit()
                self.return_status(self.STATUS_SUCCESS)
            except Exception as e:
                if DEBUG:
                    print(e)
                self.return_status(self.STATUS_ERROR)
        session.close()


class CheckAdminHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user_new(session, uid)
            if user.power < 1:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                self.return_status(self.STATUS_SUCCESS)
        session.close()


class SetPowerHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user_new(session, uid)

            if user.power < 2:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                try:
                    mail = self.get_argument('mail')
                    power = self.get_argument('power')

                    res = session.query(User).filter(User.mail == mail)

                    for row in res:
                        row.power = power

                    session.commit()
                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()


class GetAllUserDataHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user_new(session, uid)
            if user.power < 1:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                data = []

                res = session.query(User, UserData, GenderOption, SchoolTypeOption) \
                    .filter(User.id == UserData.uid) \
                    .filter(UserData.gender == GenderOption.id) \
                    .filter(UserData.school_type == SchoolTypeOption.id) \
                    .order_by(User.id)

                for row in res:
                    element = row[0].as_dict()
                    del element['password']

                    user_data = row[1].as_dict()
                    del user_data['id']
                    del user_data['uid']
                    element.update(user_data)

                    element['gender_value'] = row[2].value
                    element['school_type_value'] = row[3].value

                    data.append(element)

                self.return_status(self.STATUS_SUCCESS, data = data)
        session.close()
