# src/code_reviewer/core/analyzer.py
from pathlib import Path
from typing import List, Dict, Any
import re
from ..models.entities import CodeFile
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeAnalyzer:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}

    def analyze_complexity(self, content: str) -> int:
        # 简单的圈复杂度计算
        decision_patterns = [
            r'\bif\b',
            r'\bwhile\b',
            r'\bfor\b',
            r'\bcase\b',
            r'\bcatch\b',
            r'\b&&\b',
            r'\b\|\|\b'
        ]

        complexity = 1
        for pattern in decision_patterns:
            complexity += len(re.findall(pattern, content))
        return complexity

    def analyze_file(self, code_file: CodeFile) -> Dict[str, Any]:
        content = code_file.content

        metrics = {
            'path': str(code_file.path),
            'lines': len(content.splitlines()),
            'complexity': self.analyze_complexity(content),
            'token_count': code_file.token_count,
        }

        if code_file.language == 'java':
            metrics.update(self._analyze_java_file(content))

        return metrics

    def _analyze_java_file(self, content: str) -> Dict[str, Any]:
        metrics = {
            'class_count': len(re.findall(r'\bclass\b', content)),
            'method_count': len(
                re.findall(r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{?', content)),
            'todo_count': len(re.findall(r'//\s*TODO', content)),
            'comment_lines': len(re.findall(r'//.*$|/\*(?:.|[\r\n])*?\*/', content, re.MULTILINE))
        }
        return metrics

    def generate_report(self, files: List[CodeFile]) -> str:
        total_metrics = {
            'total_files': len(files),
            'total_lines': 0,
            'total_complexity': 0,
            'total_tokens': 0,
            'files_analysis': []
        }

        for file in files:
            metrics = self.analyze_file(file)
            total_metrics['files_analysis'].append(metrics)
            total_metrics['total_lines'] += metrics['lines']
            total_metrics['total_complexity'] += metrics['complexity']
            total_metrics['total_tokens'] += metrics['token_count']

        report = "# Code Analysis Report\n\n"
        report += f"## Summary\n"
        report += f"- Total Files: {total_metrics['total_files']}\n"
        report += f"- Total Lines: {total_metrics['total_lines']}\n"
        report += f"- Average Complexity: {total_metrics['total_complexity'] / len(files):.2f}\n"
        report += f"- Total Tokens: {total_metrics['total_tokens']}\n\n"

        report += "## File Details\n\n"
        for analysis in total_metrics['files_analysis']:
            report += f"### {analysis['path']}\n"
            report += f"- Lines: {analysis['lines']}\n"
            report += f"- Complexity: {analysis['complexity']}\n"
            if 'class_count' in analysis:
                report += f"- Classes: {analysis['class_count']}\n"
                report += f"- Methods: {analysis['method_count']}\n"
                report += f"- TODOs: {analysis['todo_count']}\n"
                report += f"- Comment Lines: {analysis['comment_lines']}\n"
            report += "\n"

        return report