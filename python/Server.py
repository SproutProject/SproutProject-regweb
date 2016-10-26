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
        (r'/poll', View.PollViewerHandler, app_param),
    ])
    app.listen(7122)

    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
