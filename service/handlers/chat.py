import json
import os
from datetime import datetime as dt

from aiohttp import web
from aiohttp_security import authorized_userid

from misc.handlers import TemplateHandler

from . import BaseHandler
from ..storages.users import Storage

from aiohttp.web import (WebSocketResponse, WSMsgType)


class Handler(
    BaseHandler,
    TemplateHandler,
):
    path = 'service/storages/log.json'
    message_counter = 0
    max_message_counter = 1000
    init_file = True

    def __init__(self, app):
        self.storage = Storage(app)
        self.loop = app['loop']
        self.loop.run_until_complete(self.__pre_setup_json_file())

    async def websocket_chat(self, request):
        username = await authorized_userid(request)
        if username is None:
            return self.render_template(
                template_name='page/index.html',
                request=request,
                context={},
            )

        user_counter = await self.storage.get_all_users()

        resp = WebSocketResponse()
        available = resp.can_prepare(request)
        print('=' * 30)
        print(f'Socket: {available}')
        print(f'User: {username}')
        print('=' * 30)
        if not available:
            return self.render_template(
                template_name='page/chat.html',
                request=request,
                context={
                    'user_name': username,
                    'user_count': len(user_counter),
                },
            )

        await resp.prepare(request)

        try:
            print('Someone joined.')
            for ws in request.app['sockets']:
                await ws.send_str('Someone joined.')
            request.app['sockets'].append(resp)

            async for msg in resp:
                if msg.type == WSMsgType.TEXT:
                    for ws in request.app['sockets']:
                        resp = {
                            'time': str(dt.now().time()),
                            'name': username,
                            'message': msg.data,
                        }
                        await self.save(resp)
                        if ws is not resp:
                            await ws.send_json(resp)
                else:
                    return resp
            return resp
        finally:
            request.app['sockets'].remove(resp)
            print('Someone disconnected.')
            for ws in request.app['sockets']:
                await ws.send_str('Someone disconnected.')

    async def get_cached_messages(self, request):
        with open(self.path) as json_data:
            data = json.load(json_data)

        return web.Response(
            status=web.HTTPOk.status_code,
            content_type='text/html',
            charset='utf-8',
            body=json.dumps(data),
            reason=None,
        )

    async def __flush(self):
        open(self.path, 'w').close()

    async def __pre_setup_json_file(self):
        await self.__flush()
        if os.stat(self.path).st_size == 0:
            with open(self.path, 'w') as outfile:
                outfile.write('[\n]')

    async def __save_to_log(self, data):
        with open(self.path, 'rb+') as outfile:
            outfile.seek(-1, os.SEEK_END)
            outfile.truncate()

        with open(self.path, 'a') as outfile:
            if not self.init_file:
                outfile.write(',\n')
            json.dump(data, outfile, sort_keys=True)
            outfile.write(']')
            self.init_file = False

    async def save(self, data):
        self.message_counter += 1
        if self.message_counter >= self.max_message_counter:
            await self.__flush()
            self.message_counter = 0
        await self.__save_to_log(data)
