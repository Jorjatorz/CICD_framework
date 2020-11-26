# Manager for a Postgres DB
import psycopg2

from config import postgres
from ..pull_request import PullRequest
from .db_manager import DBManager

class PGManager(DBManager):
    def __init__(self):
        super().__init__()
        self._conn = None # DB Connector

    # Tries to connect to a db, throws an error if not possible
    def connect(self):
        if self._conn is None:
            try:
                self._conn = psycopg2.connect(host=postgres["host"], database=postgres["database"], user=postgres["user"], password=postgres["password"])
                self.isConnected = True
            except Exception as e:
                print("An error ocurred while connecting to the Postgres DB.")
                print(e)
                self._conn = None

    # Close the DB connection
    def close(self):
        if not self._conn is None:
            self._conn.close()
        self._conn = None
        self.isConnected = False

    # Returns the last Pull Request from the db
    def get_last_pull_request(self) -> PullRequest:
        if self._conn is None:
            print("Error: Can't get the las PR. No connection to a Postgres DB")
            return None
        cur = self._conn.cursor()
        try:
            cur.execute("SELECT merged_at FROM pull_requests where state = 'closed' and merged_at IS NOT NULL ORDER BY merged_at DESC LIMIT 1;")
        except Exception as e:
            print("Error in the SQL query")
            print(e)
            return None
        query = cur.fetchone()
        merge_date = query[0]
        cur.close()

        # Empty query
        if merge_date is None:
            print("The PR query returned empty")
            return None
        pr = PullRequest(merge_date)

        return pr
        