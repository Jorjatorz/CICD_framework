from .db_managers.db_manager import DBManager

# Returns the last pull request from the DB
def get_last_pull_request(db_manager):
    # Try to connect to the DB if we are not already connected
    if not db_manager.isConnected:
        db_manager.connect()
        if not db_manager.isConnected:
            return None

    # Get the last PR
    pr = db_manager.get_last_pull_request()

    return pr