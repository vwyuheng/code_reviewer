# src/code_reviewer/utils/helpers.py
from pathlib import Path
from typing import Union, List
import os
import shutil


def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_directory(path: Union[str, Path]) -> None:
    """清空目录内容"""
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def get_file_size(path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    return Path(path).stat().st_size


def format_file_size(size_in_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"


def list_files(
        directory: Union[str, Path],
        extensions: List[str] = None,
        recursive: bool = True
) -> List[Path]:
    """列出目录中的文件"""
    directory = Path(directory)
    files = []

    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(root) / filename
                if not extensions or file_path.suffix.lower() in extensions:
                    files.append(file_path)
    else:
        files = [
            f for f in directory.iterdir()
            if f.is_file() and (not extensions or f.suffix.lower() in extensions)
        ]

    return sorted(files)