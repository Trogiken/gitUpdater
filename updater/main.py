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
    download(download_path=str, tag=str) -> None:
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
        self._module_dir = os.path.dirname(__file__)
        self._working_dir = os.path.join(self._module_dir, 'temp')
        self._download_dir = os.path.join(self._working_dir, 'down')
        self._download_name = 'data.zip'

        self._current_version = current_version
        self.whitelist = []

    def download(self, download_path: str, tag: str) -> None:
        """Download tag ZipBall"""
        if '.zip' not in download_path:
            raise ValueError("Download path must end in a filename with .zip extension")
        url = f'{self.repo_url}/zipball/refs/tags/{tag}'
        resp = self.fetch(url).content
        open(download_path, "wb").write(resp)

    def check(self) -> dict:
        """Check if current version is less than the latest"""
        versions = self.get_versions()
        latest = versions[-1]

        if version.parse(latest) > version.parse(self._current_version):
            status = True
        else:
            status = False

        return {'update': status, 'latest': latest, 'versions': versions}

    def install(self, install_path: str, startup_path: str, zip_path: str = None, force: bool = False) -> None:
        """Download the latest version and clone and start payload"""
        if not force:
            if not self.check()['update']:
                raise UserWarning("Already Up To Date. (You can use 'force=True' to override this)")

        # Validate parameters
        for path in [install_path, zip_path]:
            if os.path.exists(path):
                if path == install_path:
                    if not os.path.isdir(path):
                        raise NotADirectoryError(f"'{path}' must be a directory")
                else:
                    if '.zip' not in path:
                        raise ValueError(f"'{path}' must end with .zip extension")
            else:
                raise LookupError(f"'{path}' does not exist")

        # Validate and organize whitelist paths
        sorted_whitelist = {'files': [], 'dirs': []}
        for path in self.whitelist:
            if not os.path.exists(path):
                raise FileNotFoundError(f"'{path}' does not not exist")
            if install_path == path:
                raise ValueError(f"Cannot whitelist the install path: '{path}'")
            if not path.startswith(os.path.abspath(install_path)+os.sep):  # if not a sub path of install_path
                raise ValueError(f"'{path}' is not a sub-path of '{install_path}'")

            if os.path.isfile(path):
                sorted_whitelist['files'].append(path)
            if os.path.isdir(path):
                sorted_whitelist['dirs'].append(path)

        # Create directory's
        if os.path.exists(self._working_dir):
            shutil.rmtree(self._working_dir)
        os.mkdir(self._working_dir)
        os.mkdir(self._download_dir)

        if zip_path is None:
            # Download the latest zip tag
            zip_path = os.path.join(self._download_dir, self._download_name)
            self.download(download_path=zip_path, tag=self.get_versions()[-1])

        # Create environment file
        data = {'module_directory': self._module_dir,
                'working_directory': self._working_dir,
                'download_directory': self._download_dir,
                'install_path': install_path,
                'startup_path': startup_path,
                'zip_path': zip_path,
                'whitelist': sorted_whitelist
                }
        with open(os.path.join(self._module_dir, 'env.pkl'), 'wb') as file:
            pickle.dump(data, file)

        # Start payload
        os.system(f"python {os.path.join(self._module_dir, 'payload.py')}")

        # exit code 0
        exit(0)
