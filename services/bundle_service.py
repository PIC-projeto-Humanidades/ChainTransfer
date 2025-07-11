import uuid
import time
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class Bundle:
    id: str
    timestamp: int
    file_name: str
    source_node: str
    destination_node: str
    session: str

    def to_dict(self) -> Dict:
        return asdict(self)


class BundleService:
    def create_bundle(self, file_name: str, source_node: str, destination_node: str, session: str) -> Bundle:
        return Bundle(
            id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            file_name=file_name,
            source_node=source_node,
            destination_node=destination_node,
            session=session
        )
