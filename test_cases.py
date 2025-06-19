#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py-process-monitor 测试用例

这个文件包含了对进程监控工具各项功能的全面测试用例。
测试覆盖了以下功能：
1. 基本监控功能
2. 进程搜索功能
3. 监控进程管理
4. 配置文件操作
5. 网络进程监控
6. 历史记录管理
7. 系统信息获取
8. 错误处理
"""

import os
import sys
import time
import json
import tempfile
import subprocess
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_monitor import ProcessMonitor
from process_monitor.utils import (
    get_system_info, 
    get_current_time_info, 
    get_network_connections,
    is_system_process,
    is_safe_to_terminate,
    format_bytes,
    format_duration
)
from process_monitor.menu import InteractiveMenu


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print(f"\n🧪 运行测试: {test_name}")
        try:
            test_func()
            print(f"✅ 测试通过: {test_name}")
            self.passed += 1
            self.test_results.append((test_name, "PASS", None))
        except Exception as e:
            print(f"❌ 测试失败: {test_name} - {str(e)}")
            self.failed += 1
            self.test_results.append((test_name, "FAIL", str(e)))
    
    def print_summary(self):
        """打印测试总结"""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"📊 测试总结")
        print(f"{'='*60}")
        print(f"总测试数: {total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"成功率: {(self.passed/total*100):.1f}%" if total > 0 else "成功率: 0%")
        
        if self.failed > 0:
            print(f"\n❌ 失败的测试:")
            for name, status, error in self.test_results:
                if status == "FAIL":
                    print(f"  - {name}: {error}")


def test_system_info():
    """测试系统信息获取"""
    info = get_system_info()
    assert 'os' in info, "系统信息缺少操作系统字段"
    assert 'cpu_count' in info, "系统信息缺少CPU核心数字段"
    assert 'total_memory' in info, "系统信息缺少总内存字段"
    assert info['cpu_count'] > 0, "CPU核心数应该大于0"
    
    time_info = get_current_time_info()
    assert 'current_time' in time_info, "时间信息缺少当前时间字段"
    assert 'system_uptime' in time_info, "时间信息缺少系统运行时间字段"
    assert 'memory_usage' in time_info, "时间信息缺少内存使用率字段"
    assert 0 <= time_info['memory_usage'] <= 100, "内存使用率应该在0-100之间"


def test_process_monitor_init():
    """测试ProcessMonitor初始化"""
    # 测试默认参数
    monitor = ProcessMonitor()
    assert monitor.check_interval == 5, "默认检查间隔应该是5秒"
    assert monitor.timeout == 30, "默认超时应该是30秒"
    assert not monitor.dry_run, "默认不应该是干运行模式"
    
    # 测试自定义参数
    monitor = ProcessMonitor(check_interval=10, timeout=120, dry_run=True, verbose=True)
    assert monitor.check_interval == 10, "自定义检查间隔应该是10秒"
    assert monitor.timeout == 120, "自定义超时应该是120秒"
    assert monitor.dry_run, "应该是干运行模式"
    assert monitor.verbose, "应该是详细模式"


def test_process_search():
    """测试进程搜索功能"""
    monitor = ProcessMonitor()
    
    # 搜索Python进程
    python_processes = monitor.search_processes("python")
    assert isinstance(python_processes, list), "搜索结果应该是列表"
    
    # 搜索不存在的进程
    fake_processes = monitor.search_processes("nonexistent_process_12345")
    assert isinstance(fake_processes, list), "搜索结果应该是列表"
    assert len(fake_processes) == 0, "不存在的进程搜索结果应该为空"
    
    # 测试空查询
    empty_result = monitor.search_processes("")
    assert isinstance(empty_result, list), "空查询结果应该是列表"


def test_monitored_processes_management():
    """测试监控进程管理"""
    monitor = ProcessMonitor()
    
    # 添加监控进程
    monitor.add_monitored_process("test_process")
    assert "test_process" in monitor.monitored_processes, "应该成功添加监控进程"
    
    # 重复添加同一进程
    initial_count = len(monitor.monitored_processes)
    monitor.add_monitored_process("test_process")
    assert len(monitor.monitored_processes) == initial_count, "重复添加不应该增加进程数量"
    
    # 移除监控进程
    monitor.remove_monitored_process("test_process")
    assert "test_process" not in monitor.monitored_processes, "应该成功移除监控进程"
    
    # 移除不存在的进程
    monitor.remove_monitored_process("nonexistent_process")
    # 不应该抛出异常


def test_config_operations():
    """测试配置文件操作"""
    # 使用临时文件进行测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config = f.name
    
    try:
        monitor = ProcessMonitor(config_file=temp_config)
        
        # 添加一些测试数据
        monitor.add_monitored_process("test_app")
        
        # 保存配置
        monitor._save_config()
        
        # 验证配置文件存在
        assert os.path.exists(temp_config), "配置文件应该被创建"
        
        # 读取配置文件内容
        with open(temp_config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        assert "monitored_processes" in config_data, "配置文件应该包含监控进程列表"
        assert "test_app" in config_data["monitored_processes"], "配置文件应该包含测试进程"
        
        # 创建新的监控器实例并加载配置
        new_monitor = ProcessMonitor(config_file=temp_config)
        new_monitor._load_config()
        
        assert "test_app" in new_monitor.monitored_processes, "新实例应该加载监控进程"
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_config):
            os.unlink(temp_config)


def test_network_connections():
    """测试网络连接获取"""
    connections = get_network_connections()
    assert isinstance(connections, list), "网络连接应该是列表"
    
    # 如果有连接，验证连接信息结构
    if connections:
        conn = connections[0]
        expected_keys = ['fd', 'family', 'type', 'local_address', 'remote_address', 'status', 'pid']
        for key in expected_keys:
            assert key in conn, f"连接信息应该包含{key}字段"


def test_process_status():
    """测试进程状态获取"""
    monitor = ProcessMonitor()
    monitor.add_monitored_process("test_process")
    
    status = monitor.get_status()
    assert isinstance(status, dict), "状态应该是字典"
    assert 'is_running' in status, "状态应该包含运行状态"
    assert 'monitored_processes' in status, "状态应该包含监控进程列表"
    assert 'check_interval' in status, "状态应该包含检查间隔"
    assert 'timeout' in status, "状态应该包含超时设置"
    assert 'history_count' in status, "状态应该包含历史记录数量"


def test_history_management():
    """测试历史记录管理"""
    monitor = ProcessMonitor()
    
    # 初始历史应该为空
    history = monitor.get_history()
    assert isinstance(history, list), "历史记录应该是列表"
    
    # 清空历史记录
    monitor.clear_history()
    history_after_clear = monitor.get_history()
    assert len(history_after_clear) == 0, "清空后历史记录应该为空"


def test_utility_functions():
    """测试工具函数"""
    # 测试格式化字节
    assert format_bytes(1024) == "1.0 KB", "1024字节应该格式化为1.0 KB"
    assert format_bytes(1024*1024) == "1.0 MB", "1MB应该格式化为1.0 MB"
    assert format_bytes(0) == "0.0 B", "0字节应该格式化为0.0 B"
    
    # 测试格式化持续时间
    duration_1h = format_duration(3600)
    assert "1小时" in duration_1h or "1.0小时" in duration_1h, "3600秒应该包含小时"
    
    duration_1d = format_duration(86400)
    assert "1天" in duration_1d or "1.0天" in duration_1d, "86400秒应该包含天"


def test_error_handling():
    """测试错误处理"""
    monitor = ProcessMonitor()
    
    # 测试无效配置文件路径
    invalid_monitor = ProcessMonitor(config_file="/invalid/path/config.json")
    # 不应该抛出异常，应该优雅处理
    
    # 测试搜索无效查询
    try:
        result = monitor.search_processes(None)
        # 应该返回空列表或处理None值
        assert isinstance(result, list), "无效查询应该返回列表"
    except Exception:
        # 如果抛出异常，应该是可预期的异常
        pass


def test_interactive_menu():
    """测试交互式菜单"""
    monitor = ProcessMonitor()
    menu = InteractiveMenu(monitor)
    
    # 测试菜单初始化
    assert menu.monitor == monitor, "菜单应该正确关联监控器"
    
    # 测试系统信息显示（不会有用户交互）
    try:
        # 这里只测试方法存在性，不实际运行交互
        assert hasattr(menu, 'display_header'), "菜单应该有显示头部信息方法"
        assert hasattr(menu, 'display_main_menu'), "菜单应该有显示主菜单方法"
        assert hasattr(menu, 'run'), "菜单应该有运行方法"
    except Exception as e:
        raise AssertionError(f"交互式菜单方法检查失败: {e}")


def test_command_line_interface():
    """测试命令行界面"""
    # 测试帮助命令
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'process_monitor.cli', '--help'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        assert result.returncode == 0, "帮助命令应该成功执行"
        assert "usage:" in result.stdout.lower() or "用法:" in result.stdout, "帮助输出应该包含用法信息"
    except subprocess.TimeoutExpired:
        raise AssertionError("命令行帮助命令超时")
    except Exception as e:
        raise AssertionError(f"命令行界面测试失败: {e}")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 py-process-monitor 测试用例")
    print("="*60)
    
    runner = TestRunner()
    
    # 定义所有测试用例
    test_cases = [
        ("系统信息获取", test_system_info),
        ("ProcessMonitor初始化", test_process_monitor_init),
        ("进程搜索功能", test_process_search),
        ("监控进程管理", test_monitored_processes_management),
        ("配置文件操作", test_config_operations),
        ("网络连接获取", test_network_connections),
        ("进程状态获取", test_process_status),
        ("历史记录管理", test_history_management),
        ("工具函数测试", test_utility_functions),
        ("错误处理测试", test_error_handling),
        ("交互式菜单", test_interactive_menu),
        ("命令行界面", test_command_line_interface),
    ]
    
    # 运行所有测试
    for test_name, test_func in test_cases:
        runner.run_test(test_name, test_func)
    
    # 打印测试总结
    runner.print_summary()
    
    return runner.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)