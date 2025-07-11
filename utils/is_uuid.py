import uuid

def is_uuid(text):
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False