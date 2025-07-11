from pathlib import Path
from typing import List

class StorageService:
    def __init__(self, media_path: Path):
        self.media_path = media_path
        self._ensure_directory()

    def _ensure_directory(self):
        if not self.media_path.exists():
            self.media_path.mkdir(parents=True, exist_ok=True)

    def list_files(self) -> List[str]:
        return [f.name for f in self.media_path.iterdir() if f.is_file()]
