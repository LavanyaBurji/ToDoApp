import json
import logging
import os
import shutil
import tempfile
import time
from config import DATABASE_DIR, TASKS_FILE, USERS_FILE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SESSION_FILE = os.path.join(DATABASE_DIR, "session.json")


class FileLock:
    def __init__(self, path, timeout=10, delay=0.05):
        self.path = path
        self.lock_path = f"{path}.lock"
        self.timeout = timeout
        self.delay = delay
        self.handle = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.lock_path), exist_ok=True)
        self.handle = open(self.lock_path, "a+")
        start = time.time()
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except (BlockingIOError, OSError):
                if time.time() - start >= self.timeout:
                    raise TimeoutError(f"Timeout waiting for lock: {self.lock_path}")
                time.sleep(self.delay)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self.handle.close()
            self.handle = None


def _ensure_database_dir():
    os.makedirs(DATABASE_DIR, exist_ok=True)


def _backup_file(path, keep=5):
    if not os.path.exists(path):
        return

    directory = os.path.dirname(path)
    base = os.path.basename(path)
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(directory, f"{base}.{timestamp}.bak")
    shutil.copy2(path, backup_path)

    backups = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.startswith(base + ".") and f.endswith(".bak")
        ],
        reverse=True,
    )
    for old_backup in backups[keep:]:
        try:
            os.remove(old_backup)
        except OSError:
            pass


def _restore_from_backup(path):
    directory = os.path.dirname(path)
    base = os.path.basename(path)
    candidates = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.startswith(base + ".") and f.endswith(".bak")
        ],
        reverse=True,
    )
    if not candidates:
        return False

    for backup_path in candidates:
        try:
            shutil.copy2(backup_path, path)
            logger.info("Restored %s from backup %s", path, backup_path)
            return True
        except OSError as exc:
            logger.error("Failed to restore %s from backup %s: %s", path, backup_path, exc)
            continue
    return False


def _atomic_write(path, data):
    _ensure_database_dir()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as tmp:
        json.dump(data, tmp, indent=4)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, path)


def _handle_corrupt_file(path):
    try:
        corrupt_path = f"{path}.corrupt"
        if os.path.exists(corrupt_path):
            os.remove(corrupt_path)
        os.replace(path, corrupt_path)
        logger.warning("Backed up corrupt JSON file to %s", corrupt_path)
    except OSError as exc:
        logger.error("Unable to backup corrupt JSON file %s: %s", path, exc)


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        if _restore_from_backup(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                return default
        return default
    except json.JSONDecodeError:
        logger.warning("JSON decode failed for %s", path)
        _handle_corrupt_file(path)
        if _restore_from_backup(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                return default
        return default
    except OSError as exc:
        logger.error("Unable to read %s: %s", path, exc)
        return default


def load_users():
    with FileLock(USERS_FILE):
        return _read_json(USERS_FILE, [])


def save_users(users):
    with FileLock(USERS_FILE):
        _backup_file(USERS_FILE)
        _atomic_write(USERS_FILE, users)


def load_tasks():
    with FileLock(TASKS_FILE):
        return _read_json(TASKS_FILE, [])


def save_tasks(tasks):
    with FileLock(TASKS_FILE):
        _backup_file(TASKS_FILE)
        _atomic_write(TASKS_FILE, tasks)


def load_session():
    with FileLock(SESSION_FILE):
        return _read_json(SESSION_FILE, None)


def save_session(session):
    with FileLock(SESSION_FILE):
        _backup_file(SESSION_FILE)
        _atomic_write(SESSION_FILE, session)


def clear_session():
    with FileLock(SESSION_FILE):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)