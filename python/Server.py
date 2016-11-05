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


def main():
    Model.init()

    tornado.platform.asyncio.AsyncIOMainLoop().install()
    db_engine = asyncio.get_event_loop().run_until_complete(create_db_engine())

    app_param = {
        'db_engine': db_engine,
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
        (r'/mg', View.ManageHandler, app_param),
        (r'/mg/qa', View.QaHandler, app_param),
        (r'/mg/qa_del', View.QaDeleteHandler, app_param),
        (r'/mg/qa_add', View.QaAddHandler, app_param),
        (r'/mg/poll', View.PollHandler, app_param),
        (r'/mg/poll_del', View.PollDeleteHandler, app_param),
        (r'/mg/poll_add', View.PollAddHandler, app_param),
        (r'/mg/user_data', View.UserDataHandler, app_param),
    ], cookie_secret='7122')
    app.listen(7122)

    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
