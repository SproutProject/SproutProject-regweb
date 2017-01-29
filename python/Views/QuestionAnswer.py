from sqlalchemy import and_

from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user_new, db_insert


class GetAllHandler(RequestHandler):
    async def post(self):
        session = self.get_session()

        data = []
        for row in session.query(Qa).filter(Qa.status == 1).order_by(Qa.order):
            data.append(row.as_dict())

        self.return_status(self.STATUS_SUCCESS, data=data)
        session.close()


class DeleteHandler(RequestHandler):
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
                try:
                    qa_id = self.get_argument('id')
                    for row in session.query(Qa).filter(Qa.id == qa_id):
                        row.status = 0
                    session.commit()
                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()


class AddHandler(RequestHandler):
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
                try:
                    qa_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    question = self.get_argument('question')
                    answer = self.get_argument('answer')

                    if qa_id != -1:
                        for row in session.query(Qa).filter(and_(Qa.id == qa_id, Qa.status == 1)):
                            row.order = order
                            row.question = question
                            row.answer = answer
                        session.commit()
                    else:
                        instance = Qa(order = order, question = question \
                            , answer = answer, status = 1)
                        db_insert(session, instance)

                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        await db.close()
