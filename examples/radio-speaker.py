from mq.component import Component
from mq.protocol import create_message, never_expires
import time
from radio_messages import RadioMessage


class RadioSpeaker(Component):
    """
    Simple component example.
    In an infinite loop it sends a message to the scheduler every two seconds.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            message = create_message(b'', self.get_config().creator, never_expires, 'example_radio', 'JSON', 'data', RadioMessage().pack())
            print(b'sent %s' % message.data)
            sched_in.send(message)
            time.sleep(2)


if __name__ == "__main__":
    comp = RadioSpeaker("example_radio-speaker-py")
