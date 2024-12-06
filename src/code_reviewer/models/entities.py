# src/code_reviewer/models/entities.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class CodeFile:
    path: Path
    content: str
    token_count: int
    file_type: str = "unknown"

    @property
    def file_extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def language(self) -> str:
        return {
            ".java": "java",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".properties": "properties",
            ".xml": "xml"
        }.get(self.file_extension, "text")


@dataclass
class FileGroup:
    files: List[CodeFile]
    total_tokens: int
    group_id: int


@dataclass
class ReviewResult:
    group_id: int
    content: str
    files: List[Path]
    status: str
    error: Optional[str] = None