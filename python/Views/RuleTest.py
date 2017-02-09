import json
import random
import re
from sqlalchemy import and_

from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user, db_insert


class GetQuestionHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        response_is_answer = False
        uid = self.get_secure_cookie('uid')

        if uid:
            uid = int(uid)
            user = get_user(session, uid)
            if user.power >= 1:
                response_is_answer = True

        questions = {}
        res = session.query(RuleQuestion, RuleAnswer) \
            .filter(and_(RuleQuestion.id == RuleAnswer.qid, RuleQuestion.status == 1, RuleAnswer.status == 1))
        for row in res:
            q = row[0]
            a = row[1]
            questions[q.id] = questions.get(q.id, {'order': q.order, 'description': q.description, 'options': []})
            option = {'aid': a.id, 'answer': a.description}
            if response_is_answer:
                option['is_answer'] = a.is_answer
            questions[q.id]['options'].append(option)

        data = []
        for qid in questions:
            questions[qid]['id'] = qid
            if not response_is_answer:
                random.shuffle(questions[qid]['options'])
            data.append(questions[qid])
        data = sorted(data, key=lambda x : x['order'])

        self.return_status(self.STATUS_SUCCESS, data=data)
        session.close()


class AnswerHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user(session, uid)

            if user.power < 0:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                try:
                    data = json.loads(self.get_argument('data'))
                    correct = True
                    res = session.query(RuleQuestion, RuleAnswer).filter(
                        and_(RuleQuestion.id == RuleAnswer.qid,
                             RuleAnswer.is_answer == 1,
                             RuleQuestion.status == 1,
                             RuleAnswer.status == 1)
                        )
                    for row in res:
                        q = row[0]
                        a = row[1]
                        if str(q.id) not in data:
                            correct = False
                        elif data[str(q.id)] != str(a.id):
                            correct = False

                    if not correct:
                        self.return_status(self.STATUS_WRONG)
                    else:
                        for row in session.query(User).filter(User.id == uid):
                            row.rule_test = 1
                        session.commit()
                        self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()


class AddQuestionHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user(session, uid)
            if user.power < 1:
                self.return_status(self.STATUS_PERMISSION_DENIED)
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
                        instance = RuleQuestion(order = order, description = description, status = 1)
                        db_insert(session, instance)

                        # maybe race condition for get insert lastrowid
                        for row in session.query(RuleQuestion).order_by(RuleQuestion.id.desc()).limit(1):
                            qid = row.id
                    else:
                        # clear old optionss
                        for row in session.query(RuleAnswer).filter(RuleAnswer.qid == qid):
                            row.status = 0
                        session.commit()

                        for row in session.query(RuleQuestion).filter(RuleQuestion.id == qid):
                            row.order = order
                            row.description = description
                        session.commit()

                    for key in options:
                        option = options[key]
                        instance = RuleAnswer(qid = qid, description = option['answer'], status = 1,
                                              is_answer = 1 if ('is_answer' in option) else 0)
                        db_insert(session, instance)
                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()


class DeleteQuestionHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')

        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user(session, uid)
            if user.power < 1:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                try:
                    qid = self.get_argument('id')
                    for row in session.query(RuleQuestion).filter(RuleQuestion.id == qid):
                        row.status = 0
                    session.commit()
                    for row in session.query(RuleAnswer).filter(RuleAnswer.qid == qid):
                        row.status = 0
                    session.commit()
                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()
