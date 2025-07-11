# routines/__init__.py
from services.routines.observer_and_transfer import routine, observe_and_rename
import threading

def start_routines():
    threading.Thread(target=observe_and_rename, daemon=True).start()
    threading.Thread(target=routine, daemon=True).start()
