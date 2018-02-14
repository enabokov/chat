import base64
import logging

import aioreloader
from aiohttp import web
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
from jinja2 import Environment, FileSystemLoader

from misc.auth import DictAuthorization, user_map
from misc.jinja2 import setup_jinja2
from misc.setup import Loop, setup_postgres
from service.handlers import Router

from .middlewares import TemplateMiddleware
from .routes import setup_routes
from .settings import APP_ROOT, JINJA2_ENVIRONMENT, STATIC_ROOT, TEMPLATES_ROOT


class Server(
    TemplateMiddleware,
):
    host = '0.0.0.0'
    port = 9000

    router = None
    http_server = None
    loop = Loop().get_loop()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = None
    reloader = None

    def __init__(self):
        self.app = web.Application(loop=self.loop)
        self.app.user_map = user_map
        self.app['loop'] = self.loop

        logging.info('App initialized')

    def setup(self):
        self.app['sockets'] = []

        self.app.on_shutdown.append(self.on_shutdown)

        jinja2_env = Environment(
            loader=FileSystemLoader([TEMPLATES_ROOT, APP_ROOT]))
        self.app[JINJA2_ENVIRONMENT] = jinja2_env
        jinja2_env = setup_jinja2(jinja2_env, self.app)
        jinja2_env.globals['app'] = self.app

        self.app.router.add_static(
            '/static/',
            path=STATIC_ROOT,
            name='static')

        self.app['pool'] = self.loop.run_until_complete(
            setup_postgres(loop=self.loop),
        )

        self.router = Router(self.app)
        self.router.setup_index_handlers()
        self.router.setup_chat_handlers()
        setup_routes(self.app, self.router)

        self.app.middlewares.append(self.middleware)

        # secret_key must be 32 url-safe base64-encoded bytes
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)

        setup_session(
            self.app,
            EncryptedCookieStorage(
                secret_key,
                cookie_name='API_SESSION'),
        )

        policy = SessionIdentityPolicy()
        setup_security(self.app, policy, DictAuthorization(user_map))

        self.handler = self.app.make_handler(loop=self.loop)

        aioreloader.watch('service/handlers/')

    def run(self):
        self.reloader = aioreloader.start(loop=self.loop)
        http_server = self.loop.create_server(
            self.handler,
            self.host,
            self.port,
        )

        self.http_server = self.loop.run_until_complete(http_server)

        try:
            logging.info('App was started. '
                         'Running on %(host)s:%(port)s',
                         {'host': self.host, 'port': self.port})
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.reloader.cancel()
            logging.info('Aioreloader is closing')

            self.http_server.close()
            logging.info('HTTP Server is closing')

            self.loop.run_until_complete(self.http_server.wait_closed())
            logging.info('HTTP Server is closed')

            self.loop.run_until_complete(self.app.shutdown())
            logging.info('App was shutdown')

            self.loop.run_until_complete(self.handler.shutdown())
            logging.info('Handler is shutting down')

            self.loop.run_until_complete(self.app.cleanup())
            self.loop.close()
            logging.info('App was finished')

    async def on_shutdown(self, app):
        for ws in app['sockets']:
            await ws.close()