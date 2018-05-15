from mq.component import Component
from mq.protocol import message_type, message_spec, create_message, never_expires
import json

from time import time

class ClockReply(Component):
    """
    Simple component example.
    It receives a config message with JSON-encoded data which contains two operands and action and sends back the result.
    write_log function is used here as an example.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            tag, msg = contr_out.recv_multipart()
            if message_type(tag) == 'config' and message_spec(tag) == 'example_clock':
                self.write_log('received message from %s' % msg.id.decode('UTF-8'))
                msg_data = json.loads(msg.data.decode('UTF-8'))
                print(msg_data)
                cur_time = int(time() * 1000)
                self.write_log('Result sent back to %s' % msg.id.decode('UTF-8'))
                answer = create_message(msg.id, self.get_config().creator, never_expires, 'example_clock', 'MessagePack', 'result', json.dumps({ "answer" : cur_time }).encode('UTF-8'))
                sched_in.send(answer)


if __name__ == "__main__":
    comp = ClockReply("example_clock-reply-py")
