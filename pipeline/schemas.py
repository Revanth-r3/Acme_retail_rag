from dataclasses import dataclass
from typing import Dict


@dataclass
class DocumentChunk:
    text: str
    metadata: Dict