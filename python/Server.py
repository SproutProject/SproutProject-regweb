import threading
import requests

import aiopg.sa
import asyncio
import tornado.platform.asyncio
import tornado.process
import tornado.web

import View
import Model
import Config

import Views.User
import Views.Register
import Views.ResetPassword
import Views.QuestionAnswer
import Views.Poll
import Views.RuleTest
import Views.Application

async def create_db_engine():
    return await aiopg.sa.create_engine(
            database=Config.DB_NAME,
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWD)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def update_google_sheet():
    r = requests.post('http://%s/spt/d/gs' % Config.HOST, params={'key': Config.SECRET_KEY})

def main():
    Model.init()

    tornado.platform.asyncio.AsyncIOMainLoop().install()
    db_engine = asyncio.get_event_loop().run_until_complete(create_db_engine())
    g_sheet = Model.GoogleSheet()

    # Daemon for updating google sheet
    set_interval(update_google_sheet, Config.GOOGLE_REFRESH_TIME)

    import sqlalchemy
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    new_db_engine = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgresql+psycopg2',
            database=Config.DB_NAME,
            host=Config.DB_HOST,
            username=Config.DB_USER,
            password=Config.DB_PASSWD
        )
    )

    SessionMaker = sessionmaker(bind=new_db_engine)
    from Model import User
    session = SessionMaker()

    app_param = {
        'db_engine': db_engine,
        'g_sheet': g_sheet,
        'session_maker': SessionMaker,
    }
    app = tornado.web.Application([
        (r'/user/check_login', Views.User.CheckLoginHandler, app_param),
        (r'/user/login', Views.User.LoginHandler, app_param),
        (r'/user/logout', Views.User.LogoutHandler, app_param),
        (r'/user/get_indiv_data', Views.User.GetIndividualDataHandler, app_param),
        (r'/user/modify_indiv_data', Views.User.ModifyIndividualDataHandler, app_param),
        (r'/user/check_admin', Views.User.CheckAdminHandler, app_param),
        (r'/user/set_power', Views.User.SetPowerHandler, app_param),
        (r'/user/get_all_user_data', Views.User.GetAllUserDataHandler, app_param),
        (r'/register/first', Views.Register.FirstHandler, app_param),
        (r'/register/second', Views.Register.SecondHandler, app_param),
        (r'/register/get_options', Views.Register.GetOptionsHandler, app_param),
        (r'/reset_password/get_mail', Views.ResetPassword.GetMailHandler, app_param),
        (r'/reset_password/set', Views.ResetPassword.SetHandler, app_param),
        (r'/qa/get_all', Views.QuestionAnswer.GetAllHandler, app_param),
        (r'/qa/add', Views.QuestionAnswer.AddHandler, app_param),
        (r'/qa/del', Views.QuestionAnswer.DeleteHandler, app_param),
        (r'/poll/get_all', Views.Poll.GetAllHandler, app_param),
        (r'/poll/add', Views.Poll.AddHandler, app_param),
        (r'/poll/del', Views.Poll.DeleteHandler, app_param),
        (r'/rule_test/get_question', Views.RuleTest.GetQuestionHandler, app_param),
        (r'/rule_test/answer', Views.RuleTest.AnswerHandler, app_param),
        (r'/rule_test/add_question', Views.RuleTest.AddQuestionHandler, app_param),
        (r'/rule_test/del_question', Views.RuleTest.DeleteQuestionHandler, app_param),
        (r'/application/get_all', Views.Application.GetAllHandler, app_param),
        (r'/application/answer', Views.Application.AnswerHandler, app_param),
        (r'/application/update_question', Views.Application.UpdateQuestionHandler, app_param),
        (r'/application/del_question', Views.Application.DeleteQuestionHandler, app_param),

        (r'/cms_token', View.GetCmsTokenHandler, app_param),
        (r'/entrance_token', View.GetEntranceTokenHandler, app_param),
        (r'/gs', View.UpdateGoogleSheetHandler, app_param),
    ], cookie_secret=Config.SECRET_KEY)
    app.listen(Config.LISTEN_PORT)

    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
