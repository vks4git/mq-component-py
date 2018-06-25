from mq.component import Component
from mq.protocol import message_type, message_spec, create_message, never_expires
import msgpack

from time import time
from clock_messages import ClockResponse

class ClockReply(Component):
    """
    Simple component example.
    It receives a config message with JSON-encoded question "What time is it?" and sends back result with current time. 
    """

    def run(self, sched_out, contr_out, sched_in, state_message):
        while True:
            tag, msg = contr_out.recv_multipart()
            if message_type(tag) == 'config' and message_spec(tag) == 'example_clock':
                self.approve_tag(tag)
                self.logger.write_log('received message from %s' % msg.id)
                msg_data = msgpack.unpackb(msg.data, raw=False)
                print(msg_data)
                cur_time = int(time() * 1000)
                self.logger.write_log('Result sent back to %s' % msg.id)
                answer = create_message(msg.id, self.get_config().creator, never_expires, 'example_clock', 'result', ClockResponse(cur_time).pack(), False, b'')
                sched_in.send(answer)


if __name__ == "__main__":
    comp = ClockReply("example_clock-reply-py")
