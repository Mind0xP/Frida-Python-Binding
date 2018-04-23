import frida
import os
import logging
import subprocess
import requests
import lzma
import re
from shutil import copyfile
from termcolor import colored
from argparse import ArgumentParser
from time import sleep
from sys import exit
from colorlog import ColoredFormatter

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
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

# extract frida-server tar.xz
def extract_frida_server_comp(file_path):
    # create a subdir for the specified filename
    frida_server_dir = file_path[:-3]
    os.makedirs(frida_server_dir)
    with lzma.open(file_path, 'rb') as f:
        decompressed_file = f.read()
    with open(frida_server_dir+'/frida-server', 'wb') as f:
        f.write(decompressed_file)
        logger.info("Extracted frida-server under - {0}".format(frida_server_dir))
    # del compressed file
    os.remove(file_path)
    return

# check if specific a frida-server is version already located locally
def check_frida_server_version_local(folder_name):
    if os.path.exists(folder_name):
        return True
    else:
        return False

# gets frida-server binaries by requested version/arch
def get_frida_server_repo(arch,version='latest'):
    base_url = 'https://github.com/frida/frida/releases'
    if version == 'latest':
        url = base_url
    else:
        url = base_url + '/tag/' + version
    res = requests.get(url)
    frida_server_path = re.findall(r'\/download\/\d+\.\d+\.\d+\/frida\-server\-\d+\.\d+\.\d+\-android\-'+arch+'\.xz',res.text)
    download_url = base_url + frida_server_path[0]
    filename = frida_server_path[0].split("/")[-1]
    # check if folder already exists
    frida_server_bin_folder = os.path.abspath('bin/')
    frida_server_file_path = os.path.abspath('bin/'+filename)
    frida_server_download_folder = frida_server_file_path[:-3]
    ck_frida_server_folder = check_frida_server_version_local(frida_server_download_folder)
    if ck_frida_server_folder:
        logger.info("The requested version \'{0}\' is already located locally".format(filename[:-3]))
    else:
        # download & write file locally
        with open('bin/'+filename, "wb") as f:
            res = requests.get(download_url)
            f.write(res.content)
        logger.info("The requested file \'{0}\' was successfully downloaded".format(filename))
        extract_frida_server_comp(frida_server_file_path)
    return frida_server_bin_folder, frida_server_download_folder

def frida_server_set_default(src_path,dst_path):
    frida_server_exec_src = src_path+'/frida-server'
    frida_server_exec_dst = dst_path+'/frida-server'
    copied_file = copyfile(frida_server_exec_src,frida_server_exec_dst)
    if copied_file:
        logger.info("The chosen frida-server version was set to default!")
        return copied_file
    else:
        return None

def frida_server_local_versions():
    dir_list = os.listdir("bin")
    frida_server_local_v = [x for x in dir_list if x.find('.') > -1]
    print(" Id  |" + "   Arch " +"  " +"|" + " " * 3 + "Version")
    print("-" * 5 + "+" + "-" * 10 + "+" + "-" * 12)
    for k,v in enumerate(frida_server_local_v):
        _version = v.split("-")
        print("[{0}]  |   {1}    |   {2}    ".format(k,_version[4],_version[2]))
    print("-"*29)
    return frida_server_local_v

