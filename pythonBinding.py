import frida
import argparse
import time
import os
import logging
import sys
import subprocess
from colorlog import ColoredFormatter

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    color_formatter = ColoredFormatter(
	        "%(log_color)s[%(asctime)s] [%(levelname)-4s]%(reset)s - %(message)s",
	        datefmt='%d-%m-%y %H:%M:%S',
	        reset=True,
	        log_colors={
		        'DEBUG':    'cyan',
		        'INFO':     'green',
		        'WARNING':  'bold_yellow',
		        'ERROR':    'bold_red',
		        'CRITICAL': 'bold_red',
	        },
	        secondary_log_colors={},
	        style='%')
    logging_handler = logging.StreamHandler()
    logging_handler.setFormatter(color_formatter)
    logger.addHandler(logging_handler)

# setup logging for script
setup_logging()
logger = logging.getLogger(__name__)

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)

# start frida-server process
def frida_server_start_process(device_id,frida_server):
    frida_server_subprocess = subprocess.Popen("adb -s "+device_id+" shell "+frida_server+" &", shell=True)
    if frida_server_subprocess:
        return frida_server_subprocess
    else:
        return None

# kill frida-server running process
def frida_server_kill_process(frida_subprocess):
    logger.info("Terminating frida-server process - PID: {0}".format(frida_subprocess.pid))
    frida_subprocess.kill()

