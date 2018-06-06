from mq.component import Component
from mq.protocol import message_type, message_spec


class RadioListener(Component):
    """
    Simple component example.
    In an infinite loop it receives message from the scheduler, prints its data and sets status variable.
    """

    def run(self, sched_out, contr_out, sched_in, state_message):
        while True:
            tag, msg = sched_out.recv_multipart()
            if message_type(tag) == 'data' and message_spec(tag) == 'example_radio':
                self.approve_tag(tag)
                print(msg.data)
                state_message.value = "Processed message from %s" % msg.creator


if __name__ == "__main__":
    comp = RadioListener("example_radio-listener-py")
