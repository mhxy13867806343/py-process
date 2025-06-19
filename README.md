# py-process-monitor

一个用于监控和管理进程的Python包，可以自动终止超过指定时间未运行的进程（排除系统进程）。

## 功能特性

- 监控系统中的所有进程
- 自动识别并排除系统进程
- 当进程超过指定时间（默认30秒）未活动时自动终止
- 支持自定义监控间隔和超时时间
- 提供命令行工具和Python API

## 安装

### 从源码安装

```bash
git clone https://github.com/hooksvue/py-process-monitor.git
cd py-process-monitor
pip install -e .
```

### 使用pip安装

```bash
pip install py-process-monitor
```

## 使用方法

### 命令行使用

```bash
# 启动进程监控（默认30秒超时）
process-monitor

# 自定义超时时间（60秒）
process-monitor --timeout 60

# 自定义检查间隔（10秒）
process-monitor --interval 10

# 显示帮助信息
process-monitor --help
```

### Python API使用

```python
from process_monitor import ProcessMonitor

# 创建监控器实例
monitor = ProcessMonitor(timeout=30, check_interval=5)

# 启动监控
monitor.start_monitoring()

# 停止监控
monitor.stop_monitoring()
```

## 系统进程保护

本工具会自动识别并保护以下类型的系统进程：

- 内核进程
- 系统守护进程
- 重要的系统服务
- 具有系统权限的进程

## 要求

- Python 3.11+
- psutil 5.9.0+

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！

## 注意事项

- 请谨慎使用此工具，确保不会意外终止重要进程
- 建议在测试环境中先行验证
- 系统进程受到保护，不会被终止