import multiprocessing as mp
import zmq
from ctypes import c_char_p

from mq.component.communication import default_communication
from mq.component.monitoring import default_monitor
from mq.component.technical import default_tech_listener
from mq.component.error import default_error_handler
from mq.config import Config
from mq.protocol import Logger, error_killed, error_component, message_id, MQError

import platform
import sys

class Component:
    """
    A MoniQue component.
    It behaves as described below:
    * On creation three processes are spawned: technical listener, communication process and monitoring sender.
    * User implements communication logic via implementation of @run@ method in Component class descendants.
    * Technical listener communicates with the master-process using pipe without duplex. 
    * When a kill message is received, communication process restarts.

    Component uses three shared between processes variables:
    * shared_message: user-defined variable which is included in monitoring message.
    * is_alive: set to True iff communicational process works properly. Included in monitoring message.
    * task_id: current task id. Compared with kill_task_id from kill message.

    User is free to use write_log function.
    """

    def __init__(self, name, tag_filter = lambda tag : True):
        if platform.system() == 'Windows':
            raise OSError('Windows is not supported.')
        if sys.version_info < (3, 0):
            raise EnvironmentError('Python 3 only is supported.')

        self._config = Config(name)
        self._name = name
        self.message_filter = tag_filter

        manager = mp.Manager()

        self.logger = Logger(name)

        self.error_recv, self.error_send = mp.Pipe(duplex = False)

        self.shared_message = manager.Value(c_char_p, '')
        self.is_alive = manager.Value(bool, False)
        self.task_id = manager.Value(c_char_p, '')

        self._tech_master, self._tech_child = mp.Pipe(duplex=True)

        self._error_handler = mp.Process(target = default_error_handler,
                                         args = (self.error_recv, self.logger, self._config, self.shared_message, self.task_id),
                                         name = 'Error handler')

        self._tech_listen = mp.Process(target=default_tech_listener,
                                       args=(self.error_send, self.logger, self._config, self._tech_child,),
                                       name='Technical channel listener')

        self._monitor = mp.Process(target=default_monitor,
                                   args=(self.error_send, self.logger, self._config, self.shared_message, self.is_alive,),
                                   name='Monitoring sender')

        self._communication = mp.Process(target=default_communication,
                                         args=(self.error_send, self.logger, self._config, self._action_wrapper, self.shared_message, self.task_id, self._tech_child, ),
                                         name='Communication channel – scheduler')

        self._error_handler.start()
        self.logger.write_log('Component :: Error handler started.')
        self._tech_listen.start()
        self.logger.write_log('Component :: Technical listener started.')
        self._communication.start()
        self.logger.write_log('Component :: Communicational process started.')
        self.is_alive.value = True
        self._monitor.start()
        self.logger.write_log('Component :: Monitor started.')

        while True:
            command = self._tech_master.recv()
            print(command)
            print(self.task_id.value)
            if self.task_id.value == command and self._communication is not None:
                self.task_id.value = None
                self.logger.write_log('Component :: Kill message received – restarting communicational process.')
                self.error_send.send(MQError(error_killed, 'Component killed.'))
                self._communication.terminate()
                self.is_alive.value = False
                self._communication = mp.Process(target=default_communication,
                                                 args=(self.error_send, self.logger, self._config, self._action_wrapper, self.shared_message, self.task_id, self._tech_child, ),
                                                 name='Communication channel – scheduler')
                self._communication.start()
                self.logger.write_log('Component :: Communicational process started.')
                self.is_alive.value = True
            elif command == "restart_communicational":
                self._communication = mp.Process(target=default_communication,
                                                 args=(self.error_send, self.logger, self._config, self._action_wrapper, self.shared_message, self.task_id, self._tech_child, ),
                                                 name='Communication channel – scheduler')
                self._communication.start()
                self.is_alive.value = True


    def _action_wrapper(self, sched_out, contr_out, sched_in, state_message, master_send):
        try:
            self.run(sched_out, contr_out, sched_in, state_message)
        except Exception as e:
            self.is_alive.value = False
            error_msg = 'User action :: %s.' % format(e)
            self.logger.write_log(error_msg, log_type='error')
            error = MQError(error_component, error_msg)
            self.error_send.send(error)
            master_send.send("restart_communicational")


    def run(self, sched_out, contr_out, sched_in, state_message):
        pass

    def approve_tag(self, tag : bytes):
        self.task_id.value = message_id(tag).decode('UTF-8')

    def get_config(self):
        return self._config

    def terminate(self):
        self._communication.terminate()
        self._tech_listen.terminate()
        self._monitor.terminate()


