#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py-process-monitor 使用示例

这个脚本演示了如何使用 py-process-monitor 包的各种功能：
1. 基本的进程监控
2. 自定义监控设置
3. 获取系统信息
4. 多线程监控
5. 进程搜索和管理
6. 网络进程监控
7. 历史记录管理
"""

import time
import threading
from process_monitor import ProcessMonitor
from process_monitor.menu import InteractiveMenu
from process_monitor.utils import get_system_info, get_current_time_info, format_bytes, format_duration


def show_system_info():
    """
    显示系统信息
    """
    print("\n=== 系统信息 ===")
    info = get_system_info()
    time_info = get_current_time_info()
    
    print(f"操作系统: {info['os']}")
    print(f"架构: {info['architecture']}")
    print(f"CPU核心数: {info['cpu_count']}")
    print(f"总内存: {info['total_memory']}")
    print(f"当前时间: {time_info['current_time']} ({time_info['weekday']})")
    print(f"系统运行时间: {time_info['system_uptime']}")
    print(f"内存使用率: {time_info['memory_usage']:.1f}%")
    print(f"磁盘使用率: {time_info['disk_usage']:.1f}%")
    print("==================\n")


def basic_usage_example():
    """
    基本使用示例
    """
    print("\n=== 基本使用示例 ===")
    
    # 创建监控器实例（使用默认设置）
    monitor = ProcessMonitor()
    
    print("创建了一个基本的进程监控器")
    print(f"默认超时时间: {monitor.timeout} 秒")
    print(f"默认检查间隔: {monitor.check_interval} 秒")
    
    # 获取当前状态
    status = monitor.get_status()
    print(f"\n当前状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n基本示例完成")


def custom_settings_example():
    """
    自定义设置示例
    """
    print("\n=== 自定义设置示例 ===")
    
    # 创建具有自定义设置的监控器
    monitor = ProcessMonitor(
        timeout=120,        # 2分钟超时
        check_interval=10,  # 10秒检查一次
        dry_run=False,     # 真实模式
        verbose=True       # 详细输出
    )
    
    print("创建了一个自定义设置的进程监控器")
    print(f"超时时间: {monitor.timeout} 秒")
    print(f"检查间隔: {monitor.check_interval} 秒")
    print(f"真实模式: {not monitor.dry_run}")
    print(f"详细输出: {monitor.verbose}")
    
    print("\n自定义设置示例完成")


def process_search_example():
    """
    进程搜索示例
    """
    print("\n=== 进程搜索示例 ===")
    
    monitor = ProcessMonitor()
    
    # 搜索包含 "python" 的进程
    print("搜索包含 'python' 的进程...")
    python_processes = monitor.search_processes("python")
    
    if python_processes:
        print(f"找到 {len(python_processes)} 个Python进程:")
        for i, proc in enumerate(python_processes[:5], 1):  # 只显示前5个
            print(f"  {i}. PID: {proc['pid']}, 名称: {proc['name']}, 类型: {'系统' if proc['is_system'] else '用户'}")
        if len(python_processes) > 5:
            print(f"  ... 还有 {len(python_processes) - 5} 个进程")
    else:
        print("未找到Python进程")
    
    # 搜索包含 "node" 的进程
    print("\n搜索包含 'node' 的进程...")
    node_processes = monitor.search_processes("node")
    
    if node_processes:
        print(f"找到 {len(node_processes)} 个Node进程:")
        for i, proc in enumerate(node_processes[:3], 1):  # 只显示前3个
            print(f"  {i}. PID: {proc['pid']}, 名称: {proc['name']}")
    else:
        print("未找到Node进程")
    
    print("\n进程搜索示例完成")


def monitored_processes_example():
    """
    监控进程管理示例
    """
    print("\n=== 监控进程管理示例 ===")
    
    monitor = ProcessMonitor()
    
    # 添加监控进程
    print("添加监控进程...")
    monitor.add_monitored_process("python")
    monitor.add_monitored_process("node")
    monitor.add_monitored_process("webstorm")
    
    print(f"当前监控进程: {list(monitor.monitored_processes)}")
    
    # 移除一个监控进程
    print("\n移除 'webstorm' 监控...")
    monitor.remove_monitored_process("webstorm")
    
    print(f"更新后监控进程: {list(monitor.monitored_processes)}")
    
    print("\n监控进程管理示例完成")


def network_processes_example():
    """
    网络进程示例
    """
    print("\n=== 网络进程示例 ===")
    
    monitor = ProcessMonitor()
    monitor.monitor_network = True
    
    print("获取网络进程信息...")
    network_processes = monitor.get_network_processes()
    
    if network_processes:
        print(f"找到 {len(network_processes)} 个网络进程:")
        for i, proc in enumerate(network_processes[:5], 1):  # 只显示前5个
            conn = proc.get('connection', {})
            print(f"  {i}. PID: {proc.get('pid')}, 名称: {proc.get('name')}, 本地地址: {conn.get('local_address', 'N/A')}")
        if len(network_processes) > 5:
            print(f"  ... 还有 {len(network_processes) - 5} 个网络进程")
    else:
        print("未找到网络进程或无权限访问")
    
    print("\n网络进程示例完成")


def monitoring_demo():
    """
    监控演示（短时间运行）
    """
    print("\n=== 监控演示 ===")
    
    # 创建监控器（真实模式，会实际终止进程）
    monitor = ProcessMonitor(
        timeout=30,
        check_interval=5,
        dry_run=False,
        verbose=True
    )
    
    # 添加一些监控进程
    monitor.add_monitored_process("python")
    monitor.add_monitored_process("node")
    
    print("启动监控演示（真实模式，持续15秒）...")
    print(f"监控进程: {list(monitor.monitored_processes)}")
    
    try:
        # 启动监控
        monitor.start_monitoring()
        
        # 运行15秒
        time.sleep(15)
        
        # 停止监控
        monitor.stop_monitoring()
        
        print("监控演示完成")
        
        # 显示最终状态
        status = monitor.get_status()
        print(f"\n最终状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 显示历史记录
        history = monitor.get_history(5)
        if history:
            print(f"\n最近 {len(history)} 条历史记录:")
            for record in history:
                timestamp = record['timestamp'][:19].replace('T', ' ')
                action = record['action']
                process_info = record.get('process', {})
                print(f"  {timestamp} - {action} - {process_info.get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"监控演示过程中出错: {e}")
        monitor.stop_monitoring()


def multithreaded_example():
    """
    多线程监控示例
    """
    print("\n=== 多线程监控示例 ===")
    
    # 创建多个监控器实例
    monitors = [
        ProcessMonitor(timeout=60, check_interval=5, dry_run=False),
    ProcessMonitor(timeout=90, check_interval=8, dry_run=False),
    ProcessMonitor(timeout=120, check_interval=10, dry_run=False)
    ]
    
    # 为每个监控器添加不同的监控进程
    monitors[0].add_monitored_process("python")
    monitors[1].add_monitored_process("node")
    monitors[2].add_monitored_process("java")
    
    def run_monitor(monitor, name):
        """在单独线程中运行监控器"""
        print(f"启动监控器 {name}")
        try:
            monitor.start_monitoring()
            time.sleep(10)  # 运行10秒
            monitor.stop_monitoring()
            print(f"监控器 {name} 完成")
        except Exception as e:
            print(f"监控器 {name} 出错: {e}")
    
    # 创建并启动线程
    threads = []
    for i, monitor in enumerate(monitors, 1):
        thread = threading.Thread(
            target=run_monitor,
            args=(monitor, f"Monitor-{i}"),
            daemon=True
        )
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("多线程监控示例完成")


def interactive_menu_demo():
    """
    交互式菜单演示
    """
    print("\n=== 交互式菜单演示 ===")
    print("启动交互式菜单...")
    
    monitor = ProcessMonitor(dry_run=False)  # 使用真实模式
    menu = InteractiveMenu(monitor)
    
    print("注意: 这是真实模式，将会实际终止进程，请谨慎操作！")
    print("您可以尝试各种功能，如搜索进程、添加监控等")
    
    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n交互式菜单演示结束")


def interactive_menu():
    """
    交互式菜单
    """
    while True:
        print("\n" + "=" * 60)
        print("py-process-monitor 功能演示")
        print("=" * 60)
        print("1. 显示系统信息")
        print("2. 基本使用示例")
        print("3. 自定义设置示例")
        print("4. 进程搜索示例")
        print("5. 监控进程管理示例")
        print("6. 网络进程示例")
        print("7. 监控演示")
        print("8. 多线程监控示例")
        print("9. 交互式菜单演示")
        print("0. 退出")
        print("=" * 60)
        
        try:
            choice = input("请选择功能 (0-9): ").strip()
            
            if choice == '0':
                print("感谢使用 py-process-monitor！")
                break
            elif choice == '1':
                show_system_info()
            elif choice == '2':
                basic_usage_example()
            elif choice == '3':
                custom_settings_example()
            elif choice == '4':
                process_search_example()
            elif choice == '5':
                monitored_processes_example()
            elif choice == '6':
                network_processes_example()
            elif choice == '7':
                monitoring_demo()
            elif choice == '8':
                multithreaded_example()
            elif choice == '9':
                interactive_menu_demo()
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n收到中断信号，正在退出...")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    # 首先显示系统信息
    show_system_info()
    
    # 启动交互式菜单
    interactive_menu()