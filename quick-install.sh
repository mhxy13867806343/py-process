#!/bin/bash

# py-process-monitor 一键安装脚本
# 最简化的安装方式

set -e

echo "🚀 py-process-monitor 一键安装"
echo "================================"

# 检测系统并安装
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 检测到 macOS 系统"
    
    # 安装 Homebrew（如果没有）
    if ! command -v brew &> /dev/null; then
        echo "📦 安装 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # 安装 Python
    if ! command -v python3 &> /dev/null; then
        echo "🐍 安装 Python..."
        brew install python
    fi
    
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 检测到 Linux 系统"
    
    # 检测包管理器并安装 Python
    if command -v apt-get &> /dev/null; then
        echo "🐍 安装 Python (Ubuntu/Debian)..."
        sudo apt update
        sudo apt install -y python3 python3-pip git curl
    elif command -v yum &> /dev/null; then
        echo "🐍 安装 Python (CentOS/RHEL)..."
        sudo yum install -y python3 python3-pip git curl
    elif command -v dnf &> /dev/null; then
        echo "🐍 安装 Python (Fedora)..."
        sudo dnf install -y python3 python3-pip git curl
    else
        echo "❌ 不支持的 Linux 发行版"
        exit 1
    fi
    
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    echo "💡 请使用 Windows 系统运行 install.bat"
    exit 1
fi

# 下载项目
echo "📥 下载项目..."
cd "$HOME"
if [ -d "py-process-monitor" ]; then
    rm -rf py-process-monitor
fi

if command -v git &> /dev/null; then
    git clone https://github.com/mhxy13867806343/py-process.git py-process-monitor
else
    echo "📦 使用 curl 下载..."
    curl -L https://github.com/mhxy13867806343/py-process/archive/main.tar.gz | tar -xz
    mv py-process-main py-process-monitor
fi

cd py-process-monitor

# 安装依赖
echo "📦 安装依赖..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt
$PIP_CMD install -e .

# 创建启动脚本
echo "🔧 创建启动脚本..."
mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/process-monitor" << EOF
#!/bin/bash
cd "$HOME/py-process-monitor"
$PYTHON_CMD -m process_monitor.cli
EOF

chmod +x "$HOME/.local/bin/process-monitor"

# 添加到 PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

echo "✅ 安装完成！"
echo ""
echo "🎯 使用方法:"
echo "   1. 重新加载终端: source ~/.bashrc"
echo "   2. 运行命令: process-monitor"
echo "   3. 或直接运行: $HOME/.local/bin/process-monitor"
echo ""
echo "📁 项目位置: $HOME/py-process-monitor"
echo "🚀 启动脚本: $HOME/.local/bin/process-monitor"
echo ""
echo "💡 提示: 如果命令未找到，请重新打开终端"