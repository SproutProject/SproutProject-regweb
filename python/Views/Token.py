import hashlib
import requests
import time

import Config
from Views.Base import RequestHandler
from Views.Utils import get_user

class PretestHandler(RequestHandler):
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
                # if DEBUG:
                if True:
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

class EntranceHandler(RequestHandler):
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
