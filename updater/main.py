from packaging import version
import requests


class _Repo:
    """Gather github repository information"""
    def __init__(self, username: str, repository: str, token: str):
        self.user = username
        self.repo = repository
        self.token = token
        self.repo_url = f"https://api.github.com/repos/{self.user}/{self.repo}"

        self.session = requests.Session()
        self.auth_header = {"Authorization": f"token {self.token}"}

    def fetch(self, url) -> dict:
        """Return all repository information"""
        status = None
        message = 'Unknown'
        try:
            resp = self.session.get(url, headers=self.auth_header if self.token is not None else None)
            if not resp.ok:
                status = False
                message = f"Failed to get '{self.repo_url}'. Reason: '{resp.reason}' (Private repos require tokens)"
            else:
                status = True
                message = resp.json()
        except requests.exceptions.ConnectionError:
            status = False
            message = 'Failed to make connection'

        return {'ok': status, 'msg': message}

    def get(self, param: str) -> fetch:
        """Return specific repository url information"""
        return self.fetch(f'{self.repo_url}/{param}')


class Update(_Repo):
    """
    Main package class

    Attributes
    ----------
    username:
        github username
    repository:
        repository name
    token (optional):
        github personal access token
    """
    def __init__(self, username: str, repository: str, token: str = None):
        super().__init__(username, repository, token)

    def check(self, current):

        response = self.get('tags')
        if not response['ok']:
            raise Exception(f"Error: {response['msg']}")
        else:
            tag_data = response['msg']

        versions = []
        for tag in tag_data:
            v = tag['name'].lower()
            v = v if v[0] != 'v' else v[:0] + v[0+1:]  # remove common 'v' from version if exists at index 0
            versions.append(v)
        versions.sort(key=version.Version)  # versions in ascending order

        if version.parse(versions[-1]) > version.parse(current):
            return True
        else:
            return False

    def download(self):
        pass

    def install(self):
        pass
