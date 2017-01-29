from sqlalchemy import and_

from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user_new, db_insert


class GetAllHandler(RequestHandler):
    async def post(self):
        session = self.get_session()

        data = []
        res = session.query(Poll).filter(Poll.status == 1) \
            .order_by(Poll.year.desc(), Poll.order)
        for row in res:
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
                    poll_id = self.get_argument('id')
                    for row in session.query(Poll).filter(Poll.id == poll_id):
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
                    poll_id = int(self.get_argument('id'))
                    order = self.get_argument('order')
                    year = self.get_argument('year')
                    subject = self.get_argument('subject')
                    body = self.get_argument('body')

                    if poll_id != -1:
                        for row in session.query(Poll).filter(and_(Poll.id == poll_id, Poll.status == 1)):
                            row.order = order
                            row.year = year
                            row.subject = subject
                            row.body = body
                        session.commit()
                    else:
                        instance = Poll(order = order, year = year, subject = subject \
                            , body = body, status = 1)
                        db_insert(session, instance)

                    self.return_status(self.STATUS_SUCCESS)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    self.return_status(self.STATUS_ERROR)
        session.close()
