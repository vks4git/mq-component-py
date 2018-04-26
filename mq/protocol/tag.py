from mq.protocol.types import Message


def message_tag(msg: Message) -> bytes:
    return msg.type.encode('UTF-8') + b':' + msg.spec.encode(
        'UTF-8') + b':' + msg.id + b':' + msg.pid + b':' + msg.creator.encode('UTF-8')


def message_type(tag: bytes) -> str:
    return get_field(tag, 0).decode('UTF-8')


def message_spec(tag: bytes) -> str:
    return get_field(tag, 1).decode('UTF-8')


def message_id(tag: bytes) -> bytes:
    return get_field(tag, 2)


def message_pid(tag: bytes) -> bytes:
    return get_field(tag, 3)


def message_creator(tag: bytes) -> str:
    return get_field(tag, 4).decode('UTF-8')


def get_field(tag: bytes, ix: int) -> bytes:
    if len(tag.split(b':')) != 5:
        raise ValueError('not a message tag: %s, length %i' % (tag, len(tag.split(b':'))))
    elif ix < 0 or ix > 4:
        raise ValueError('tag field index out of bounds.')
    else:
        return tag.split(b':')[ix]
