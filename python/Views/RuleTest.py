import json
import re

from Views.Base import RequestHandler
from Views.Utils import get_user


class GetQuestionHandler(RequestHandler):
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


class AnswerHandler(RequestHandler):
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



class AddQuestionHandler(RequestHandler):
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
