# Interface defining a Database Manager.
from ..pull_request import PullRequest

class DBManager:

    def __init__(self):
        self.isConnected = False

    # Tries to connect to a db, throws an error if not possible
    def connect(self):
        raise NotImplementedError

    # Closes the connection to the db
    def close(self):
        raise NotImplementedError

    # Returns the last Pull Request from the db
    def get_last_pull_request(self) -> PullRequest:
        raise NotImplementedError
