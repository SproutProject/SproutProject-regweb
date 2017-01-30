import json
from datetime import datetime
from sqlalchemy import and_

import Config
from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user, db_insert


class GetAllHandler(RequestHandler):
    def post(self):
        session = self.get_session()
        uid = self.get_secure_cookie('uid')
        if uid == None:
            self.return_status(self.STATUS_NOT_LOGINED)
        else:
            uid = int(uid)
            user = get_user(session, uid)

            try:
                class_type = int(self.get_argument('class_type'))
                data = []
                if user.signup_status & (1 << (class_type - 1)):
                    id_records = {}
                    res = session.query(ApplicationQuestion, ApplicationAnswer) \
                        .filter(and_(ApplicationQuestion.id == ApplicationAnswer.qid,
                                     ApplicationQuestion.class_type == class_type,
                                     ApplicationAnswer.uid == uid,
                                     ApplicationQuestion.status == 1)) \
                        .order_by(ApplicationQuestion.order)
                    for row in res:
                        element = row[0].as_dict()
                        element['answer'] = row[1].description
                        id_records[row[0].id] = True
                        data.append(element)

                    res = session.query(ApplicationQuestion) \
                        .filter(and_(ApplicationQuestion.class_type == class_type,
                                     ApplicationQuestion.status == 1)) \
                        .order_by(ApplicationQuestion.order)
                    for row in res:
                        if row.id not in id_records:
                            data.append(row.as_dict())
                else:
                    res = session.query(ApplicationQuestion) \
                        .filter(and_(ApplicationQuestion.class_type == class_type,
                                     ApplicationQuestion.status == 1)) \
                        .order_by(ApplicationQuestion.order)
                    for row in res:
                        data.append(row.as_dict())
                self.return_status(self.STATUS_SUCCESS, data=data)
            except Exception as e:
                if DEBUG:
                    print(e)
                self.return_status(self.STATUS_ERROR)
        session.close()


class UpdateQuestionHandler(RequestHandler):
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
                    app_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    class_type = self.get_argument('class_type')
                    description = self.get_argument('description')

                    if app_id == -1:
                        instance = ApplicationQuestion(order = order, class_type = class_type,
                                                       description = description, status = 1)
                        db_insert(session, instance)
                    else:
                        for row in session.query(ApplicationQuestion).filter(ApplicationQuestion.id == app_id):
                            row.order = order
                            row.class_type = class_type
                            row.description = description
                        session.commit()

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
                    app_id = int(self.get_argument('id'))

                    for row in session.query(ApplicationQuestion).filter(ApplicationQuestion.id == app_id):
                        row.status = 0
                    session.commit()

                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
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

            try:
                class_type = int(self.get_argument('class_type'))

                if datetime.now() > Config.DEADLINE:
                    self.return_status(self.STATUS_DEADLINE)
                    return

                if not user.rule_test:
                    self.return_status(self.STATUS_PERMISSION_DENIED)
                elif class_type == 3 and not user.pre_test:
                    self.return_status(self.STATUS_PERMISSION_DENIED)
                else:
                    data = json.loads(self.get_argument('data'))
                    for obj in data:
                        res = session.query(ApplicationQuestion) \
                            .filter(and_(ApplicationQuestion.id == obj['id'],
                                         ApplicationQuestion.class_type == class_type))
                        if res.count() > 0:
                            res = session.query(ApplicationAnswer) \
                                .filter(and_(ApplicationAnswer.uid == uid,
                                             ApplicationAnswer.qid == obj['id']))
                            if res.count() > 0:
                                for row in res:
                                    row.description = obj['answer']
                                session.commit()
                            else:
                                instance = ApplicationAnswer(uid = uid, qid = obj['id'], description = obj['answer'])
                                db_insert(session, instance)
                    if (user.signup_status & (1 << (class_type - 1))) == 0:
                        for row in session.query(User).filter(User.id == uid):
                            row.signup_status = user.signup_status | (1 << (class_type - 1))
                        session.commit()
                    self.return_status(self.STATUS_SUCCESS)
            except Exception as e:
                if DEBUG:
                    print(e)
                self.return_status(self.STATUS_ERROR)
        session.close()
