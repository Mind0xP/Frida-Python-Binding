
# read script file from local FS
def read_hooking_script(filename):
        with open(filename, 'r') as raw:
            try:
                return raw.read()
            except (IOError,OSError):
                return None

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)