#!/bin/bash

# 测试安装脚本的功能
# 用于验证安装脚本是否正常工作

set -e

echo "🧪 测试 py-process-monitor 安装脚本"
echo "===================================="

# 创建临时测试目录
TEST_DIR="/tmp/py-process-test-$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 测试目录: $TEST_DIR"
echo

# 测试一键安装脚本下载
echo "🔍 测试 1: 下载一键安装脚本"
if curl -fsSL https://raw.githubusercontent.com/mhxy13867806343/py-process/main/quick-install.sh -o quick-install.sh; then
    echo "✅ 一键安装脚本下载成功"
else
    echo "❌ 一键安装脚本下载失败"
    exit 1
fi

# 测试完整安装脚本下载
echo "🔍 测试 2: 下载完整安装脚本"
if curl -fsSL https://raw.githubusercontent.com/mhxy13867806343/py-process/main/install.sh -o install.sh; then
    echo "✅ 完整安装脚本下载成功"
else
    echo "❌ 完整安装脚本下载失败"
    exit 1
fi

# 测试 Windows 安装脚本下载
echo "🔍 测试 3: 下载 Windows 安装脚本"
if curl -fsSL https://raw.githubusercontent.com/mhxy13867806343/py-process/main/install.bat -o install.bat; then
    echo "✅ Windows 安装脚本下载成功"
else
    echo "❌ Windows 安装脚本下载失败"
    exit 1
fi

# 检查脚本权限
echo "🔍 测试 4: 检查脚本权限"
chmod +x quick-install.sh install.sh
if [[ -x "quick-install.sh" && -x "install.sh" ]]; then
    echo "✅ 脚本权限设置成功"
else
    echo "❌ 脚本权限设置失败"
    exit 1
fi

# 测试脚本语法
echo "🔍 测试 5: 检查脚本语法"
if bash -n quick-install.sh && bash -n install.sh; then
    echo "✅ 脚本语法检查通过"
else
    echo "❌ 脚本语法检查失败"
    exit 1
fi

# 测试项目下载
echo "🔍 测试 6: 测试项目下载"
if git clone https://github.com/mhxy13867806343/py-process.git test-project; then
    echo "✅ 项目下载成功"
    
    # 检查关键文件
    cd test-project
    if [[ -f "requirements.txt" && -f "setup.py" && -d "process_monitor" ]]; then
        echo "✅ 项目文件完整"
    else
        echo "❌ 项目文件不完整"
        exit 1
    fi
    
    # 检查 Python 模块
    if [[ -f "process_monitor/__init__.py" && -f "process_monitor/cli.py" ]]; then
        echo "✅ Python 模块完整"
    else
        echo "❌ Python 模块不完整"
        exit 1
    fi
    
    cd ..
else
    echo "❌ 项目下载失败"
    exit 1
fi

# 测试 README 内容
echo "🔍 测试 7: 检查 README 内容"
if grep -q "一键安装" test-project/README.md; then
    echo "✅ README 包含安装说明"
else
    echo "❌ README 缺少安装说明"
    exit 1
fi

# 清理测试目录
echo "🧹 清理测试环境"
cd /
rm -rf "$TEST_DIR"

echo
echo "🎉 所有测试通过！"
echo "✅ 安装脚本功能正常"
echo "✅ 项目文件完整"
echo "✅ 下载链接有效"
echo
echo "📋 测试总结:"
echo "   - 一键安装脚本: ✅"
echo "   - 完整安装脚本: ✅"
echo "   - Windows 安装脚本: ✅"
echo "   - 项目下载: ✅"
echo "   - 文件完整性: ✅"
echo "   - 脚本语法: ✅"
echo
echo "🚀 用户现在可以使用以下命令安装:"
echo "   curl -fsSL https://raw.githubusercontent.com/mhxy13867806343/py-process/main/quick-install.sh | bash"