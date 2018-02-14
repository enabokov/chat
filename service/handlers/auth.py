import trafaret as t
from aiohttp import web
from aiohttp_security import forget, remember

from misc.auth import add_user
from misc.handlers import TemplateHandler
from service.trafaret import LoginTrafaret, SignUpTrafaret

from . import BaseHandler
from ..storages.users import Storage


class Handler(
    BaseHandler,
    TemplateHandler,
):

    def __init__(self, app):
        self.storage = Storage(app)

    async def index(self, request):
        return self.render_template(
            template_name='page/index.html',
            request=request,
            context={},
        )

    async def signup_get(self, request):
        return self.render_template(
            template_name='page/auth.html',
            request=request,
            context={
                'signup': True,
                'data': {},
            },
        )

    async def signup_post(self, request):
        get = dict(await request.post())

        try:
            data = SignUpTrafaret(get)
        except t.DataError as exc:
            return self.render_template(
                template_name='page/auth.html',
                request=request,
                context={
                    'signup': True,
                    'data': get,
                    'errors': exc.as_dict()
                }
            )

        try:
            await self.storage.insert(data)
        except web.HTTPBadRequest as exc:
            return self.render_template(
                template_name='page/auth.html',
                request=request,
                context={
                    'signup': True,
                    'data': data,
                    'errors': exc.reason
                }
            )

        await remember(request, response=None, identity=data['name'])
        add_user(**data)

        return web.Response(
            status=web.HTTPSeeOther.status_code,
            headers={'Location': '/chat'},
            content_type='text/html',
            charset='utf-8',
            reason=None,
        )

    async def login_get(self, request):
        return self.render_template(
            template_name='page/auth.html',
            request=request,
            context={
                'signup': False,
                'data': {},
            },
        )

    async def login_post(self, request):
        get = dict(await request.post())

        try:
            data = LoginTrafaret(get)
        except t.DataError as exc:
            return self.render_template(
                template_name='page/auth.html',
                request=request,
                context={
                    'signup': True,
                    'data': get,
                    'errors': exc.as_dict()
                }
            )

        user = await self.storage.get_by_name_with_password(data)

        if user is None:
            return self.render_template(
                template_name='page/auth.html',
                request=request,
                context={
                    'signup': False,
                    'data': get,
                    'errors': 'Login or password is incorrect. '
                              'Or user doesn\'t exist',
                }

            )

        await remember(request, response=None, identity=user['name'])
        add_user(**data)

        return web.Response(
            status=web.HTTPSeeOther.status_code,
            headers={'Location': '/chat'},
            content_type='text/html',
            charset='utf-8',
            reason=None,
        )

    async def logout(self, request):
        await forget(request, None)
        return web.Response(
            status=web.HTTPSeeOther.status_code,
            headers={
                'Location': '/',
            },
            content_type='text/html',
            charset='utf-8',
            reason=None
        )
