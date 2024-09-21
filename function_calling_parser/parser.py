from inspect import signature
from typing import List, Callable, Union, Any, get_type_hints
from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel, create_model, Field

from function_calling_parser.base import (
    _parse_tool_calls,
    ToolCall
)

class ToolCallParser(BaseModel):
    """
    解析工具调用的解析器类。

    Attributes:
        function_map (dict[str, Callable]): 函数映射表。
    """
    function_map: dict[str, Callable] = {}

    def set_function_map(self, function_map: dict[str, Callable]):
        """
        设置函数映射表。

        Parameters:
            function_map (dict[str, Callable]): 新的函数映射表。
        """
        self.function_map = function_map

    def parse(self, tool_calls: List[ChatCompletionMessageToolCall], function_map: dict[str, Callable] = None) -> List[ToolCall]:
        """
        解析工具调用列表。

        Parameters:
            tool_calls (List[ChatCompletionMessageToolCall]): 工具调用列表。
            function_map (dict[str, Callable], optional): 函数映射表，默认为 None。

        Returns:
            List[ToolCall]: 解析后的工具调用列表。
        """
        if not tool_calls: return None
        if not function_map:
            function_map = self.function_map
        tool_call_list = _parse_tool_calls(tool_calls, function_map)
        return tool_call_list
    
    def parse_to_result_contents(self, tool_calls: List[ChatCompletionMessageToolCall], function_map: dict[str, Callable] = None) -> List[str]:
        """
        解析工具调用并返回结果内容列表。

        Parameters:
            tool_calls (List[ChatCompletionMessageToolCall]): 工具调用列表。
            function_map (dict[str, Callable], optional): 函数映射表，默认为 None。

        Returns:
            List[str]: 结果内容列表。
        """
        if not tool_calls: return None
        contents = []
        tool_call_list = self.parse(tool_calls, function_map)
        for tool_call in tool_call_list:
            contents.append(tool_call.get_function_result_content())
        return contents
    
    def parse_to_messages(self, tool_calls: List[ChatCompletionMessageToolCall], function_map: dict[str, Callable] = None) -> List[dict[str, Any]]:
        """
        解析工具调用并返回消息列表。

        Parameters:
            tool_calls (List[ChatCompletionMessageToolCall]): 工具调用列表。
            function_map (dict[str, Callable], optional): 函数映射表，默认为 None。

        Returns:
            List[dict[str, Any]]: 消息列表。
        """
        if not tool_calls: return None
        messages = []
        tool_call_list = self.parse(tool_calls, function_map)
        for tool_call in tool_call_list:
            messages.append(tool_call.call_dump_message())
        return messages

def parse_func_to_json(func, description: str = "", strict: bool = False) -> dict[str, Any]:
    """
    将函数解析为JSON格式。

    Parameters:
        func (Callable): 要解析的函数。
        description (str, optional): 函数的描述，默认为空字符串。
        strict (bool, optional): 是否严格模式，默认为 False。

    Returns:
        dict[str, Any]: 函数的JSON表示。
    """
    # 获取函数的类型注解
    type_hints = get_type_hints(func)
    # 创建参数模型
    args_model_fields = {}
    for arg, arg_type in type_hints.items():
        if arg != 'return':
            # 获取参数的默认值（如果有）
            default_value = signature(func).parameters[arg].default
            # 如果默认值是 Field 对象，则获取其 description
            if isinstance(default_value, type(Field())):
                description = default_value.description
            else:
                description = None  # 或者你可以设置一个默认的描述
            args_model_fields[arg] = (arg_type, Field(description=description))
    args_model = create_model('FunctionArgs', **args_model_fields)
    # 生成 JSON Schema
    function_args_schema = args_model.schema()
    # 构建最终的    
    function_schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__.strip() if not description else description,
            "parameters": {
                "type": "object",
                "properties": function_args_schema["properties"],
                "required": function_args_schema["required"]
            },
            "strict": strict
        }
    }
    return function_schema