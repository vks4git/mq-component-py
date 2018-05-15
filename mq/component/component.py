import multiprocessing as mp
import zmq
from datetime import datetime
from ctypes import c_char_p

from mq.component.communication import default_communication
from mq.component.monitoring import default_monitor
from mq.component.technical import default_tech_listener
from mq.config import Config

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

    def __init__(self, name):
        if platform.system() == 'Windows':
            raise OSError('Windows is not supported.')
        if sys.version_info < (3, 0):
            raise EnvironmentError('Python 3 only is supported.')

        self._config = Config(name)
        self._name = name

        manager = mp.Manager()

        self.shared_message = manager.Value(c_char_p, '')
        self.is_alive = manager.Value(bool, False)
        self.task_id = manager.Value(c_char_p, '')

        self._tech_master, self._tech_child = mp.Pipe(duplex=True)

        self._tech_listen = mp.Process(target=default_tech_listener,
                                       args=(self._config, self._tech_child,),
                                       name='Technical channel listener')

        self._monitor = mp.Process(target=default_monitor,
                                   args=(self._config, self.shared_message, self.is_alive,),
                                   name='Monitoring sender')

        self._communication = mp.Process(target=default_communication,
                                         args=(self._config, self.run, self.shared_message, self.task_id,),
                                         name='Communication channel – scheduler')

        self._tech_listen.start()
        self.write_log('Technical listener started.')
        self._communication.start()
        self.write_log('Communicational process started.')
        self.is_alive.value = True
        self._monitor.start()
        self.write_log('Monitor started.')

        while True:
            kill_id = self._tech_master.recv()
            if self.task_id == kill_id and self._communication is not None:
                self.write_log('Kill message received – restarting communicational process.')
                self._communication.terminate()
                self.is_alive.value = False
                self._communication = mp.Process(target=default_communication,
                                                 args=(self._config, self._action_wrapper, self.shared_message, self.task_id,),
                                                 name='Communication channel – scheduler')
                self._communication.start()
                self.write_log('Communicational process started.')
                self.is_alive.value = True

    def _action_wrapper(self, sched_out, contr_out, sched_in, message):
        try:
            run(sched_out, contr_out, sched_in, message)
        except Exception as e:
            self.write_log(format(e), log_type='error')

    def run(self, sched_out, contr_out, sched_in, message):
        pass

    def get_config(self):
        return self._config

    def terminate(self):
        self._communication.terminate()
        self._tech_listen.terminate()
        self._monitor.terminate()

    def write_log(self, logstring, log_type = 'info'):
        current_time = str(datetime.now())
        header = '[' + current_time + ' : ' + self._name + ' : ' + log_type + ']' 
        with open(self._config.logfile, 'a+') as log:
            log.write(header + logstring + '\n')

