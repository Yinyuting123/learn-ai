## 运行
```
uv run clien.py server.py
```

## Inspector 工具
  - 在实际开发MCP服务器的过程中，Anthropic提供了一个非常便捷的debug工具：Inspector。借助Inspector，我们能够非常快捷的调用各类server，并测试其功能。Inspector具体功能实现流程如下。
  - 运行Inspector工具：
    ```
    npx -y @modelcontextprotocol/inspector uv run server.py
    ```
    这会启动Inspector工具，并连接到运行在 `server.py` 上的MCP服务器。

