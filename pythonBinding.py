import frida
import argparse
import time
import os
from sys import exit as sysexit
import subprocess

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)

# pause script before termination based on OS type
def pause_command_line():
    if (os.name == "posix"):
        os.system('read -s -n 1 -p "Press any key to continue..."')
        print
        sysexit(0)
    else: 
        os.system('pause')
        sysexit(0)

# start frida-server process
def frida_server_start_process(device_id,frida_server):
    frida_server_subprocess = subprocess.Popen("adb -s "+device_id+" shell "+frida_server+" &", shell=True)
    if (frida_server_subprocess):
        print("[*] New frida-server process initiated on PID {0}".format(frida_server_subprocess.pid))
        return frida_server_subprocess
    else:
        print("[!] Could not create a new frida-server process")
        return

# kill frida-server running process
def frida_server_kill_process(frida_subprocess):
    print("[*] Terminating frida-server process - PID: {0}".format(frida_subprocess.pid))
    frida_subprocess.terminate()

# installing frida-server on android devices
def frida_server_install(device_id, frida_install_path, device_install_path='/data/local/tmp/', frida_server_name="frida-server"):
    print("[*] Installing frida service on device id: " + device_id)
    try:
        frida_server_device_path = device_install_path+frida_server_name
        frida_push_device = subprocess.Popen("adb -s "+device_id+" push \""+frida_install_path+"\" "+
                                            frida_server_device_path, shell=True, stderr=subprocess.STDOUT,
                                            stdout=subprocess.PIPE)
        data, nothing = frida_push_device.communicate()
        data_str = str(data,'utf-8')
        if (data_str.index('pushed.')):
            print("[*] Frida-server was successfully pushed to selected device on "+ device_install_path)
            # set frida-server permissions
            frida_server_perm = subprocess.Popen("adb -s "+device_id+" shell chmod 755 \""+frida_server_device_path+"\"", shell=True,
                                                stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            print("[*] Set frida-server with execution permissions")
            frida_server_perm.wait()
            frida_server_perm.terminate()
        else:
            print("[!] Please check path permissions")
        frida_push_device.terminate()
        return frida_server_start_process(device_id,frida_server_device_path)
    except:
        return "[!] Frida-server was not deployed on the selected device!"

# check if frida-server exists on selected device
def frida_server_check_existing(device_id):
    frida_existing = subprocess.Popen("adb -s "+device_id+" shell \"ps| grep frida-server\"", 
                                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data, nothing = frida_existing.communicate()
    if (len(data) != 0):
        print("[!] Frida-server is already running !")
        frida_existing.terminate()
        return True
    else:
        frida_existing.terminate()
        return False

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
    if( devices[user_id_selection].id == None):
        print("[*] ID Was not found !")
        select_device(devices)
    selected_device = devices[user_id_selection].id
    print("-" * 49)
    print("--> Connecting to device id -> " + selected_device)
    return selected_device

# enumerate local/remote/usb devices and return a list by given type
def enumerate_connected_devices():
    devices = frida.enumerate_devices()
    return create_devices_menu([x for x in devices if len(x.id) > 5])

def frida_session_retry(con_device,con_type,**kwargs):
    for _ in range(5):
        if (con_type == 'spawn'):
            time.sleep(1)
            pid = con_device.spawn([kwargs.get('spawn')])
            if (pid):
                print("[*] Spawned package : {0} on pid {1}".format(kwargs.get('spawn'),pid))
                frida_session = con_device.attach(pid)
                # resume app after spawning
                con_device.resume(pid)
                break
            else:
                print("[!] Could not spawn the requested package, retrying: {0}".format(_))
        # attach frida to existing running pid
        elif (con_type == 'pid'):
            time.sleep(1)
            frida_session = con_device.attach(int(args.pid))
            if (frida_session):
                print("-> Attaching frida session to PID - {0}".format(args.pid))
                break
            else:
                print("[!] Could not attach the requested process, retrying: {0}".format(_))
        elif (con_type == 'attach'):
            time.sleep(1)
            frida_session = con_device.attach(kwargs.get('attach'))
            if (frida_session):
                print("-> Attaching frida session to process name - {0} on PID {1}".format(kwargs.get('attach'),frida_session._impl.pid))
                break
            else:
                print("[!] Could not attach to the requested package, retrying {0}".format(_))
    return frida_session


# read script file from local FS
def read_hooking_script(filename):
    try:
        with open(filename, 'r') as raw:
            return raw.read()
    except IOError:
        print("[!] The specified script '{0}' was not found!".format(filename))
        return None
    

if __name__ == '__main__':
    try:
        # define application argument parser
        parser = argparse.ArgumentParser(description="Frida RE Easy Python Binding")
        parser.add_argument("-s","--spawn",help="Set package name to spawning a new process")
        parser.add_argument("-p","--pid",help="Specify a PID number")
        parser.add_argument("-a","--attach",help="Set a process name to attach")
        parser.add_argument("-S","--script",help="Specify a Javascript hooking script name")
        parser.add_argument("-R","--frida-run",default=True,action="store_true",help="Set for executing frida-server on selected device [Default On]")
        parser.add_argument("-P","--frida-path-device",default="/data/local/tmp/",help="Set frida-server path on selected device [Default /data/local/tmp/]")
        parser.add_argument("-i","--frida-exec-path",help="Set frida-server executable installation path")
        parser.add_argument("-n","--frida-server-name",default="frida-server",help="Set frida-server executable name on device [Default frida-server]")
        parser.add_argument("-t","--timeout",default=1000,help="Set USB connect timeout [Default 1000]")
        args = parser.parse_args()

        print("\n[*] Enumerating connected devices\n")
        # enumerate connected devices
        devices = enumerate_connected_devices()
        selected_device = select_device(devices)
        frida_server_exist = frida_server_check_existing(selected_device)
        if (args.frida_exec_path):
            # check if frida-server is already running
            if (frida_server_exist):
                pass
            else:
                frida_server_process = frida_server_install(selected_device,args.frida_exec_path,
                                                            args.frida_path_device,args.frida_server_name)
        elif (args.frida_run):
            # check if frida-server is already running
            if (frida_server_exist):
                pass
            else:
                frida_server_process = frida_server_start_process(selected_device,args.frida_path_device+args.frida_server_name)
        connected_device = frida.get_device(selected_device, args.timeout)
        # spawn a new process instance and attach
        if (args.spawn):
            frida_session = frida_session_retry(connected_device,'spawn',spawn=args.spawn)
        # attach frida to existing running pid
        elif (args.pid):
            frida_session = frida_session_retry(connected_device,'pid')
        elif (args.attach):
            frida_session = frida_session_retry(connected_device,'attach',attach=args.attach)
        else:
            print("[!] You must specify atleast one option to run the application\n[*] Please use --help for full reference")
        # set timeout so java.perform will not crash
        time.sleep(1)

        # load hooking script
        hooking_script = frida_session.create_script(read_hooking_script(args.script))
        hooking_script.on('message', on_message)
        hooking_script.load()

        # stop python script from terminating
        input()
        # kill frida-server process before exiting
        frida_server_kill_process(frida_server_process)
    except:
        print("\n[!] Something went wrong, please check your input.")