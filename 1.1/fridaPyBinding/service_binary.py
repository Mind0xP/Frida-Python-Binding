import logging
from os import makedirs, remove, path, listdir
from shutil import copyfile
from lzma import open as open_zx
from requests import get
from re import findall
from tqdm import tqdm
import math

# set logger for module
logger = logging.getLogger(__name__)


class ServiceBinHandler(object):
    """
    Object which handles frida service binaries
    """

    def __init__(self, arch, version='latest', default=False, frida_server_bin_folder='bin/'):
        """
        Handles frida-server binaries versions
        :param arch: x86/x86_64/arm/arm64
        :param version: specify for specific version
        :param frida_server_bin_folder: set path for frida-server binaries
        """

        self.frida_server_arch = arch
        self.frida_server_version = version
        self.frida_server_bin_folder = frida_server_bin_folder
        self.frida_server_filename = None
        self.frida_server_download_folder = None
        self.frida_server_file_path = None
        self.frida_server_default = default

    def get_frida_server_repo(self):
        """
        Downloads frida-server by given arch/version
        :return: frida-server bin path
        """
        base_url = 'https://github.com/frida/frida/releases'
        if self.frida_server_version == 'latest' or self.frida_server_version == '':
            url = base_url
        else:
            url = base_url + '/tag/' + self.frida_server_version
        res = get(url)
        frida_server_path = findall(r'\/download\/\d+\.\d+\.\d+\/frida\-server\-\d+\.\d+\.\d+\-android\-'
                                    + self.frida_server_arch + '\.xz', res.text)
        download_url = base_url + frida_server_path[0]
        # set url by given arguments, set stream so we can track on download progress
        res = get(download_url, stream=True)
        self.frida_server_filename = frida_server_path[0].split("/")[-1]
        # check if folder already exists
        self.frida_server_bin_folder = path.abspath(self.frida_server_bin_folder)
        self.frida_server_file_path = path.abspath('bin/'+self.frida_server_filename)
        self.frida_server_download_folder = self.frida_server_file_path[:-3]
        if self.check_frida_server_version_local():
            logger.info("The requested version \'{0}\' is already located locally"
                        .format(self.frida_server_filename[:-3]))
            return
        else:
            # set file size, block size and data progress init
            total_file_size = int(res.headers.get('content-length', 0))
            block_size = 1024
            data_wrote = 0
            # download & write file locally
            with open(self.frida_server_file_path, "wb") as f:
                for data in tqdm(res.iter_content(chunk_size=block_size),
                                 total=total_file_size/block_size, unit='KB',
                                 unit_scale=True,
                                 desc='File Download'):
                    data_wrote += len(data)
                    f.write(data)
            if total_file_size != 0 and data_wrote != total_file_size:
                raise 'Something went wrong with the download process'
                return
            else:
                logger.info("The requested file \'{0}\' was successfully downloaded".format(self.frida_server_filename))
                return self.extract_frida_server_comp()

    def extract_frida_server_comp(self):
        """
        Decompress frida-server XZ file into executable binary
        :return:
        """
        frida_server_extract_dir = self.frida_server_file_path[:-3]
        makedirs(frida_server_extract_dir)
        with open_zx(self.frida_server_file_path, 'rb') as f:
            decompressed_file = f.read()
        with open(frida_server_extract_dir + '/frida-server', 'wb') as f:
            f.write(decompressed_file)
            logger.info("Extracted frida-server under - {0}".format(frida_server_extract_dir))
        # delete compressed file
        remove(self.frida_server_file_path)
        if self.frida_server_default:
            return self.frida_server_set_default()
        else:
            return

    def check_frida_server_version_local(self):
        """
        Check if the specified frida-server folder already exist
        :return: True/None
        """
        if path.exists(self.frida_server_download_folder):
            return True
        else:
            return

    def frida_server_set_default(self):
        """
        Sets frida-server specified version to default under /bin folder
        :return: True/None
        """
        frida_server_exec_src = self.frida_server_download_folder + '/frida-server'
        frida_server_exec_dst = self.frida_server_bin_folder + '/frida-server'
        self.frida_server_default = copyfile(frida_server_exec_src, frida_server_exec_dst)
        if self.frida_server_default:
            return self.frida_server_default
        else:
            return None

    def frida_server_local_versions(self):
        dir_list = listdir(self.frida_server_bin_folder)
        frida_server_local_versions = [x for x in dir_list if x.find('.') > -1]
        print(" Id  |" + "   Arch " + "  " + "|" + " " * 3 + "Version")
        print("-" * 5 + "+" + "-" * 10 + "+" + "-" * 12)
        for k, v in enumerate(frida_server_local_versions):
            _version = v.split("-")
            print("[{0}]  |   {1}    |   {2}    ".format(k, _version[4], _version[2]))
        print("-" * 29)
        return frida_server_local_versions





