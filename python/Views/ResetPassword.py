import bcrypt
from uuid import uuid4

import Config
from Model import SMTPMail
from Views.Base import RequestHandler
from Views.Utils import get_user


class GetMailHandler(RequestHandler):
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


class SetHandler(RequestHandler):
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
