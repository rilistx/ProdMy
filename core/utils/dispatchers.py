from core import views


# Middlewares
def middleware_dispatchers(dispatcher):
    middleware_list = [
        views.session_bot(dispatcher),
    ]

    return [middleware for middleware in middleware_list]


# Handlers
def handler_dispatchers(dispatcher):
    handler_list = [
        views.start_bot(dispatcher),
        views.stop_bot(dispatcher),
    ]

    return [handler for handler in handler_list]


# Callbacks
def callback_dispatchers(dispatcher):
    callback_list = [

    ]

    return [callback for callback in callback_list]


# All Dispatcher (Middlewares & Handlers)
def all_dispatchers(dispatcher):
    return middleware_dispatchers(dispatcher), handler_dispatchers(dispatcher), callback_dispatchers(dispatcher)
