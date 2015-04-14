def reraise(exc_info):
    (klass, message, trace) = exc_info
    raise klass(message).with_traceback(trace)