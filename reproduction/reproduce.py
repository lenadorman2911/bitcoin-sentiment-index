                                                                       
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def fingerprint():
                                                                    
    result = {}
    for label, root in [("repository", ROOT)]:
        for folder in ("data", "scripts"):
            base = root / folder
            if not base.is_dir():
                raise RuntimeError("Missing protected directory: " + str(base))
            for path in sorted(base.rglob("*")):
                if path.is_symlink():
                    raise RuntimeError("Symlink in protected tree: " + str(path))
                if path.is_file():
                    result[label + "/" + str(path.relative_to(root))] = digest(path)
    return result
