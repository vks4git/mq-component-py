import msgpack


class MessagePack:
    def pack(self):
        pass


class Message(MessagePack):
    id: bytes = None
    pid: bytes = None
    creator: str = None
    created_at: int = None
    expires_at: int = None
    spec: str = None
    encoding: str = None
    type: str = None
    data: bytes = None

    def __init__(self, packed_message: bytes = None):
        """ Creates a Message from MessagePack byte sequence.
        * See Message specification at https://github.com/biocad/mq/blob/develop/doc/PROTOCOL.md
        * See MessagePack specification at https://msgpack.org/index.html

        Args:
            packed_message: packed dictionary with field names as keys and field data as values.

        Returns:
            Message: returns Message if success.

        Raises:
            ValueError: if packed_message is not a dictionary or there are missing some necessary fields.

        """
        if packed_message is not None:
            dictionary = msgpack.unpackb(packed_message, raw=False)

            self.id = unpack_field(dictionary, b'id')
            self.pid = unpack_field(dictionary, b'pid')
            self.creator = unpack_field(dictionary, b'creator')
            self.created_at = unpack_field(dictionary, b'created_at')
            self.expires_at = unpack_field(dictionary, b'expires_at')
            self.spec = unpack_field(dictionary, b'spec')
            self.encoding = unpack_field(dictionary, b'encoding')
            self.type = unpack_field(dictionary, b'type')
            self.data = unpack_field(dictionary, b'data')

    def pack(self):
        """ Creates a MessagePack byte sequence from Message.
        * See Message specification at https://github.com/biocad/mq/blob/develop/doc/PROTOCOL.md
        * See MessagePack specification at https://msgpack.org/index.html

        Args:
            packed_message: packed dictionary with field names as keys and field data as values.

        Returns:
            Message: returns Message if success.

        Raises:
            ValueError: if packed_message is not a dictionary or there are missing some necessary fields.

        """
        dictionary = {}

        dictionary[b'id'] = bytes(self.id)
        dictionary[b'pid'] = bytes(self.pid)
        dictionary[b'creator'] = str(self.creator)
        dictionary[b'created_at'] = int(self.created_at)
        dictionary[b'expires_at'] = int(self.expires_at)
        dictionary[b'spec'] = str(self.spec)
        dictionary[b'encoding'] = str(self.encoding)
        dictionary[b'type'] = str(self.type)
        dictionary[b'data'] = bytes(self.data)

        return msgpack.packb(dictionary, use_bin_type=True)


class MonitoringResult(MessagePack):
    sync_time = None
    name = None
    is_alive = None
    message = None

    def __init__(self, packed_result: bytes = None):
        if packed_result is not None:
            dictionary = msgpack.unpackb(packed_result, raw=False)

            self.sync_time = unpack_field(dictionary, b'sync_time')
            self.name = unpack_field(dictionary, b'name')
            self.is_alive = unpack_field(dictionary, b'is_alive')
            self.message = unpack_field(dictionary, b'message')

    def pack(self):
        dictionary = {b'sync_time': int(self.sync_time), b'name': str(self.name), b'is_alive': bool(self.is_alive),
                      b'message': str(self.message)}

        return msgpack.packb(dictionary, use_bin_type=True)


def unpack_field(msg: dict, name: bytes):
    if name in msg:
        return msg.get(name)
    else:
        raise ValueError('could not unpack field with name ' + name)
