from packaging import version
import tempfile
import requests
import os


class _Repo:
    """Gather GitHub repository information"""
    def __init__(self, username: str, repository: str, token: str):
        self.user = username
        self.repo = repository
        self.token = token
        self.repo_url = f"https://api.github.com/repos/{self.user}/{self.repo}"

        self.session = requests.Session()
        self.auth_header = {"Authorization": f"token {self.token}"}

    def fetch(self, url) -> requests.models.Response:
        """Get and return requested api data"""
        try:
            resp = self.session.get(url, headers=self.auth_header if self.token is not None else None)
            if not resp.ok:
                raise LookupError(f"Failed to get '{url}'. Reason: '{resp.reason}' "
                                  f"{'(Is this a private repo? Token Needed)' if resp.reason == 'Not Found' else None}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to make connection!")

        return resp

    def get_tags(self) -> list:
        """List tag names"""
        tags_data = self.fetch(f'{self.repo_url}/tags').json()
        return [tag['name'] for tag in tags_data]

    def get_versions(self) -> list:
        """List versions in ascending order"""
        tags = self.get_tags()

        versions = []
        for tag in tags:
            t_filter = tag.lower()
            t_filter = t_filter if t_filter[0] != 'v' else t_filter[1:]  # remove 'v' from version if exists at index 0
            versions.append(t_filter)
        versions.sort(key=version.Version)  # ascend order

        return versions

    def download(self, path: str, tag: str):
        url = f'{self.repo_url}/zipball/refs/tags/{tag}'
        resp = self.fetch(url).content
        open(path, "wb").write(resp)


class _Disk:
    """Manage disk"""
    def __init__(self, install_path, startup_path):
        self.install = install_path
        self.startup = startup_path

    def backup(self):
        """Backup all files in the install_path"""
        pass


class Update(_Repo):
    """
    Main package class

    Attributes
    ----------
    username:
        GitHub username
    repository:
        repository name
    token (optional):
        GitHub personal access token
    """
    def __init__(self, username: str, repository: str, token: str = None):
        super().__init__(username, repository, token)

    def check(self, current: str) -> dict:
        """Check if current version is less than latest"""
        versions = self.get_versions()
        latest = versions[-1]

        if version.parse(latest) > version.parse(current):
            status = True
        else:
            status = False

        return {'update': status, 'latest': latest, 'versions': versions}

    def run(self, install_path: str, startup_path: str, close: bool = False, backup: bool = False) -> bool:
        """Download latest version, clone/start payload, kill import program (optional)"""
        for path in [install_path, startup_path]:
            if os.path.exists(path):
                if not os.path.isdir(path):
                    raise NotADirectoryError(f"'{path}' must be a directory")
            else:
                raise FileNotFoundError(f"'{path}' does not exist")

        # file_location = (os.path.dirname(__file__))
        # os.mkdir(file_location)
        # self.download(os.path.join(file_location, 'download'), tag=)

        if close:
            # close program
            pass
        else:
            return True