# installing frida-server on android devices
def frida_server_install(device_id, frida_install_path, device_install_path='/data/local/tmp/', frida_server_name="frida-server"):
    logger.info("Installing frida service on device id: " + device_id)
    try:
        frida_server_device_path = device_install_path+frida_server_name
        frida_push_device = subprocess.Popen("adb -s "+device_id+" push \""+frida_install_path+"\" "+
                                            frida_server_device_path, shell=True, stderr=subprocess.STDOUT,
                                            stdout=subprocess.PIPE)
        data, nothing = frida_push_device.communicate()
        data_str = str(data,'utf-8')
        if data_str.index('pushed.'):
            logger.info("Frida-server was successfully pushed to selected device on "+ device_install_path)
            # set frida-server permissions
            frida_server_perm = subprocess.Popen("adb -s "+device_id+" shell chmod 755 \""+frida_server_device_path+"\"", shell=True,
                                                stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            logger.info("Set frida-server with execution permissions")
            frida_server_perm.wait()
            frida_server_perm.kill()
        else:
            logger.error("Please check path permissions")
        frida_push_device.kill()
        return frida_server_start_process(device_id,frida_server_device_path)
    except:
        return None

# check if frida-server exists on selected device
def frida_server_check_existing(device_id):
    frida_existing = subprocess.Popen("adb -s "+device_id+" shell \"ps| grep frida-server\"", 
                                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data, nothing = frida_existing.communicate()
    if (len(data) != 0):
        frida_existing.kill()
        return True
    else:
        frida_existing.kill()
        return None

# creation of devices choice menu
def create_devices_menu(device_list):
    print("-" * 8 + " Connected Devices List " + "-" * 8 + "\n")
    print(" Id  |" + "   Type " +"  " +"|" + " " * 7 + "IP Address" + " " * 7 + "|"+" " *10 + "Name")
    print("-" * 5 + "+" + "-" * 10 + "+" + "-" * 24 + "+" + "-" * 28 )
    for index, value in enumerate(device_list):
        print("[{0}]  |  {1}  |   {2}  | {3}".format(index,value.type,value.id,value.name))
        print("-" * 70)
    return device_list

# return user selected device
def select_device(devices):
    user_id_selection = int(input("[*] Please specify a device number: "))
    if (devices[user_id_selection].id == None):
        print("[*] ID Was not found !")
        select_device(devices)
    selected_device = devices[user_id_selection].id
    print("-" * 49)
    logger.info("Connecting to device id -> " + selected_device)
    return selected_device

# enumerate local/remote/usb devices and return a list by given type
def enumerate_connected_devices():
    devices = frida.enumerate_devices()
    if (len([x for x in devices if len(x.id) > 5]) != 0):
        return create_devices_menu([x for x in devices if len(x.id) > 5])
    else:
        return None

def frida_session_activity_handler(con_device,activity,**kwargs):
    for _ in range(5):
        if (activity != 'list_pids'):
            time.sleep(1)
            if activity == 'pid':
                frida_session = con_device.attach(int(kwargs.get('pid')))
            elif activity == 'spawn':
                pid = con_device.spawn([kwargs.get('spawn')])
                if pid:
                    frida_session = con_device.attach(pid)
                    # resume app after spawning
                    con_device.resume(pid)
                    return frida_session
                else:
                    pass
            else:
                frida_session = con_device.attach(kwargs.get('attach'))
            if (frida_session):
                return frida_session
            else:
                return None
        # attach frida to existing running package by name
        elif (activity == 'list_pids'):
            time.sleep(1)
            pid_list = con_device.enumerate_processes()
            if pid_list:
                return pid_list
            else:
                return None

# read script file from local FS
def read_hooking_script(filename):
    try:
        with open(filename, 'r') as raw:
            return raw.read()
    except IOError:
        return None

if __name__ == '__main__':
    try:
        # define application argument parser
        parser = argparse.ArgumentParser(description="Frida RE Easy Python Binding")
        parser.add_argument("-s","--spawn",help="Set package name to spawning a new process")
        parser.add_argument("-p","--pid",help="Specify a PID number")
        parser.add_argument("-a","--attach",help="Set a process name to attach")
        parser.add_argument("-S","--script",help="Specify a Javascript hooking script name")
        parser.add_argument("-P","--frida-path-device",default="/data/local/tmp/",help="Set frida-server path on selected device [Default /data/local/tmp/]")
        parser.add_argument("-i","--frida-exec-path",default="./frida-bin/frida-server",help="Set frida-server executable installation path")
        parser.add_argument("-n","--frida-server-name",default="frida-server",help="Set frida-server executable name on device [Default frida-server]")
        parser.add_argument("-lp","--list-pids",action="store_true",help="Enumerate running processes by PID on selected device")
        parser.add_argument("-la","--list-apps",action="store_true",help="Enumerate installed applications on selected device")
        parser.add_argument("-t","--timeout",default=1000,help="Set USB connect timeout [Default 1000]")
        args = parser.parse_args()

        if not args.script:
            while True:
                args.script = input("Please type your script path: ")
                script_exists = os.path.isfile(args.script)
                if script_exists:
                    break
                else:
                    logger.error("The file you specified does not exists.")
        logger.info("Enumerating connected devices\n")
        # enumerate connected devices
        devices = enumerate_connected_devices()
        if devices:
            selected_device = select_device(devices)
        else:
            logger.error("No connected devices found")
            sys.exit(1)
        if frida_server_check_existing(selected_device):
            logger.info("Frida-server is running on the selected device!")
        else:
            frida_server_process = frida_server_install(selected_device,args.frida_exec_path,
                                                        args.frida_path_device,args.frida_server_name)
            if frida_server_process:
                logger.info("New frida-server process initiated on PID {0}".format(frida_server_process.pid))
            else:
                logger.error("Frida-server could not be deployed on the selected device!")
                sys.exit(1)
        connected_device = frida.get_device(selected_device, args.timeout)
        if args.list_pids or args.list_apps:
            pid_list = frida_session_activity_handler(connected_device,'list_pids')
            if pid_list:
                print("-" * 50 + "\n[*] Generated process list on selected device\n" + "-" * 50)
                print("Process Name" + " " * 21 + "PID"+"\n"+"-" * 30 + " " + "-" * 7)
                for key, val in enumerate(pid_list):
                    spaces = " " * (33 - len(pid_list[key].name))
                    print("{0}{1}{2}".format(pid_list[key].name,spaces,pid_list[key].pid))
                pid_choice = int(input("\n[*] Please enter PID number: "))
                frida_session = frida_session_activity_handler(connected_device,'pid',pid=pid_choice)
            else:
                logger.error("Could not enumerate process on the selected device")
                sys.exit(1)
        # spawn a new process instance and attac
        elif args.spawn:
            frida_session = frida_session_activity_handler(connected_device,'spawn',spawn=args.spawn)
            if frida_session:
                logger.info("Spawned package : {0} on pid {1}".format(args.spawn,frida_session._impl.pid))
            else:
                logger.error("Could not spawn the requested package")
                sys.exit(1)
        # attach frida to existing running pid
        elif args.pid:
            frida_session = frida_session_activity_handler(connected_device,'pid',pid=args.pid)
            if frida_session:
                logger.info("Attaching frida session to PID - {0}".format(frida_session._impl.pid))
            else:
                logger.error("Could not attach the requested process")
                sys.exit(1)
        elif args.attach:
            frida_session = frida_session_activity_handler(connected_device,'attach',attach=args.attach)
            if frida_session:
                logger.info("Attaching frida session to process name - {0}".format(args.attach))
            else: 
                logger.error("Could not attach to the requested package")
        else:
            logger.warning("You must specify atleast one option to run the application\n[*] Please use --help for full reference")
        # set timeout so java.perform will not crash
        time.sleep(1)

        # load hooking script
        hooking_script = frida_session.create_script(read_hooking_script(args.script))
        if hooking_script:
            hooking_script.on('message', on_message)
            hooking_script.load()
        else:
            logger.error("The specified script '{0}' was not found!".format(args.script))
        
        # stop python script from terminating
        input('Press any key to continue...')
        # kill frida-server process before exiting
    except Exception as e:
        logger.error("Something went wrong, please check your input.\n Error - {0}".format(e))