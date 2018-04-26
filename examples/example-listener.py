from mq.component import Component


class ExampleListener(Component):
    """
    Simple component example.
    In an infinite loop it receives message from the scheduler, prints its data and sets status variable.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            tag, msg = sched_out.recv_multipart()
            print(msg.data)
            message.value = "Processed message from %s" % msg.creator


if __name__ == "__main__":
    comp = ExampleListener("example-listener")
