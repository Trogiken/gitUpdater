from packaging import version
import requests


class _Repo:
    """Gather GitHub repository information"""
    def __init__(self, username: str, repository: str, token: str):
        self.user = username
        self.repo = repository
        self.token = token
        self.repo_url = f"https://api.github.com/repos/{self.user}/{self.repo}"

        self.session = requests.Session()
        self.auth_header = {"Authorization": f"token {self.token}"}

    def fetch(self, url) -> dict:
        """Return all repository information"""
        try:
            resp = self.session.get(url, headers=self.auth_header if self.token is not None else None)
            if resp.ok:
                message = resp.json()
            else:
                raise LookupError(f"Failed to get '{url}'. Reason: '{resp.reason}' (Is this a private repo?)")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to make connection!")

        return message

    def get_versions(self) -> list:
        """List tag versions in ascending order"""
        tags_data = self.fetch(f'{self.repo_url}/tags')

        versions = []
        for tag in tags_data:
            v = tag['name'].lower()
            v = v if v[0] != 'v' else v[:0] + v[0+1:]  # remove 'v' from version if exists at index 0
            versions.append(v)
        versions.sort(key=version.Version)  # ascend order

        return versions


class _Disk:
    """Manage disk"""
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

    def check(self, current) -> bool:
        latest = self.get_versions()[-1]

        if version.parse(latest) > version.parse(current):
            return True
        else:
            return False

    def download(self):
        pass

    def install(self):
        pass
