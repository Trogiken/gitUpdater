from packaging import version
import requests
import shutil
import pickle
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

    def fetch(self, url: str) -> requests.models.Response:
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
            versions.append(t_filter)
        versions.sort(key=version.Version)  # ascend order

        return versions

    def download(self, path: str, tag: str) -> None:
        """Download tag ZipBall"""
        url = f'{self.repo_url}/zipball/refs/tags/{tag}'
        resp = self.fetch(url).content
        open(path, "wb").write(resp)


class Update(_Repo):
    """
    Main package class

    ...

    Methods
    -------
    check() -> bool:
        Check if current version is less than the latest
    run(install_path=str, startup_path=str, force=bool (optional)):
        Download and install the latest version
    fetch(url=str) -> requests.models.Response:
        Get response url
    get_tags() -> list:
        Return all tag names
    get_versions() -> list:
        List versions in ascending order
    download(path=str, tag=str) -> None:
        Download ZipBall of (tag) and store to (path)

    Attributes
    ----------
    current_version:
        Current program version
    username:
        GitHub username
    repository:
        repository name
    token (optional):
        GitHub personal access token
    """
    def __init__(self, current_version: str, username: str, repository: str, token: str = None):
        super().__init__(username, repository, token)
        self.module_dir = os.path.dirname(__file__)
        self._working_dir = os.path.join(self.module_dir, 'temp')
        self._download_dir = os.path.join(self._working_dir, 'down')

        self.current_version = current_version
        self.whitelist = []

    def check(self) -> dict:
        """Check if current version is less than the latest"""
        versions = self.get_versions()
        latest = versions[-1]

        if version.parse(latest) > version.parse(self.current_version):
            status = True
        else:
            status = False

        return {'update': status, 'latest': latest, 'versions': versions}

    def run(self, install_path: str, startup_path: str, force: bool = False) -> None:
        """Download the latest version and clone and start payload"""
        if not force:
            if not self.check()['update']:
                raise UserWarning("Already Up To Date. (You can use 'force=True' to override this)")

        # Validate parameters
        for path in [install_path, startup_path]:
            if os.path.exists(path):
                if path == install_path:
                    if not os.path.isdir(path):
                        raise NotADirectoryError(f"'{path}' must be a directory")
                else:
                    if not os.path.isfile(path):
                        raise FileNotFoundError(f"'{path}' must be a file'")
            else:
                raise LookupError(f"'{path}' does not exist")

        # Validate and organize whitelist paths
        invalid_paths = []
        sorted_whitelist = {'files': [], 'dirs': []}
        for path in self.whitelist:
            if not os.path.exists(path):
                invalid_paths.append(path)
            if os.path.isfile(path):
                sorted_whitelist['files'].append(path)
            if os.path.isdir(path):
                sorted_whitelist['dirs'].append(path)
        if invalid_paths:
            raise LookupError(f"Invalid Whitelist Path(s): {invalid_paths}")

        # Create directory's
        if os.path.exists(self._working_dir):
            shutil.rmtree(self._working_dir)
        os.mkdir(self._working_dir)
        os.mkdir(self._download_dir)

        # Download the latest zip tag
        self.download(path=os.path.join(self._download_dir, 'data.zip'), tag=self.get_versions()[-1])

        # Create environment file
        data = {'module_directory': self.module_dir,
                'working_directory': self._working_dir,
                'install_path': install_path,
                'startup_path': startup_path,
                'whitelist': sorted_whitelist
                }
        with open(os.path.join(self.module_dir, 'env.pkl'), 'wb') as file:
            pickle.dump(data, file)

        # Start payload
        os.system(f"python {os.path.join(self.module_dir, 'payload.py')}")

        # Close program with exit code 0
        exit(0)
