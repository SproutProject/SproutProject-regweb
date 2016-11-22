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
    r = requests.post('http://localhost/spt/d/gs', params={'key': Config.SECRET_KEY})


def main():
    Model.init()

    tornado.platform.asyncio.AsyncIOMainLoop().install()
    db_engine = asyncio.get_event_loop().run_until_complete(create_db_engine())
    g_sheet = Model.GoogleSheet()

    # Daemon for updating google sheet
    set_interval(update_google_sheet, Config.GOOGLE_REFRESH_TIME)

    app_param = {
        'db_engine': db_engine,
        'g_sheet': g_sheet,
    }
    app = tornado.web.Application([
        (r'/', View.IndexHandler, app_param),
        (r'/qa', View.QaHandler, app_param),
        (r'/poll', View.PollHandler, app_param),
        (r'/register', View.RegisterHandler, app_param),
        (r'/register_data', View.RegisterDataHandler, app_param),
        (r'/check_login', View.CheckLoginHandler, app_param),
        (r'/login', View.LoginHandler, app_param),
        (r'/logout', View.LogoutHandler, app_param),
        (r'/forget', View.ForgetHandler, app_param),
        (r'/set_password', View.SetPasswordHandler, app_param),
        (r'/register_options', View.RegisterOptionsHandler, app_param),
        (r'/indiv_data', View.IndividualDataHandler, app_param),
        (r'/modify_indiv_data', View.ModifyIndividualDataHandler, app_param),
        (r'/rule_question', View.RuleQuestionHandler, app_param),
        (r'/rule_test', View.RuleTestHandler, app_param),
        (r'/application', View.ApplicationHandler, app_param),
        (r'/application_answer', View.ApplicationAnswerHandler, app_param),
        (r'/mg', View.ManageHandler, app_param),
        (r'/mg/qa_del', View.QaDeleteHandler, app_param),
        (r'/mg/qa_add', View.QaAddHandler, app_param),
        (r'/mg/poll_del', View.PollDeleteHandler, app_param),
        (r'/mg/poll_add', View.PollAddHandler, app_param),
        (r'/mg/rule_question_add', View.RuleQuestionAddHandler, app_param),
        (r'/mg/rule_question_del', View.RuleQuestionDeleteHandler, app_param),
        (r'/mg/user_data', View.UserDataHandler, app_param),
        (r'/mg/application_add', View.ApplicationAddHandler, app_param),
        (r'/mg/application_del', View.ApplicationDeleteHandler, app_param),
        (r'/mg/set_power', View.SetPowerHandler, app_param),
        (r'/cms_token', View.GetCmsTokenHandler, app_param),
        (r'/gs', View.UpdateGoogleSheetHandler, app_param),
    ], cookie_secret=Config.SECRET_KEY)
    app.listen(7122)

    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
