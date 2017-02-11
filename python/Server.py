import threading
import requests

import tornado.ioloop
import tornado.netutil
import tornado.process
import tornado.httpserver
import tornado.web
import tornado.websocket
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import Model
import Config
import Views.User
import Views.Register
import Views.ResetPassword
import Views.QuestionAnswer
import Views.Poll
import Views.RuleTest
import Views.Application
import Views.Token
import Views.GoogleSheet


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def update_google_sheet():
    r = requests.post('http://%s/spt/d/google_sheet/update' % Config.HOST, params={'key': Config.SECRET_KEY})

def main():
    Model.init()

    g_sheet = Model.GoogleSheet()

    # Daemon for updating google sheet
    set_interval(update_google_sheet, Config.GOOGLE_REFRESH_TIME)

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
    session = SessionMaker()

    app_param = {
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
        (r'/token/pre_test_score', Views.Token.PretestScoreHandler, app_param),
        (r'/token/pre_test', Views.Token.PretestHandler, app_param),
        (r'/token/entrance', Views.Token.EntranceHandler, app_param),
        (r'/google_sheet/update', Views.GoogleSheet.UpdateHandler, app_param),
    ], cookie_secret=Config.SECRET_KEY)

    httpsock = tornado.netutil.bind_sockets(Config.LISTEN_PORT)
    tornado.process.fork_processes(16)
    httpsrv = tornado.httpserver.HTTPServer(app)
    httpsrv.add_sockets(httpsock)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
