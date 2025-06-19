#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import signal
import time
from typing import Optional

from .monitor import ProcessMonitor
from .menu import InteractiveMenu
from .utils import get_system_info


def signal_handler(signum, frame):
    """
    信号处理器，用于优雅退出
    """
    print("\n收到退出信号，正在安全退出...")
    sys.exit(0)


def main():
    """
    命令行入口函数
    """
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='智能进程监控工具 - 监控并管理系统进程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  process-monitor                    # 启动交互式菜单
  process-monitor --auto             # 启动自动监控模式
  process-monitor --timeout 30      # 设置30秒超时
  process-monitor --interval 2      # 设置2秒检查间隔
  process-monitor --info            # 显示系统信息
  process-monitor --dry-run         # 干运行模式（不实际终止进程）
  process-monitor --search python   # 搜索包含python的进程
  process-monitor --monitor "py,node" # 监控指定进程

注意事项:
  - 系统进程和重要应用程序受到保护
  - 建议在测试环境中验证行为
  - 使用 Ctrl+C 安全退出
        """
    )
    
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=60,
        help='进程超时时间（秒），默认60秒'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help='检查间隔时间（秒），默认5秒'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='干运行模式，只检测不实际终止进程'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示系统信息并退出'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='自动监控模式（非交互式）'
    )
    
    parser.add_argument(
        '--search', '-s',
        type=str,
        help='搜索进程（如: python, node, py）'
    )
    
    parser.add_argument(
        '--monitor', '-m',
        type=str,
        help='指定要监控的进程列表，用逗号分隔（如: "py,node,webstorm"）'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='process_monitor_config.json',
        help='配置文件路径，默认为 process_monitor_config.json'
    )
    
    parser.add_argument(
        '--network', '-n',
        action='store_true',
        help='启用网络进程监控'
    )
    
    args = parser.parse_args()
    
    # 显示系统信息
    if args.info:
        info = get_system_info()
        print("系统信息:")
        print(f"  操作系统: {info['os']}")
        print(f"  架构: {info['architecture']}")
        print(f"  CPU核心数: {info['cpu_count']}")
        print(f"  总内存: {info['total_memory']}")
        return
    
    # 创建监控器实例
    monitor = ProcessMonitor(
        timeout=args.timeout,
        check_interval=args.interval,
        dry_run=args.dry_run,
        verbose=args.verbose,
        config_file=args.config
    )
    
    # 设置网络监控
    if args.network:
        monitor.monitor_network = True
        monitor._save_config()
    
    # 添加监控进程
    if args.monitor:
        processes = [p.strip() for p in args.monitor.split(',') if p.strip()]
        for process in processes:
            monitor.add_monitored_process(process)
        print(f"✅ 已添加监控进程: {', '.join(processes)}")
    
    # 搜索进程
    if args.search:
        print(f"🔍 搜索 '{args.search}' 相关进程...")
        processes = monitor.search_processes(args.search)
        
        if not processes:
            print("❌ 未找到匹配的进程")
            return
        
        print(f"\n✅ 找到 {len(processes)} 个匹配的进程:")
        print("-" * 80)
        print(f"{'PID':<8} {'进程名':<20} {'类型':<8} {'可执行文件':<30}")
        print("-" * 80)
        
        for proc in processes[:20]:  # 只显示前20个
            proc_type = "系统" if proc['is_system'] else "用户"
            exe_path = proc['exe'][:27] + "..." if len(proc['exe']) > 30 else proc['exe']
            print(f"{proc['pid']:<8} {proc['name']:<20} {proc_type:<8} {exe_path:<30}")
        
        if len(processes) > 20:
            print(f"... 还有 {len(processes) - 20} 个进程未显示")
        
        # 询问是否添加到监控
        if not args.auto:
            choice = input(f"\n是否将 '{args.search}' 添加到监控列表？(y/N): ").strip().lower()
            if choice == 'y':
                monitor.add_monitored_process(args.search)
                print(f"✅ 已添加 '{args.search}' 到监控列表")
        
        return
    
    try:
        # 如果指定了自动模式，直接启动监控
        if args.auto:
            print(f"🚀 启动自动监控模式...")
            print(f"⚙️  配置: 超时={args.timeout}s, 间隔={args.interval}s, 干运行={args.dry_run}")
            
            if args.dry_run:
                print("🔍 干运行模式 - 只检测，不会实际终止进程")
            
            # 启动监控
            monitor.start_monitoring()
            
            # 保持程序运行
            while True:
                time.sleep(1)
        else:
            # 启动交互式菜单
            print("🎯 启动交互式进程监控工具...")
            menu = InteractiveMenu(monitor)
            menu.run()
            
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止监控...")
    except Exception as e:
        print(f"监控过程中发生错误: {e}")
    finally:
        monitor.stop_monitoring()
        print("监控已停止")


if __name__ == '__main__':
    main()