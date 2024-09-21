import json
import logging
from typing import List, Callable
from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel

log = logging.getLogger(__name__)


class Function(BaseModel):
    call: Callable
    name: str
    arguments: dict

    def get_result(self):
        return self.call(**self.arguments)

    def get_result_content(self) -> str:
        return str(self.call(**self.arguments))


class ToolCall(BaseModel):
    id: str
    function: Function

    def call_dump_message(self) -> dict[str, str]:
        return {
            "role": "tool",
            "tool_call_id": self.id,
            "name": self.function.name,
            "content": self.function.get_result_content()
        }

    def get_function_result(self):
        return self.function.get_result()

    def get_function_result_content(self) -> str:
        return self.function.get_result_content()


def _parse_tool_call(tool_call: ChatCompletionMessageToolCall, function_map: dict[str, Callable]) -> ToolCall:
    function_name = tool_call.function.name
    # 查找并调用对应的函数
    if function_name in function_map:
        # 确保arguments是一个字符串
        arguments = tool_call.function.arguments
        if isinstance(arguments, dict):
            arguments = json.dumps(arguments)
        # 解析arguments字符串为字典
        arguments = json.loads(arguments)
        function_call = function_map[function_name]
        return ToolCall(
            id=tool_call.id,
            function=Function(
                call=function_call,
                name=function_name,
                arguments=arguments
            )
        )
    else:
        log.exception(f"Function not found: {function_name}")
    return None


def _parse_tool_calls(tool_calls: List[ChatCompletionMessageToolCall], function_map: dict[str, Callable]) -> List[ToolCall]:
    tool_call_list = []
    for tool_call in tool_calls:
        tool_call = _parse_tool_call(tool_call, function_map)
        if tool_call:
            tool_call_list.append(tool_call)
    return tool_call_list
