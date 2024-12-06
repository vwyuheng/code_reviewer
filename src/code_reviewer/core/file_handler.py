# src/code_reviewer/core/file_handler.py
import asyncio
from pathlib import Path
from typing import List, Generator
import tiktoken
from ..models.entities import CodeFile, FileGroup
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    def __init__(self, project_dir: Path, max_tokens_per_group: int):
        self.project_dir = project_dir
        self.max_tokens_per_group = max_tokens_per_group
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def read_file(self, file_path: Path) -> CodeFile:
        try:
            content = file_path.read_text(encoding="utf-8")
            return CodeFile(
                path=file_path.relative_to(self.project_dir),
                content=content,
                token_count=self.count_tokens(content)
            )
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise

    def collect_files(self) -> List[CodeFile]:
        files = []
        for pattern in ["**/*.java", "**/*.yml", "**/*.yaml", "**/*.properties", "**/pom.xml"]:
            files.extend([
                self.read_file(f) for f in self.project_dir.glob(pattern)
                if f.is_file()
            ])
        return files

    def group_files(self, files: List[CodeFile]) -> List[FileGroup]:
        groups = []
        current_group = []
        current_tokens = 0

        for file in sorted(files, key=lambda x: x.token_count):
            if file.token_count > self.max_tokens_per_group:
                if current_group:
                    groups.append(FileGroup(
                        files=current_group,
                        total_tokens=current_tokens,
                        group_id=len(groups) + 1
                    ))
                groups.append(FileGroup(
                    files=[file],
                    total_tokens=file.token_count,
                    group_id=len(groups) + 1
                ))
                current_group = []
                current_tokens = 0
                continue

            if current_tokens + file.token_count > self.max_tokens_per_group:
                if current_group:
                    groups.append(FileGroup(
                        files=current_group,
                        total_tokens=current_tokens,
                        group_id=len(groups) + 1
                    ))
                current_group = [file]
                current_tokens = file.token_count
            else:
                current_group.append(file)
                current_tokens += file.token_count

        if current_group:
            groups.append(FileGroup(
                files=current_group,
                total_tokens=current_tokens,
                group_id=len(groups) + 1
            ))

        return groups