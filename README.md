# Frida-Python-Binding
Easy to use Frida python binding script for Android reversing automation.
The idea behind the script was to make frida's binding much easier and quicker, as of:
1. Enumerate every connected device (usb/remote/local) to your machine and generate a selection menu. 
2. Automatically install frida agent on a selected device with changeable arguments (dir location, execution path etc). inside the `bin` folder I have placed a `frida-server` v1.7.3 for android x86, make sure to use the same version on your client or just replace the file with your current version, in other cases you can use the `--frida-exec-path` argument to specify a different path for your `frida-server` binary.
3. The script is able to enumerate running processes(`--list-pids`)/installed packages(`--list-apps`) and generate a selection menu for the user.

### Demo

![app-demo](https://i.imgur.com/SyNcaix.gif)

### Usage
Use the `--help` argument to get the full arguments list
```
usage: pythonBinding.py [-h] [-s SPAWN] [-p PID] [-a ATTACH] [-S SCRIPT]
                        [-P FRIDA_PATH_DEVICE] [-i FRIDA_EXEC_PATH]
                        [-n FRIDA_SERVER_NAME] [-lp] [-la] [-t TIMEOUT]

Frida RE Easy Python Binding

optional arguments:
  -h, --help            show this help message and exit
  -s SPAWN, --spawn SPAWN
                        Set package name to spawning a new process
  -p PID, --pid PID     Specify a PID number
  -a ATTACH, --attach ATTACH
                        Set a process name to attach
  -S SCRIPT, --script SCRIPT
                        Specify a Javascript hooking script name
  -P FRIDA_PATH_DEVICE, --frida-path-device FRIDA_PATH_DEVICE
                        Set frida-server path on selected device [Default
                        /data/local/tmp/]
  -i FRIDA_EXEC_PATH, --frida-exec-path FRIDA_EXEC_PATH
                        Set frida-server executable installation path
  -n FRIDA_SERVER_NAME, --frida-server-name FRIDA_SERVER_NAME
                        Set frida-server executable name on device [Default
                        frida-server]
  -lp, --list-pids      Enumerate running processes by PID on selected device
  -la, --list-apps      Enumerate installed applications on selected device
  -t TIMEOUT, --timeout TIMEOUT
                        Set USB connect timeout [Default 1000]
```

### How-to install
  * Make sure to use `Python 3.x`.
  * Install `adb` via Android SDK and check that the environment variables are set correctly.
  * Install the dependecies by running:  
    `pip install -r requirements.txt`