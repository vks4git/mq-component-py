import msgpack
import json

class JSON:
    def pack(self):
        """ Creates a JSON string from an instance of this class.

        Returns:
            JSON string.
        """
        return json.dumps(self.__dict__).encode('UTF-8')

    def unpack(self, packed_data : bytes):
        raise NotImplementedError('Unpacking from JSON not implemented.')


class MessagePack:
    def pack(self):
        """ Creates a MessagePack byte sequence from an instance of this class.
        * See MessagePack specification at https://msgpack.org/index.html

        Returns:
            MessagePack byte sequence.
        """
        dictionary = {}
        for k, v in self.__dict__.items():
            dictionary[k.encode('UTF-8')] = v
        return msgpack.packb(dictionary, use_bin_type = True)

    def unpack(self, packed_data : bytes):
        raise NotImplementedError('Unpacking from MessagePack not implemented.')


class Message(MessagePack):
    def __init__(self):
        self.id: bytes = None
        self.pid: bytes = None
        self.creator: str = None
        self.created_at: int = None
        self.expires_at: int = None
        self.spec: str = None
        self.encoding: str = None
        self.type: str = None
        self.data: bytes = None


    def unpack(self, packed_data):
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
        dictionary = msgpack.unpackb(packed_data, raw=False)

        self.id = unpack_field(dictionary, b'id')
        self.pid = unpack_field(dictionary, b'pid')
        self.creator = unpack_field(dictionary, b'creator')
        self.created_at = unpack_field(dictionary, b'created_at')
        self.expires_at = unpack_field(dictionary, b'expires_at')
        self.spec = unpack_field(dictionary, b'spec')
        self.encoding = unpack_field(dictionary, b'encoding')
        self.type = unpack_field(dictionary, b'type')
        self.data = unpack_field(dictionary, b'data')


class MonitoringResult(MessagePack):
    def __init__(self):
        self.sync_time = None
        self.name = None
        self.is_alive = None
        self.message = None

    def unpack(self, packed_data):
        dictionary = msgpack.unpackb(packed_data, raw=False)

        self.sync_time = unpack_field(dictionary, b'sync_time')
        self.name = unpack_field(dictionary, b'name')
        self.is_alive = unpack_field(dictionary, b'is_alive')
        self.message = unpack_field(dictionary, b'message')


def unpack_field(msg: dict, name: bytes):
    if name in msg:
        return msg.get(name)
    else:
        raise ValueError('could not unpack field with name ' + name)
