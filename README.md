# function-calling-parser

具有`Function Calling`能力的大语言模型，它允许开发者将外部工具（如 API、函数等）集成到大模型应用程序中，并通过简单的接口进行调用。

`function-calling-parser` 是一个用于解析和调用外部工具的 Python 库，为用户在调用`Function Calling API`时提供了一系列简化流程的工具和方法，。

## 项目功能

- 解析函数并将其转换为 JSON 格式，以便于模型理解和使用。
- 解析模型返回的工具调用信息，并将其转换为可调用的函数和参数，便于获取调用工具的结果。
- 将工具调用的结果转换为 message 对话消息或字符串形式，以便于模型使用。

## 项目特点

- 简单易用：提供简洁的接口和清晰的文档，方便开发者快速上手。
- 类型安全：使用 Pydantic 进行类型检查，确保函数参数和返回值的类型正确。
- 高度可定制：允许开发者自定义函数映射和参数解析方式。

## 详细示例请查阅

[演示示例 - Function calling parser - Example](./main.ipynb)

## 简单调用示例

### 解析函数并转换为 JSON 格式

```python
from function_calling_parser import parse_func_to_json

def get_weather(location: str) -> str:
    """获取某个位置的天气"""
    # 这里可以添加获取天气的逻辑
    return {"location": location, "weather": "sunny"}

# 将函数转换为 JSON 格式
function_schema = parse_func_to_json(get_weather)
print(function_schema)
```

### 解析模型返回的工具调用信息

```python
from function_calling_parser import ToolCallParser

# 定义函数映射表
function_map = {
    "get_weather": get_weather
}

# 创建 ToolCallParser 对象
tool_call_parser = ToolCallParser(function_map=function_map)

# 解析模型返回的工具调用信息
tool_calls = ...  # 从模型获取工具调用信息
tool_call_list = tool_call_parser.parse(tool_calls)

# 调用工具并获取结果
for tool_call in tool_call_list:
    result = tool_call.get_function_result()
    print(result)
```

### 获取工具调用的结果内容

```python
# 获取工具调用的结果内容
result_contents = tool_call_parser.parse_to_result_contents(tool_calls)
print(result_contents)
```

### 获取工具调用的消息列表

```python
# 获取工具调用的消息列表
messages = tool_call_parser.parse_to_messages(tool_calls)
print(messages)
```
