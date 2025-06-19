# py-process-monitor

一个功能强大的 Python 进程监控和管理工具，支持批量处理、智能分组和自动化管理。

## ✨ 特性

- 🔍 **实时进程监控** - 监控系统中的所有进程
- 📊 **详细信息显示** - CPU、内存、运行时间等详细信息
- 🎯 **批量处理** - 智能分组处理同名进程
- ⚙️ **灵活配置** - 可配置的监控规则和限制
- 🖥️ **交互式界面** - 友好的命令行交互界面
- 🚀 **一键安装** - 支持多平台自动安装

## 🚀 快速安装

### 方法一：一键安装（推荐）

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/mhxy13867806343/py-process/main/quick-install.sh | bash
```

**Windows:**
```cmd
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/mhxy13867806343/py-process/main/install.bat' -OutFile 'install.bat' && install.bat"
```

### 方法二：完整安装脚本

**Linux/macOS:**
```bash
# 下载并运行安装脚本
wget https://raw.githubusercontent.com/mhxy13867806343/py-process/main/install.sh
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
# 下载并运行安装脚本
curl -O https://raw.githubusercontent.com/mhxy13867806343/py-process/main/install.bat
install.bat
```

### 方法三：手动安装

```bash
# 克隆项目
git clone https://github.com/mhxy13867806343/py-process.git
cd py-process

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 运行
python example.py
```

## 📖 使用方法

### 命令行启动

安装完成后，可以通过以下方式启动：

```bash
# 如果已添加到 PATH
process-monitor

# 或者直接运行
python -m process_monitor.cli

# 或者运行示例
python example.py
```

### 主要功能

1. **进程监控**
   - 查看所有运行中的进程
   - 实时更新进程信息
   - 按 CPU、内存等排序

2. **批量处理**
   - 自动分组同名进程
   - 批量终止进程
   - 可配置终止数量限制

3. **配置管理**
   - 监控规则设置
   - 批量处理配置
   - 进程限制管理

## ⚙️ 配置选项

### 批量处理设置

- **批量模式**: 启用/禁用批量处理
- **全局限制**: 设置全局最大终止数量
- **进程限制**: 为特定进程设置终止数量限制

### 监控设置

- **网络监控**: 启用/禁用网络信息监控
- **自动刷新**: 设置自动刷新间隔
- **显示过滤**: 配置进程显示过滤规则

## 🛠️ 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows, macOS, Linux
- **依赖**: psutil >= 5.9.0

## 📁 项目结构

```
py-process/
├── process_monitor/          # 主要模块
│   ├── __init__.py
│   ├── cli.py               # 命令行接口
│   ├── menu.py              # 交互式菜单
│   ├── monitor.py           # 核心监控逻辑
│   └── utils.py             # 工具函数
├── install.sh               # Linux/macOS 安装脚本
├── install.bat              # Windows 安装脚本
├── quick-install.sh         # 一键安装脚本
├── example.py               # 使用示例
├── requirements.txt         # 依赖列表
└── setup.py                 # 安装配置
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

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