import logging
from time import sleep

# set logger for module
logger = logging.getLogger(__name__)


class SessionHandler(object):
    """
    Handle frida server to client session
    """

    def __init__(self, connected_device):

        self.connected_device = connected_device
        self.frida_session = None
        self.process_list = []
        self.application_list = []
        self.package_spawn_pid = None

    def attach(self, args):
        """
        Attaches frida service to requested package identifier or pid id
        :param args: running package identifier or pid id
        :return: True/None
        """
        self.frida_session = self.connected_device.attach(args)
        if self.frida_session:
            logger.info("Attaching frida session to PID - {0}".format(self.frida_session._impl.pid))
            return True
        else:
            logger.error("Could not attach the requested process")
        return

    def spawn(self, args, resume=True):
        """
        Spawns a new package and attaches to PID by given args
        :param args: package identifier
        :param resume: set flag to resume pid after spawn
        :return: True/False
        """

        self.package_spawn_pid = self.connected_device.spawn([args])
        if self.package_spawn_pid:
            x = self.connected_device.attach(int(self.package_spawn_pid))
            logger.info("Spawned package : {0} on pid {1}".format(args, self.package_spawn_pid))
            if resume:
                self.connected_device.resume(self.package_spawn_pid)
            return True
        else:
            logger.error("Could not spawn the requested package!")
        return

    def list_processes(self):
        """
        enumerate running processes and return a list
        :return: process list of selected device
        """
        self.process_list = self.connected_device.enumerate_processes()
        return self.process_list

    def list_applications(self):

        self.application_list = self.connected_device.enumerate_applications()
        return self.application_list