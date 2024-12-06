# src/code_reviewer/cli.py
import typer
import asyncio
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskID
from .config.settings import Settings, load_config, save_config
from .core.file_handler import FileHandler
from .core.reviewer import CodeReviewer
from .core.analyzer import CodeAnalyzer
from .utils.logger import get_logger
from .utils.helpers import ensure_directory

app = typer.Typer()
console = Console()
logger = get_logger(__name__)


@app.command()
def review(
        project_dir: str = typer.Argument(..., help="Java项目目录路径"),
        output_dir: str = typer.Option("./reviews", help="审查报告输出目录"),
        config_file: str = typer.Option("config.yaml", help="配置文件路径")
):
    """运行代码审查"""
    try:
        # 加载配置
        config = load_config(Path(config_file))
        settings = Settings(**config)

        if not settings.api_key:
            settings.api_key = typer.prompt(
                "请输入 POE API Key",
                hide_input=True
            )
            save_config({"api_key": settings.api_key}, Path(config_file))

        # 初始化组件
        project_dir = Path(project_dir)
        output_dir = ensure_directory(output_dir)

        file_handler = FileHandler(project_dir, settings.max_tokens_per_group)
        reviewer = CodeReviewer(settings.api_key, settings.model_name)
        analyzer = CodeAnalyzer()

        # 运行审查
        asyncio.run(run_review(
            file_handler,
            reviewer,
            analyzer,
            output_dir
        ))

    except Exception as e:
        logger.error(f"Review failed: {str(e)}")
        raise typer.Exit(1)


async def run_review(
        file_handler: FileHandler,
        reviewer: CodeReviewer,
        analyzer: CodeAnalyzer,
        output_dir: Path
):
    """执行审查流程"""
    with Progress() as progress:
        # 收集文件
        files = file_handler.collect_files()
        if not files:
            console.print("[red]未找到需要审查的文件[/red]")
            return

        # 生成分析报告
        analysis_report = analyzer.generate_report(files)
        (output_dir / "analysis_report.md").write_text(
            analysis_report,
            encoding="utf-8"
        )

        # 分组处理
        groups = file_handler.group_files(files)
        task = progress.add_task(
            "[green]执行代码审查...",
            total=len(groups)
        )

        for group in groups:
            try:
                result = await reviewer.review_group(group)
                if result.status == "success":
                    output_file = output_dir / f"review_group_{result.group_id}.md"
                    output_file.write_text(result.content, encoding="utf-8")
                    progress.update(task, advance=1)
                else:
                    console.print(f"[red]组 {group.group_id} 审查失败: {result.error}[/red]")

            except Exception as e:
                logger.error(f"Group {group.group_id} review failed: {str(e)}")
                continue

            if not progress.finished:
                from src.code_reviewer.config import settings
                await asyncio.sleep(settings.delay_between_groups)


if __name__ == "__main__":
    app()