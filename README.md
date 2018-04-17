# Frida-Python-Binding
Easy to use Frida python binding script for Android reversing automation.

# Demo

![app-demo](https://i.imgur.com/SyNcaix.gif)

# Usage
Use the --help argument to get full 
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

# How-to install
..* Make sure to use Python 3.x to run the script.  
..* install the dependecies by running:  
    `pip install -r requirements.txt`