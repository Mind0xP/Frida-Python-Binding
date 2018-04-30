import frida
import logging

# set logger for module
logger = logging.getLogger(__name__)


class Device(object):

    def __init__(self):
        """Return a Device object with devices list and user's selected option"""

        self.devices_list = None
        self.timeout = 1000
        self.device_id = None
        self.connected_device = None
    
    def enumerate_connected_devices(self):
        """Enumerates each connected device to the machine (local/tether/remote)
            and returns devices list
        
        Returns:
            list -- devices list
        """

        self.devices_list = frida.enumerate_devices()

        def create_devices_menu(self):
            """Creates a device list menu and returns a devices list
            
            Returns:
                list -- available connected devices to the machine
            """

            print("-" * 8 + " Connected Devices List " + "-" * 8 + "\n")
            print(" Id  |" + "   Type " +"  " +"|" + " " * 7 + "IP Address" + " " * 8 + "|"+" " *10 + "Name")
            print("-" * 5 + "+" + "-" * 10 + "+" + "-" * 25 + "+" + "-" * 28 )
            for index, value in enumerate(self):
                print("[{0}]  |  {1}  |   {2}  | {3}".format(index,value.type,value.id,value.name))
                print("-" * 70)
            return self

        if len([x for x in self.devices_list if len(x.id) > 5]) != 0:
            return create_devices_menu([x for x in self.devices_list if len(x.id) > 5])
        else:
            return

    def select_device(self):
            """Asks for user's device choice and return its id
            
            Returns:
                str -- device serial number
            """

            retry_count = 0
            while True:
                user_id_selection = int(input("[*] Please specify a device ID number: "))
                if user_id_selection <= len(self.devices_list) - 1:
                    break
                elif user_id_selection > len(self.devices_list) - 1:
                    print("[*] The selected ID was not found !")
                    retry_count += 1
                if retry_count > 2 :
                    return
            print("-" * 49)
            logger.info("Connecting to device id -> " + self.devices_list[user_id_selection].id)

            return self.devices_list[user_id_selection].id

    def connect_to_device(self, device_id, timeout=1000):
        """Connects to selected device_id and returns frida core object
        
        Arguments:
            device_id {str} -- device serial number
        
        Returns:
            Object -- Frida core object
        """
        self.timeout = timeout
        self.device_id = device_id
        self.connected_device = frida.get_device(self.device_id, self.timeout)
        if self.connected_device:
            logger.info("Connected !")

        return self.connected_device
