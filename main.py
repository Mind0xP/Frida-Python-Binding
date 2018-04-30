# import frida
# import os
import logging
# import subprocess
# import requests
# import lzma
# import re
# from shutil import copyfile
# from termcolor import colored
from argparse import ArgumentParser
from time import sleep
from sys import exit
from colorlog import ColoredFormatter
from fridaPyBinding import device
from fridaPyBinding import service_handler
from fridaPyBinding import service_binary
from fridaPyBinding import session_handler


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    color_formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)-4s]%(reset)s - %(message)s",
        datefmt='%d-%m-%y %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={},
        style='%')
    logging_handler = logging.StreamHandler()
    logging_handler.setFormatter(color_formatter)
    logger.addHandler(logging_handler)

# setup logging for runtime
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    try:
        # define application argument parser
        parser = ArgumentParser(description="Frida RE Easy Python Binding")
        parser.add_argument("-s", "--spawn",
                            help="Set package name to spawning a new process")
        parser.add_argument("-p", "--pid",
                            help="Specify a PID number")
        parser.add_argument("-a", "--attach",
                            help="Set a process name to attach")
        parser.add_argument("-S", "--script",
                            help="Specify a Javascript hooking script name")
        parser.add_argument("-d", "--download-frida",
                            action="store_true",
                            help="Check this option for auto downloading frida-server from repo")
        parser.add_argument("-fv", "--frida-version",
                            action="store_true",
                            help="Set frida-server version to use as default")
        parser.add_argument("-P", "--frida-path-device",
                            default="/data/local/tmp/",
                            help="Set frida-server path on selected device [Default /data/local/tmp/]")
        parser.add_argument("-i", "--frida-exec-path",
                            default="./bin/frida-server",
                            help="Set frida-server executable installation path")
        parser.add_argument("-n", "--frida-server-name",
                            default="frida-server",
                            help="Set frida-server executable name on device [Default frida-server]")
        parser.add_argument("-lp", "--list-pids",
                            action="store_true",
                            help="Enumerate running processes by PID on selected device")
        parser.add_argument("-la", "--list-apps",
                            action="store_true",
                            help="Enumerate installed applications on selected device")
        parser.add_argument("-t", "--timeout",
                            default=1000,
                            help="Set USB connect timeout [Default 1000]")
        args = parser.parse_args()

        if args.download_frida:
            frida_server_version = input("[*] Please specify the frida-server version to download (blank will get"
                                         " latest)? ")
            frida_server_arch = input("[*] Please specify the frida-server architecture [x86,x86_64,arm,arm64]? ")
            frida_server_default = input("[*] Do you want to set this version as default [y/n]? ")
            if (frida_server_default == 'y') or (frida_server_default == 'Y'):
                frida_server_default = True
                logger.info("The chosen frida-server version was set to default!")
            get_frida = service_binary.ServiceBinHandler(frida_server_arch, version=frida_server_version,
                                                         default=frida_server_default)
            get_frida.get_frida_server_repo()
    except (IOError, OSError) as e:
        logger.error("The path to the script file that you specified does not existed: \"{0}\"".format(e.filename))
    except IndexError as e:
        logger.error("You have chosen an unknown ID number of a device")
    except Exception as e:
        logger.error("Something went wrong, please check your input.\n Error - {0}".format(e))

        # device = device.Device()
        # device.devices_list = device.enumerate_connected_devices()
        # if not device.devices_list:
        #     logger.error("Could not find any connected devices on your machine")
        #     exit(1)
        # device.connect_to_device(device.select_device(), 1000)  # args.timeout
        # # creation of ServiceHandler object to implement frida service
        # frida_srv_handler = service_handler.ServiceHandler(device.device_id, "./bin/frida-server")
        # frida_srv_handler.frida_server_install()
        #
        #
        #
        # frida_session = session_handler.SessionHandler(device.connected_device)
        # sleep(1)
        # # if args.attach
        # frida_session.spawn('com.android.calendar')
        # # if args.spawn
        # # if args.



    # try:
    #     # define application argument parser
    #     parser = ArgumentParser(description="Frida RE Easy Python Binding")
    #     parser.add_argument("-s","--spawn",help="Set package name to spawning a new process")
    #     parser.add_argument("-p","--pid",help="Specify a PID number")
    #     parser.add_argument("-a","--attach",help="Set a process name to attach")
    #     parser.add_argument("-S","--script",help="Specify a Javascript hooking script name")
    #     parser.add_argument("-d","--download-frida",action="store_true",help="Check this option for auto downloading frida-server from repo")
    #     parser.add_argument("-fv","--frida-version",action="store_true",help="Set frida-server version to use as default")
    #     parser.add_argument("-P","--frida-path-device",default="/data/local/tmp/",help="Set frida-server path on selected device [Default /data/local/tmp/]")
    #     parser.add_argument("-i","--frida-exec-path",default="./bin/frida-server",help="Set frida-server executable installation path")
    #     parser.add_argument("-n","--frida-server-name",default="frida-server",help="Set frida-server executable name on device [Default frida-server]")
    #     parser.add_argument("-lp","--list-pids",action="store_true",help="Enumerate running processes by PID on selected device")
    #     parser.add_argument("-la","--list-apps",action="store_true",help="Enumerate installed applications on selected device")
    #     parser.add_argument("-t","--timeout",default=1000,help="Set USB connect timeout [Default 1000]")
    #     args = parser.parse_args()

    # # download different versions and arch of frida-server
    # if args.download_frida:
    #     frida_server_version = input("[*] Please specifiy the frida-server version to download (blank will get latest)? ")
    #     frida_server_arch = input("[*] Please specifiy the frida-server architecture [x86,x86_64,arm,arm64]? ")
    #     if not frida_server_version:
    #         bin_folder,download_path = get_frida_server_repo(frida_server_arch)
    #     else:
    #         bin_folder,download_path = get_frida_server_repo(frida_server_arch,frida_server_version)
    #     frida_server_default = input("[*] Do you want to set this version as default [y/n]? ")
    #     if (frida_server_default == 'y') or (frida_server_default == 'Y'):
    #         frida_server_set_default(download_path,bin_folder)
    #     else:
    #         pass

    #     # change frida-server default version
    #     if args.frida_version:
    #         frida_server_versions = frida_server_local_versions()
    #         frida_server_id = int(input("[*] Please specifiy an ID to set a default frida-server? "))
    #         frida_server_id = frida_server_versions[frida_server_id]
    #         frida_server_set_default(os.path.abspath('bin/'+frida_server_id),os.path.abspath('bin'))

    #     if not args.script:
    #         while True:
    #             args.script = input("Please type your script path: ")
    #             script_exists = os.path.isfile(args.script)
    #             if script_exists:
    #                 break
    #             else:
    #                 logger.error("The file you specified does not exists.")

    #     logger.info("Enumerating connected devices\n")
    #     # enumerate connected devices
    #     devices = enumerate_connected_devices()
    #     if devices:
    #         selected_device = select_device(devices)
    #     else:
    #         logger.error("Could not find any connected devices on your machine")
    #         exit(1)
    #     if frida_server_check_existing(selected_device):
    #         logger.info("Frida-server is running on the selected device!")
    #     else:
    #         frida_server_process = frida_server_install(selected_device,args.frida_exec_path,
    #                                                     args.frida_path_device,args.frida_server_name)
    #         if frida_server_process:
    #             logger.info("New frida-server process initiated on PID {0}".format(frida_server_process.pid))
    #         else:
    #             logger.error("Frida-server could not be deployed on the selected device!")
    #             exit(1)
    #     connected_device = frida.get_device(selected_device, args.timeout)
    #     if args.list_pids:
    #         pid_list = frida_enumerate_device(connected_device,'list_pids')
    #         if pid_list:
    #             print("-" * 50 + "\n[*] Generated running processes list on selected device\n" + "-" * 50)
    #             print("Process Name" + " " * 21 + "PID"+"\n"+"-" * 30 + " " + "-" * 7)
    #             for key, val in enumerate(pid_list):
    #                 spaces = " " * (33 - len(val.name))
    #                 print("{0}{1}{2}".format(val.name,spaces,val.pid))
    #             pid_choice = int(input("\n[*] Please enter PID number: "))
    #             frida_session = frida_session_activity_handler(connected_device,'pid',pid=pid_choice)
    #         else:
    #             logger.error("Could not enumerate processes on the selected device")
    #             exit(1)
    #     if args.list_apps:
    #         apps_list = frida_enumerate_device(connected_device,'list_apps')
    #         if apps_list:
    #             print("-" * 50 + "\n[*] Generated installed packages list on selected device\n" + "-" * 50)
    #             print("Id" + " " * 10    + "Package Name" + " " * 33 + "Package Identifier"+" " * 27 + "PID" + "\n" + "-" * 110)
    #             for key, val in enumerate(apps_list):
    #                 if val.pid == 0:
    #                     package_pid = 'Not running'
    #                 else:
    #                     fixed_spaces = 4 * " "
    #                     package_pid = fixed_spaces + str(val.pid)
    #                 first_colm_spaces = " " * (4 - len(str(key)))
    #                 second_colm_spaces = " " * (35 - len(val.name))
    #                 third_colm_spaces = " " * (50 - len(val.identifier))
    #                 if val.pid == 0:
    #                     print("[{0}]{1}|  {2}{3}|  {4}{5}| {6}".format(key,first_colm_spaces,val.name,second_colm_spaces,
    #                                                             val.identifier,third_colm_spaces,package_pid))
    #                 else:
    #                     print(colored("[{0}]{1}|  {2}{3}|  {4}{5}| {6}".format(key,first_colm_spaces,val.name,
    #                                                                     second_colm_spaces,val.identifier,third_colm_spaces,package_pid),"green"))
    #             app_choice = int(input("\n[*] Please enter an id: "))
    #             app_choice = apps_list[app_choice].identifier
    #             while True:
    #                 user_activity_choice = input("\n[?] What do you want to spawn or attach [S/A]? ")
    #                 if (user_activity_choice == 'S') or (user_activity_choice == 's'):
    #                     frida_session = frida_session_activity_handler(connected_device,'spawn',spawn=app_choice)
    #                     break
    #                 elif (user_activity_choice == 'A') or (user_activity_choice == 'a'):
    #                     frida_session = frida_session_activity_handler(connected_device,'attach',attach=app_choice)
    #                     break
    #                 else:
    #                     logger.error("Please choose between A (Attach) or S (Spawn)")
    #         else:
    #             logger.error("Could not enumerate installed packages on the selected device")
    #             exit(1)
    #     # spawn a new process instance and attach
    #     elif args.spawn:
    #         frida_session = frida_session_activity_handler(connected_device,'spawn',spawn=args.spawn)
    #     # attach frida to existing running pid
    #     elif args.pid:
    #         frida_session = frida_session_activity_handler(connected_device,'pid',pid=args.pid)
    #     elif args.attach:
    #         frida_session = frida_session_activity_handler(connected_device,'attach',attach=args.attach)                
    #     else:
    #         logger.warning("You must specify atleast one option to run the application\n[*] Please use --help for full reference")
    #     # set timeout so java.perform will not crash
    #     sleep(1)

    #     # load hooking script
    #     hooking_script = frida_session.create_script(read_hooking_script(args.script))
    #     if hooking_script:
    #         hooking_script.on('message', on_message)
    #         hooking_script.load()
    #     else:
    #         logger.error("The specified script '{0}' was not found!".format(args.script))

    #     # stop python script from terminating
    #     input('Press any key to continue...')

    # except (IOError,OSError) as e:
    #     logger.error("The path to the script file that you specified does not existed: \"{0}\"".format(e.filename))
    # except IndexError as e:
    #     logger.error("You have chosen an unknown ID number of a device")
    # except Exception as e:
    #     logger.error("Something went wrong, please check your input.\n Error - {0}".format(e))