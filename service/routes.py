

def setup_routes(
    app,
    router,
):

    app.router.add_route(
        'GET',
        '/',
        router.auth.index,
        name='page:index',
    )

    app.router.add_route(
        'GET',
        '/signup',
        router.auth.signup_get,
        name='page:signup_get',
    )

    app.router.add_route(
        'POST',
        '/signup',
        router.auth.signup_post,
        name='page:signup_post'
    )

    app.router.add_route(
        'GET',
        '/login',
        router.auth.login_get,
        name='page:login_get',
    )

    app.router.add_route(
        'POST',
        '/login',
        router.auth.login_post,
        name='page:login_post',
    )

    app.router.add_route(
        'POST',
        '/',
        router.auth.logout,
        name='page:logout',
    )

    app.router.add_route(
        'GET',
        '/chat',
        router.chat.websocket_chat,
        name='page:chat',
    )

    app.router.add_route(
        'GET',
        '/chat/get_cached_messages',
        router.chat.get_cached_messages,
        name='page:get_cached_messages',
    )
