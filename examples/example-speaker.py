from mq.component import Component
from mq.protocol import create_message
import time


class ExampleSpeaker(Component):
    """
    Simple component example.
    In an infinite loop it sends a message to the scheduler every two seconds.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            message = create_message(b'', self.get_config().creator, 1e17, 'example-speaker', 'JSON', 'config', b'{ \"message\" : \"Hello! It\'s me.\" }')
            print(b'sent %s' % message.data)
            sched_in.send(message)
            time.sleep(2)


if __name__ == "__main__":
    comp = ExampleSpeaker("example-speaker")
