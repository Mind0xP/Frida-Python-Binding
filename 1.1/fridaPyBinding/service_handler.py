from subprocess import Popen, PIPE
import logging

# set logger for module
logger = logging.getLogger(__name__)


class ServiceHandler(object):
    """
    Object which handles frida's server service
    """
    
    def __init__(self, device_id, local_install_path, device_install_path='/data/local/tmp/',
                 frida_bin_name='frida-server', adb_path='adb'):
        """installs frida service on a selected device with optional params
        
        Arguments:
            device_id {[frida core]} -- device id to interact with
            local_install_path {[str]} -- frida-server binary local path
        
        Keyword Arguments:
            device_install_path {str} -- location on device to install frida-server (default: {'/data/local/tmp/'})
            frida_bin_name {str} -- frida-server binary name (default: {"frida-server"})
        """

        self.device_id = device_id
        self.adb_path = adb_path
        self.local_install_path = local_install_path
        self.device_install_path = device_install_path
        self.frida_bin_name = frida_bin_name
        self.frida_server_start_pid = 0
        self.frida_server_bin_ps = False
        self.frida_server_dev_exec_path = self.device_install_path + self.frida_bin_name
    
    def frida_server_install(self):
        """Installs frida-server on selected [device_id] and returns 
           frida's service subprocess object
        
        Returns:
            [Object] -- frida's service subprocess object
        """

        try:
            if self.frida_server_check_existing_ps():
                return
            logger.info("Installing frida service on device id: " + self.device_id)
            frida_server_push = self.__shell_exec(args=['push', self.local_install_path, self.frida_server_dev_exec_path])
            frida_server_push_data = str(frida_server_push, 'utf-8')
            if frida_server_push_data.index('pushed.'):
                if self.frida_server_binary_perm():
                    pass
                else:
                    return
            return self.frida_server_start_process()
        except Exception as e:
            return e

    def frida_server_binary_perm(self):
        """
        Sets frida-server binary permissions and returns bool
        :return: True/None
        """
        frida_server_set_perm = self.__shell_exec(['shell','chmod 755',self.frida_server_dev_exec_path],ps_wait=True)
        if not frida_server_set_perm:
            logger.info("setting {0} with execution permissions".format(self.frida_bin_name))
            return True
        else:
            logger.info("Could not set permissions to {0} as requested, please check folder permissions!".format(self.frida_bin_name))
            return

    def frida_server_check_existing_ps(self):
        """
        Check if the frida service is already running on the selected device id
        :return: bool -- returns True if process exists
        """

        frida_srv_ck_ps = self.__shell_exec(args=['shell', 'ps', '|', 'grep '+self.frida_bin_name])
        if frida_srv_ck_ps:
            logger.info("Frida service is already running on the selected device!")
            return True
        else:
            return

    def frida_server_check_existing_bin(self):
        """
        Check if frida service is already located on the selected device_id
        :return:  True/None
        """

        frida_srv_ck_bin = self.__shell_exec(['shell', 'ls', self.frida_server_dev_exec_path])
        if str(frida_srv_ck_bin, 'utf-8') == self.frida_server_dev_exec_path:
            return True
        else:
            return

    def frida_server_start_process(self):
        """
        Starts frida service and return its subprocess obj for future handle
        :return: Object -- frida service bin pid or None
        """

        self.frida_server_start_pid = self.__shell_exec(['shell', self.frida_server_dev_exec_path, '&'],
                                                        ps_kill=False, ps_pid=True)
        if self.frida_server_start_pid:
            logger.info("New {0} process initiated on PID {1}".format(self.frida_bin_name, self.frida_server_start_pid))
            return self.frida_server_start_pid
        else:
            return

    def __shell_exec(self, args=None, specified_device=True, ps_wait=False, ps_kill=True, ps_pid=False):
        """
        Executes adb command with requested args
        :param args: list of arguments to execute
        :param specified_device: set False to run adb command without specified device
        :param ps_wait: set if process needs wait() after execution
        :param ps_kill: set flag if process needs to hang
        :param ps_pid: get pid number of executed process
        :return: runs __exec with given arguments
        """
        args = args or []
        if specified_device:
            args = ['-s', self.device_id] + args

        return self.__exec(self.adb_path, ps_wait, ps_kill, ps_pid, args=args)

    @staticmethod
    def __exec(executable, ps_wait, ps_kill, ps_pid, args=None):
        """
        Execute subprocess with given arguments
        :param executable: executable to run [self.adb_path]
        :param ps_wait: set if process needs wait() after execution
        :param ps_kill: set flag if process needs to hang
        :param ps_pid: get pid number of executed process
        :param args: given args to run subprocess
        :return: subprocess data or process pid
        """
        args = args or []
        args.insert(0, executable)

        process = Popen(args, stdout=PIPE, stderr=PIPE, shell=False)
        out, err = process.communicate()
        if ps_wait:
            process.wait()
        if ps_kill:
            process.kill()
        if process.returncode != 0:
            raise Exception(err.strip())
        if ps_pid:
            return process.pid
        else:
            return out.strip()