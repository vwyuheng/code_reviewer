# src/code_reviewer/core/reviewer.py
from typing import AsyncIterator, List
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import fastapi_poe as fp
from ..models.entities import CodeFile, FileGroup, ReviewResult
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CodeReviewer:
    def __init__(self, api_key: str, model_name: str = "Claude-2-100k"):
        self.api_key = api_key
        self.model_name = model_name

    def create_review_prompt(self, group: FileGroup) -> List[fp.ProtocolMessage]:
        system_message = fp.ProtocolMessage(
            role="system",
            content="""您是一位资深的Java技术专家，专注于代码审查。请对提供的代码进行全面分析，重点关注：
1. 代码质量与清晰度
2. 设计模式的应用
3. 性能优化机会
4. 潜在的bug或安全问题
5. 可维护性和可扩展性

对于每个问题，请提供：
1. 问题描述
2. 影响分析
3. 改进建议
4. 示例代码（如适用）

请使用markdown格式输出，确保层次分明。"""
        )

        user_message_content = "请审查以下代码文件：\n\n"
        for file in group.files:
            user_message_content += (
                f"### 文件：{file.path}\n```{file.language}\n{file.content}\n```\n\n"
            )

        user_message = fp.ProtocolMessage(
            role="user",
            content=user_message_content
        )

        return [system_message, user_message]

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def review_group(self, group: FileGroup) -> ReviewResult:
        messages = self.create_review_prompt(group)
        full_response = ""

        try:
            async for partial in fp.get_bot_response(
                messages=messages,
                bot_name=self.model_name,
                api_key=self.api_key
            ):
                if hasattr(partial, 'text') and partial.text:
                    full_response += partial.text

            return ReviewResult(
                group_id=group.group_id,
                content=full_response,
                files=[file.path for file in group.files],
                status="success"
            )

        except Exception as e:
            logger.error(f"Review error for group {group.group_id}: {str(e)}")
            return ReviewResult(
                group_id=group.group_id,
                content="",
                files=[file.path for file in group.files],
                status="error",
                error=str(e)
            )