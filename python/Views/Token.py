import hashlib
import requests
import time

import Config
from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user


class PretestScoreHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        try:
            uid = self.get_secure_cookie('uid')
            if uid is None:
                self.return_status(self.STATUS_NOT_LOGINED)
                return

            uid = int(uid)
            user = get_user(session, uid)

            if user.rule_test == 0:
                self.return_status(self.STATUS_FAILED)
                return

            h = hashlib.new('ripemd160')
            h.update((Config.PRETEST_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            url = 'http://%s/user_score' % Config.PRETEST_HOST
            res = requests.get(url, params={'username': user.mail, 'password': h.hexdigest()}, timeout=0.5)

            try:
                score = float(res.text.split('\n')[0].replace('*', ''))
            except Exception as e:
                if DEBUG:
                    print(e)
                    print(res.text)
                score = -1
            
            for row in session.query(User).filter(User.id == uid):
                row.pre_test = 1 if score >= Config.PRETEST_THRESHOLD else 0
            session.commit()

            self.write({
                'status': 'SUCCESS',
                'score': score,
            })
        finally:
            session.close()


class PretestHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        try:
            uid = self.get_secure_cookie('uid')
            if uid is None:
                self.return_status(self.STATUS_NOT_LOGINED)
                return

            uid = int(uid)
            user = get_user(session, uid)

            if user.rule_test == 0:
                self.return_status(self.STATUS_FAILED)
                return

            h = hashlib.new('sha512')
            h.update((Config.PRETEST_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            for row in session.query(UserData).filter(UserData.uid == uid):
                realname = row.full_name

            redirect_url = 'http://%s/redirect_login' % Config.PRETEST_HOST

            self.write({
                'status': 'SUCCESS',
                'username': user.mail,
                'password': h.hexdigest(),
                'realname': realname,
                'url': redirect_url,
            })
        finally:
            session.close()


class EntranceHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        try:
            uid = self.get_secure_cookie('uid')
            if uid is None:
                self.return_status(self.STATUS_NOT_LOGINED)
                return

            uid = int(uid)
            user = get_user(session, uid)

            if (user.signup_status & 4) == 0:
                self.return_status(self.STATUS_FAILED)
                return

            h = hashlib.new('sha512')
            h.update((Config.ENTRANCE_SSO_LOGIN_PASSWORD + '||' + user.mail + '||' + str(int(time.time()))).encode('utf-8'))

            for row in session.query(UserData).filter(UserData.uid == uid):
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
            session.close()
