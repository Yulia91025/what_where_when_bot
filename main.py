import os

from kts_backend.web.app import setup_app as setup_kts_backend_app
from admin.web.app import setup_app as setup_admin_app
from aiohttp.web import run_app

from database.database import Database

from aiohttp import web
import asyncio

runners = []


async def start_app(app, address="localhost", port=8080):
    runner = web.AppRunner(app)
    runners.append(runner)
    await runner.setup()
    site = web.TCPSite(runner, address, port)
    await site.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    database = Database()
    loop.run_until_complete(database.connect())
    loop.create_task(
        start_app(
            setup_kts_backend_app(
                config_path=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "config.yml"
                ),
                database=database,
            ),
            port=8081,
        )
    )
    loop.create_task(
        start_app(
            setup_admin_app(
                config_path=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "config.yml"
                ),
                database=database,
            ),
            port=8080,
        )
    )
    loop.run_until_complete(database.disconnect())

    try:
        loop.run_forever()
    except:
        pass
    finally:
        for runner in runners:
            loop.run_until_complete(runner.cleanup())

    # run_app(
    #     setup_kts_backend_app(
    #         config_path=os.path.join(
    #             os.path.dirname(os.path.realpath(__file__)), "config.yml"
    #         )
    #     )
    # )
