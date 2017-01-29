import json
from datetime import datetime

import Config
from Views.Base import RequestHandler
from Views.Utils import get_user


class GetAllHandler(RequestHandler):
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


class UpdateQuestionHandler(RequestHandler):
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


class DeleteQuestionHandler(RequestHandler):
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


class AnswerHandler(RequestHandler):
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
