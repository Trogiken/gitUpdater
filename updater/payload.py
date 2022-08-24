from zipfile import ZipFile
from time import sleep
import shutil
import pickle
import stat
import os


class Payload:
    def __init__(self):
        self.env_file = os.path.join(os.path.dirname(__file__), 'env.pkl')
        self.env = self.load_values(self.env_file)

    @staticmethod
    def load_values(path: str):
        """Read and remove environment file"""
        if os.path.exists(path):
            with open(path, 'rb') as file:
                data = pickle.load(file)
            os.remove(path)
            return data

    @staticmethod
    def reset_perms(path: str):
        """Give read, write and execute perms to every file and directory in and including 'path'"""
        for root, dirs, filenames in os.walk(path):
            os.chmod(root, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            for filename in filenames:
                os.chmod(os.path.join(root, filename), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    @staticmethod
    def set_whitelist(files: list, dirs: list):
        """Set read-only perms to whitelisted dirs and files"""
        if dirs:
            for directory in dirs:
                for root, dirs, filenames in os.walk(directory):
                    os.chmod(root, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                    for filename in filenames:
                        os.chmod(os.path.join(root, filename), stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        if files:
            for file in files:
                os.chmod(file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    def main(self):
        self.reset_perms(self.env['install_path'])
        self.set_whitelist(self.env['whitelist']['files'], self.env['whitelist']['dirs'])

        # Clear install directory of non-whitelisted files and dirs
        for root, dirs, files in os.walk(self.env['install_path'], topdown=False):
            if not root.startswith(os.path.abspath(self.env['module_directory'])+os.sep) and root != self.env['module_directory']:  # if current dir is of module
                for file in files:  # delete files
                    try:
                        os.remove(os.path.join(root, file))
                        files.remove(file)
                    except PermissionError:
                        continue
                if not files:
                    for path in dirs:  # delete empty dirs
                        if path != self.env['install_path']:  # dont delete install path
                            try:
                                os.removedirs(os.path.join(root, path))
                                dirs.remove(path)
                            except PermissionError:
                                continue
            else:
                dirs[:] = []
                files[:] = []

        self.reset_perms(self.env['install_path'])

        # Unpack download
        with ZipFile(self.env['zip_path'], 'r') as file:
            file.extractall(self.env['download_directory'])

        # Move files to install location
        download_files = os.listdir(self.env['download_directory'])
        data_folder = ''
        for file in download_files:
            if '.' not in file:
                data_folder = os.path.join(self.env['download_directory'], file)
                break
        if not data_folder:
            raise FileNotFoundError("Unable to located unzipped folder")
        file_names = os.listdir(data_folder)
        for file_name in file_names:
            try:
                shutil.move(os.path.join(data_folder, file_name), self.env['install_path'])
            except shutil.Error:  # already exists, keep original
                continue

        # Cleanup
        shutil.rmtree(self.env['working_directory'])
        os.remove(self.env_file)

        # start file
        if os.path.exists(self.env['startup_path']):
            os.system(f"python {self.env['startup_path']}")
        else:
            raise FileNotFoundError("Startup file cannot be found")


if __name__ == '__main__':
    sleep(3)
    payload = Payload()
    try:
        payload.main()
    except Exception as err:
        log_file = os.path.join(payload.env['working_directory'], 'error.log')
        if os.path.exists(log_file):
            os.remove(log_file)
        with open(os.path.join(payload.env['working_directory'], 'error.log'), 'w') as e:
            e.write(str(err))
