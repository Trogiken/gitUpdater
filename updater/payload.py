from time import sleep
import pickle
import os


class Payload:
    def __init__(self):
        self.working_dir = os.path.dirname(__file__)
        self.env_file = os.path.join(self.working_dir, 'env.pkl')

        self.blacklist = list
        self.install_path = str
        self.startup_path = str

    def load_values(self):
        """Read env file and update attribute variables"""
        if os.path.exists(self.env_file):
            with open(self.env_file, 'rb') as file:
                data = pickle.load(file)
                self.blacklist = data['blacklist']
                self.install_path = data['install_path']
                self.startup_path = data['startup_path']

    def main(self):
        self.load_values()

        print(self.blacklist, self.install_path, self.startup_path, sep=', ')


if __name__ == '__main__':
    sleep(3)
    payload = Payload()
    try:
        Payload().main()
    except Exception as err:
        log_file = os.path.join(payload.working_dir, 'error.log')
        if os.path.exists(log_file):
            os.remove(log_file)
        with open(os.path.join(payload.working_dir, 'error.log'), 'w') as f:
            f.write(str(err))