# start frida-server process
def frida_server_start_process(device_id,frida_server):
    frida_server_subprocess = subprocess.Popen("adb -s "+device_id+" shell "+frida_server+" &", shell=False)
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
                                            frida_server_device_path, shell=False, stderr=subprocess.STDOUT,
                                            stdout=subprocess.PIPE)
        data, nothing = frida_push_device.communicate()
        data_str = str(data,'utf-8')
        if data_str.index('pushed.'):
            logger.info("Frida-server was successfully pushed to selected device on "+ device_install_path)
            # set frida-server permissions
            frida_server_perm = subprocess.Popen("adb -s "+device_id+" shell chmod 755 \""+frida_server_device_path+"\"", shell=False,
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
                                       shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        sleep(1)
        if activity == 'pid':
            frida_session = con_device.attach(int(kwargs.get('pid')))
            if frida_session:
                logger.info("Attaching frida session to PID - {0}".format(frida_session._impl.pid))
            else:
                logger.error("Could not attach the requested process")
        elif activity == 'spawn':
            pid = con_device.spawn([kwargs.get('spawn')])
            if pid:
                frida_session = con_device.attach(pid)
                logger.info("Spawned package : {0} on pid {1}".format(kwargs.get('spawn'),frida_session._impl.pid))
                # resume app after spawning
                con_device.resume(pid)
            else:
                logger.error("Could not spawn the requested package")
                return None
        elif activity == 'attach':
            frida_session = con_device.attach(kwargs.get('attach'))
            if frida_session:
                logger.info("Attaching frida session to process name - {0}".format(kwargs.get('attach')))
            else: 
                logger.error("Could not attach to the requested package")
        else:
            return None
        return frida_session

def frida_enumerate_device(con_device,activity):
    # list pids on selected device
        if (activity == 'list_pids'):
            pid_list = con_device.enumerate_processes()
            if pid_list:
                return pid_list
            else:
                return None
        # list installed packages on selected device
        elif (activity == 'list_apps'):
            apps_list = con_device.enumerate_applications()
            if apps_list:
                return apps_list
            else:
                return None
            

# read script file from local FS
def read_hooking_script(filename):
        with open(filename, 'r') as raw:
            try:
                return raw.read()
            except (IOError,OSError):
                return None

if __name__ == '__main__':
    try:
        # define application argument parser
        parser = ArgumentParser(description="Frida RE Easy Python Binding")
        parser.add_argument("-s","--spawn",help="Set package name to spawning a new process")
        parser.add_argument("-p","--pid",help="Specify a PID number")
        parser.add_argument("-a","--attach",help="Set a process name to attach")
        parser.add_argument("-S","--script",help="Specify a Javascript hooking script name")
        parser.add_argument("-d","--download-frida",action="store_true",help="Check this option for auto downloading frida-server from repo")
        parser.add_argument("-fv","--frida-version",action="store_true",help="Set frida-server version to use as default")
        parser.add_argument("-P","--frida-path-device",default="/data/local/tmp/",help="Set frida-server path on selected device [Default /data/local/tmp/]")
        parser.add_argument("-i","--frida-exec-path",default="./bin/frida-server",help="Set frida-server executable installation path")
        parser.add_argument("-n","--frida-server-name",default="frida-server",help="Set frida-server executable name on device [Default frida-server]")
        parser.add_argument("-lp","--list-pids",action="store_true",help="Enumerate running processes by PID on selected device")
        parser.add_argument("-la","--list-apps",action="store_true",help="Enumerate installed applications on selected device")
        parser.add_argument("-t","--timeout",default=1000,help="Set USB connect timeout [Default 1000]")
        args = parser.parse_args()

        # download different versions and arch of frida-server
        if args.download_frida:
            frida_server_version = input("[*] Please specifiy the frida-server version to download (blank will get latest)? ")
            frida_server_arch = input("[*] Please specifiy the frida-server architecture [x86,x86_64,arm,arm64]? ")
            if not frida_server_version:
                bin_folder,download_path = get_frida_server_repo(frida_server_arch)
            else:
                bin_folder,download_path = get_frida_server_repo(frida_server_arch,frida_server_version)
            frida_server_default = input("[*] Do you want to set this version as default [y/n]? ")
            if (frida_server_default == 'y') or (frida_server_default == 'Y'):
                frida_server_set_default(download_path,bin_folder)
            else:
                pass

        # change frida-server default version
        if args.frida_version:
            frida_server_versions = frida_server_local_versions()
            frida_server_id = int(input("[*] Please specifiy an ID to set a default frida-server? "))
            frida_server_id = frida_server_versions[frida_server_id]
            frida_server_set_default(os.path.abspath('bin/'+frida_server_id),os.path.abspath('bin'))

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
            logger.error("Could not find any connected devices on your machine")
            exit(1)
        if frida_server_check_existing(selected_device):
            logger.info("Frida-server is running on the selected device!")
        else:
            frida_server_process = frida_server_install(selected_device,args.frida_exec_path,
                                                        args.frida_path_device,args.frida_server_name)
            if frida_server_process:
                logger.info("New frida-server process initiated on PID {0}".format(frida_server_process.pid))
            else:
                logger.error("Frida-server could not be deployed on the selected device!")
                exit(1)
        connected_device = frida.get_device(selected_device, args.timeout)
        if args.list_pids:
            pid_list = frida_enumerate_device(connected_device,'list_pids')
            if pid_list:
                print("-" * 50 + "\n[*] Generated running processes list on selected device\n" + "-" * 50)
                print("Process Name" + " " * 21 + "PID"+"\n"+"-" * 30 + " " + "-" * 7)
                for key, val in enumerate(pid_list):
                    spaces = " " * (33 - len(val.name))
                    print("{0}{1}{2}".format(val.name,spaces,val.pid))
                pid_choice = int(input("\n[*] Please enter PID number: "))
                frida_session = frida_session_activity_handler(connected_device,'pid',pid=pid_choice)
            else:
                logger.error("Could not enumerate processes on the selected device")
                exit(1)
        if args.list_apps:
            apps_list = frida_enumerate_device(connected_device,'list_apps')
            if apps_list:
                print("-" * 50 + "\n[*] Generated installed packages list on selected device\n" + "-" * 50)
                print("Id" + " " * 10    + "Package Name" + " " * 33 + "Package Identifier"+" " * 27 + "PID" + "\n" + "-" * 110)
                for key, val in enumerate(apps_list):
                    if val.pid == 0:
                        package_pid = 'Not running'
                    else:
                        fixed_spaces = 4 * " "
                        package_pid = fixed_spaces + str(val.pid)
                    first_colm_spaces = " " * (4 - len(str(key)))
                    second_colm_spaces = " " * (35 - len(val.name))
                    third_colm_spaces = " " * (50 - len(val.identifier))
                    if val.pid == 0:
                        print("[{0}]{1}|  {2}{3}|  {4}{5}| {6}".format(key,first_colm_spaces,val.name,second_colm_spaces,
                                                                val.identifier,third_colm_spaces,package_pid))
                    else:
                        print(colored("[{0}]{1}|  {2}{3}|  {4}{5}| {6}".format(key,first_colm_spaces,val.name,
                                                                        second_colm_spaces,val.identifier,third_colm_spaces,package_pid),"green"))
                app_choice = int(input("\n[*] Please enter an id: "))
                app_choice = apps_list[app_choice].identifier
                while True:
                    user_activity_choice = input("\n[?] What do you want to spawn or attach [S/A]? ")
                    if (user_activity_choice == 'S') or (user_activity_choice == 's'):
                        frida_session = frida_session_activity_handler(connected_device,'spawn',spawn=app_choice)
                        break
                    elif (user_activity_choice == 'A') or (user_activity_choice == 'a'):
                        frida_session = frida_session_activity_handler(connected_device,'attach',attach=app_choice)
                        break
                    else:
                        logger.error("Please choose between A (Attach) or S (Spawn)")
            else:
                logger.error("Could not enumerate installed packages on the selected device")
                exit(1)
        # spawn a new process instance and attach
        elif args.spawn:
            frida_session = frida_session_activity_handler(connected_device,'spawn',spawn=args.spawn)
        # attach frida to existing running pid
        elif args.pid:
            frida_session = frida_session_activity_handler(connected_device,'pid',pid=args.pid)
        elif args.attach:
            frida_session = frida_session_activity_handler(connected_device,'attach',attach=args.attach)                
        else:
            logger.warning("You must specify atleast one option to run the application\n[*] Please use --help for full reference")
        # set timeout so java.perform will not crash
        sleep(1)

        # load hooking script
        hooking_script = frida_session.create_script(read_hooking_script(args.script))
        if hooking_script:
            hooking_script.on('message', on_message)
            hooking_script.load()
        else:
            logger.error("The specified script '{0}' was not found!".format(args.script))
        
        # stop python script from terminating
        input('Press any key to continue...')

    except (IOError,OSError) as e:
        logger.error("The path to the script file that you specified does not existed: \"{0}\"".format(e.filename))
    except IndexError as e:
        logger.error("You have chosen an unknown ID number of a device")
    except Exception as e:
        logger.error("Something went wrong, please check your input.\n Error - {0}".format(e))