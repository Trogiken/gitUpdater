from time import sleep
# import shutil
import pickle
import os


class Payload:
    def __init__(self):
        self.env_file = os.path.join(os.path.dirname(__file__), 'env.pkl')
        self.env = self.load_values(self.env_file)

    @staticmethod
    def load_values(path):
        """Read and remove environment file"""
        if os.path.exists(path):
            with open(path, 'rb') as file:
                data = pickle.load(file)
            os.remove(path)
            return data

    def main(self):
        print('*' * 20)
        print(f"Working Directory: {self.env['working_directory']}")
        print(f"Install: {self.env['install_path']}")
        print(f"Startup: {self.env['startup_path']}")
        print(f"Whitelist Files: {self.env['whitelist']['files']}")
        print(f"Whitelist Dirs: {self.env['whitelist']['dirs']}")
        print('*' * 20)
        print()

        del_files = []
        del_dirs = []
        for current, dirs, files in os.walk(self.env['install_path']):
            if current not in self.env['whitelist']['dirs']:
                del_dirs.append(current)
                for f in files:
                    if os.path.join(current, f) not in self.env['whitelist']['files']:
                        del_files.append(os.path.join(current, f))

        print(del_files)
        print(del_dirs)

        # upack zip
        # move contents of folder to install location
        # start the startup file


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
