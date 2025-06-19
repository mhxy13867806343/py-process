#!/bin/bash

# py-process-monitor 自动安装脚本
# 支持在没有 Python 环境的系统上自动安装和运行

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            print_error "不支持的 Linux 发行版"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        PACKAGE_MANAGER="choco"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    print_info "检测到操作系统: $OS"
}

# 检查 Python 是否已安装
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_success "Python $PYTHON_VERSION 已安装"
            PYTHON_CMD="python3"
            return 0
        else
            print_warning "Python 版本过低 ($PYTHON_VERSION)，需要 Python 3.8+"
            return 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_success "Python $PYTHON_VERSION 已安装"
            PYTHON_CMD="python"
            return 0
        else
            print_warning "Python 版本过低 ($PYTHON_VERSION)，需要 Python 3.8+"
            return 1
        fi
    else
        print_warning "未检测到 Python"
        return 1
    fi
}

# 安装 Python
install_python() {
    print_info "正在安装 Python..."
    
    case $OS in
        "linux")
            case $PACKAGE_MANAGER in
                "apt")
                    sudo apt update
                    sudo apt install -y python3 python3-pip python3-venv
                    ;;
                "yum")
                    sudo yum install -y python3 python3-pip
                    ;;
                "dnf")
                    sudo dnf install -y python3 python3-pip
                    ;;
                "pacman")
                    sudo pacman -S --noconfirm python python-pip
                    ;;
            esac
            PYTHON_CMD="python3"
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                print_info "安装 Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python
            PYTHON_CMD="python3"
            ;;
        "windows")
            if ! command -v choco &> /dev/null; then
                print_error "请先安装 Chocolatey 或手动安装 Python"
                print_info "Chocolatey 安装: https://chocolatey.org/install"
                print_info "Python 下载: https://www.python.org/downloads/"
                exit 1
            fi
            choco install python -y
            PYTHON_CMD="python"
            ;;
    esac
    
    # 验证安装
    if check_python; then
        print_success "Python 安装成功"
    else
        print_error "Python 安装失败"
        exit 1
    fi
}

# 检查 pip 是否可用
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        return 0
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        return 0
    else
        print_warning "pip 未找到"
        return 1
    fi
}

# 安装 pip
install_pip() {
    print_info "正在安装 pip..."
    
    case $OS in
        "linux")
            case $PACKAGE_MANAGER in
                "apt")
                    sudo apt install -y python3-pip
                    ;;
                "yum")
                    sudo yum install -y python3-pip
                    ;;
                "dnf")
                    sudo dnf install -y python3-pip
                    ;;
                "pacman")
                    sudo pacman -S --noconfirm python-pip
                    ;;
            esac
            ;;
        "macos")
            $PYTHON_CMD -m ensurepip --upgrade
            ;;
        "windows")
            $PYTHON_CMD -m ensurepip --upgrade
            ;;
    esac
    
    if check_pip; then
        print_success "pip 安装成功"
    else
        print_error "pip 安装失败"
        exit 1
    fi
}

# 下载项目
download_project() {
    print_info "正在下载 py-process-monitor..."
    
    PROJECT_DIR="$HOME/py-process-monitor"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "项目目录已存在，正在更新..."
        cd "$PROJECT_DIR"
        if [ -d ".git" ]; then
            git pull
        else
            cd ..
            rm -rf "py-process-monitor"
            git clone https://github.com/mhxy13867806343/py-process.git py-process-monitor
        fi
    else
        cd "$HOME"
        if command -v git &> /dev/null; then
            git clone https://github.com/mhxy13867806343/py-process.git py-process-monitor
        else
            print_info "Git 未安装，使用 curl 下载..."
            mkdir -p py-process-monitor
            cd py-process-monitor
            curl -L https://github.com/mhxy13867806343/py-process/archive/main.zip -o main.zip
            if command -v unzip &> /dev/null; then
                unzip main.zip
                mv py-process-main/* .
                rm -rf py-process-main main.zip
            else
                print_error "需要 unzip 工具来解压文件"
                exit 1
            fi
        fi
    fi
    
    cd "$PROJECT_DIR"
    print_success "项目下载完成: $PROJECT_DIR"
}

# 安装依赖
install_dependencies() {
    print_info "正在安装项目依赖..."
    
    # 升级 pip
    $PIP_CMD install --upgrade pip
    
    # 安装项目依赖
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
    fi
    
    # 安装项目本身
    $PIP_CMD install -e .
    
    print_success "依赖安装完成"
}

# 创建启动脚本
create_launcher() {
    print_info "创建启动脚本..."
    
    LAUNCHER_PATH="$HOME/.local/bin/process-monitor"
    mkdir -p "$HOME/.local/bin"
    
    cat > "$LAUNCHER_PATH" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
$PYTHON_CMD -m process_monitor.cli
EOF
    
    chmod +x "$LAUNCHER_PATH"
    
    # 添加到 PATH
    SHELL_RC="$HOME/.bashrc"
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if ! grep -q "$HOME/.local/bin" "$SHELL_RC" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        print_info "已添加 $HOME/.local/bin 到 PATH"
    fi
    
    print_success "启动脚本创建完成: $LAUNCHER_PATH"
}

# 显示使用说明
show_usage() {
    print_success "安装完成！"
    echo
    print_info "使用方法:"
    echo "  1. 重新加载终端或运行: source ~/.bashrc (或 ~/.zshrc)"
    echo "  2. 运行命令: process-monitor"
    echo "  3. 或者直接运行: $HOME/.local/bin/process-monitor"
    echo "  4. 或者进入项目目录运行: cd $PROJECT_DIR && $PYTHON_CMD example.py"
    echo
    print_info "项目位置: $PROJECT_DIR"
    print_info "启动脚本: $HOME/.local/bin/process-monitor"
    echo
    print_warning "如果遇到权限问题，可能需要使用 sudo 运行某些命令"
}

# 主函数
main() {
    echo "======================================"
    echo "  py-process-monitor 自动安装脚本"
    echo "======================================"
    echo
    
    # 检测操作系统
    detect_os
    
    # 检查并安装 Python
    if ! check_python; then
        install_python
    fi
    
    # 检查并安装 pip
    if ! check_pip; then
        install_pip
    fi
    
    # 下载项目
    download_project
    
    # 安装依赖
    install_dependencies
    
    # 创建启动脚本
    create_launcher
    
    # 显示使用说明
    show_usage
}

# 运行主函数
main "$@"