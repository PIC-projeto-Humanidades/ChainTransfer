import uuid

def save_log(file_id=None, message=""):
    from modules.database import log_action
    if file_id is None:
        file_id = str(uuid.uuid4())
    log_action(file_id, message)