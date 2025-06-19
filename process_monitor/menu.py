#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import threading
from typing import List, Dict, Optional
from datetime import datetime

from .monitor import ProcessMonitor
from .utils import get_current_time_info, format_bytes, format_duration


class InteractiveMenu:
    """
    交互式菜单类，提供用户界面
    """
    
    def __init__(self, monitor: ProcessMonitor):
        """
        初始化交互式菜单
        
        Args:
            monitor: ProcessMonitor实例
        """
        self.monitor = monitor
        self.running = True
        self.status_thread: Optional[threading.Thread] = None
        self.show_status = False
    
    def clear_screen(self) -> None:
        """
        清屏
        """
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self) -> None:
        """
        显示头部信息
        """
        time_info = get_current_time_info()
        print("=" * 80)
        print(f"🔍 进程监控工具 - {time_info['current_time']} ({time_info['weekday']})")
        print(f"💻 系统运行时间: {time_info['system_uptime']} | CPU: {time_info['cpu_count']}核 | 内存使用: {time_info['memory_usage']:.1f}% | 磁盘使用: {time_info['disk_usage']:.1f}%")
        
        status = self.monitor.get_status()
        status_text = "🟢 运行中" if status['is_running'] else "🔴 已停止"
        print(f"📊 监控状态: {status_text} | 超时: {status['timeout']}s | 间隔: {status['check_interval']}s | 跟踪进程: {status['tracked_processes']}")
        
        if status['monitored_processes']:
            print(f"🎯 监控目标: {', '.join(status['monitored_processes'])}")
        else:
            print("🎯 监控目标: 所有非系统进程")
        
        print("=" * 80)
    
    def display_main_menu(self) -> None:
        """
        显示主菜单
        """
        print("\n📋 主菜单:")
        print("1. 🔍 搜索进程")
        print("2. ➕ 添加监控进程")
        print("3. ➖ 移除监控进程")
        print("4. 📊 查看监控状态")
        print("5. 📜 查看历史记录")
        print("6. 🌐 查看网络进程")
        print("7. ⚙️  监控设置")
        print("8. 🚀 启动/停止监控")
        print("9. 🧹 清理历史记录")
        print("0. 🚪 退出程序")
        print("-" * 40)
    
    def search_processes_menu(self) -> None:
        """
        搜索进程菜单
        """
        while True:
            self.clear_screen()
            self.display_header()
            print("\n🔍 进程搜索")
            print("输入搜索关键词（如: py, python, node, webstorm）")
            print("提示: 输入 'p' 可以找到所有包含p的进程")
            print("输入 'back' 返回主菜单")
            
            # 显示搜索历史
            if self.monitor.menu_history:
                print("\n📚 最近搜索:")
                for i, item in enumerate(self.monitor.menu_history[-5:], 1):
                    print(f"  {i}. {item}")
            
            query = input("\n请输入搜索关键词: ").strip()
            
            if query.lower() == 'back':
                break
            
            if not query:
                continue
            
            # 检查是否是历史记录编号
            if query.isdigit() and self.monitor.menu_history:
                idx = int(query) - 1
                if 0 <= idx < len(self.monitor.menu_history[-5:]):
                    query = self.monitor.menu_history[-(5-idx)]
            
            # 添加到历史记录
            if query not in self.monitor.menu_history:
                self.monitor.menu_history.append(query)
                self.monitor._save_config()
            
            # 搜索进程
            print(f"\n🔍 搜索 '{query}' 相关进程...")
            processes = self.monitor.search_processes(query)
            
            if not processes:
                print("❌ 未找到匹配的进程")
                input("按回车键继续...")
                continue
            
            # 显示搜索结果
            print(f"\n✅ 找到 {len(processes)} 个匹配的进程:")
            print("-" * 80)
            print(f"{'序号':<4} {'PID':<8} {'进程名':<20} {'类型':<8} {'可执行文件':<30}")
            print("-" * 80)
            
            for i, proc in enumerate(processes[:20], 1):  # 只显示前20个
                proc_type = "系统" if proc['is_system'] else "用户"
                exe_path = proc['exe'][:27] + "..." if len(proc['exe']) > 30 else proc['exe']
                print(f"{i:<4} {proc['pid']:<8} {proc['name']:<20} {proc_type:<8} {exe_path:<30}")
            
            if len(processes) > 20:
                print(f"... 还有 {len(processes) - 20} 个进程未显示")
            
            print("\n操作选项:")
            print("1. 添加到监控列表")
            print("2. 重新搜索")
            print("3. 返回主菜单")
            
            choice = input("请选择操作 (1-3): ").strip()
            
            if choice == '1':
                self.monitor.add_monitored_process(query)
                print(f"✅ 已添加 '{query}' 到监控列表")
                input("按回车键继续...")
            elif choice == '2':
                continue
            elif choice == '3':
                break
    
    def manage_monitored_processes(self) -> None:
        """
        管理监控进程
        """
        while True:
            self.clear_screen()
            self.display_header()
            print("\n⚙️  监控进程管理")
            
            monitored = list(self.monitor.monitored_processes)
            if not monitored:
                print("📝 当前没有指定监控进程（监控所有非系统进程）")
                print("\n1. 添加监控进程")
                print("2. 返回主菜单")
                
                choice = input("请选择操作 (1-2): ").strip()
                if choice == '1':
                    process_name = input("请输入要监控的进程名称或关键词: ").strip()
                    if process_name:
                        self.monitor.add_monitored_process(process_name)
                        print(f"✅ 已添加 '{process_name}' 到监控列表")
                        input("按回车键继续...")
                elif choice == '2':
                    break
            else:
                print("📋 当前监控的进程:")
                for i, proc_name in enumerate(monitored, 1):
                    print(f"  {i}. {proc_name}")
                
                print("\n操作选项:")
                print("1. 添加新的监控进程")
                print("2. 移除监控进程")
                print("3. 清空所有监控进程")
                print("4. 返回主菜单")
                
                choice = input("请选择操作 (1-4): ").strip()
                
                if choice == '1':
                    process_name = input("请输入要监控的进程名称或关键词: ").strip()
                    if process_name:
                        self.monitor.add_monitored_process(process_name)
                        print(f"✅ 已添加 '{process_name}' 到监控列表")
                        input("按回车键继续...")
                elif choice == '2':
                    try:
                        idx = int(input("请输入要移除的进程序号: ")) - 1
                        if 0 <= idx < len(monitored):
                            removed = monitored[idx]
                            self.monitor.remove_monitored_process(removed)
                            print(f"✅ 已移除 '{removed}' 从监控列表")
                        else:
                            print("❌ 无效的序号")
                    except ValueError:
                        print("❌ 请输入有效的数字")
                    input("按回车键继续...")
                elif choice == '3':
                    confirm = input("确认清空所有监控进程？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.monitor.monitored_processes.clear()
                        self.monitor._save_config()
                        print("✅ 已清空所有监控进程")
                    input("按回车键继续...")
                elif choice == '4':
                    break
    
    def view_history(self) -> None:
        """
        查看历史记录
        """
        self.clear_screen()
        self.display_header()
        print("\n📜 历史记录")
        
        history = self.monitor.get_history(50)
        if not history:
            print("📝 暂无历史记录")
            input("按回车键继续...")
            return
        
        print(f"📊 显示最近 {len(history)} 条记录:")
        print("-" * 100)
        print(f"{'时间':<20} {'操作':<10} {'进程名':<20} {'PID':<8} {'结果':<15} {'原因':<10}")
        print("-" * 100)
        
        for record in history:
            timestamp = record['timestamp'][:19].replace('T', ' ')
            action = record['action']
            process_info = record.get('process', {})
            process_name = process_info.get('name', 'Unknown')[:18]
            pid = str(process_info.get('pid', 'N/A'))
            result = record.get('result', 'Unknown')[:13]
            reason = record.get('reason', 'N/A')[:8]
            
            print(f"{timestamp:<20} {action:<10} {process_name:<20} {pid:<8} {result:<15} {reason:<10}")
        
        input("\n按回车键继续...")
    
    def view_network_processes(self) -> None:
        """
        查看网络进程
        """
        self.clear_screen()
        self.display_header()
        print("\n🌐 网络进程")
        
        print("🔍 正在获取网络连接信息...")
        network_processes = self.monitor.get_network_processes()
        
        if not network_processes:
            print("📝 未找到网络进程或无权限访问")
            input("按回车键继续...")
            return
        
        print(f"\n📊 找到 {len(network_processes)} 个网络进程:")
        print("-" * 120)
        print(f"{'PID':<8} {'进程名':<20} {'本地地址':<25} {'远程地址':<25} {'状态':<15} {'类型':<10}")
        print("-" * 120)
        
        for proc in network_processes[:30]:  # 只显示前30个
            conn = proc.get('connection', {})
            pid = str(proc.get('pid', 'N/A'))
            name = proc.get('name', 'Unknown')[:18]
            local_addr = conn.get('local_address', 'N/A')[:23]
            remote_addr = conn.get('remote_address', 'N/A')[:23]
            status = conn.get('status', 'N/A')[:13]
            conn_type = conn.get('type', 'N/A')[:8]
            
            print(f"{pid:<8} {name:<20} {local_addr:<25} {remote_addr:<25} {status:<15} {conn_type:<10}")
        
        if len(network_processes) > 30:
            print(f"... 还有 {len(network_processes) - 30} 个网络进程未显示")
        
        input("\n按回车键继续...")
    
    def monitor_settings(self) -> None:
        """
        监控设置
        """
        while True:
            self.clear_screen()
            self.display_header()
            print("\n⚙️  监控设置")
            
            batch_settings = self.monitor.get_batch_settings()
            print(f"当前设置:")
            print(f"  超时时间: {self.monitor.timeout} 秒")
            print(f"  检查间隔: {self.monitor.check_interval} 秒")
            print(f"  网络监控: {'开启' if self.monitor.monitor_network else '关闭'}")
            print(f"  批量处理: {'开启' if batch_settings['batch_mode'] else '关闭'}")
            print(f"  全局终止限制: {batch_settings['max_terminate_count'] if batch_settings['max_terminate_count'] != -1 else '无限制'}")
            
            if batch_settings['process_terminate_limits']:
                print("  进程终止限制:")
                for proc_name, limit in batch_settings['process_terminate_limits'].items():
                    print(f"    {proc_name}: {limit}")
            
            print("\n设置选项:")
            print("1. 修改超时时间")
            print("2. 修改检查间隔")
            print("3. 批量处理设置")
            print("4. 进程终止数量设置")
            print("5. 切换网络监控")
            print("6. 返回主菜单")
            
            choice = input("请选择操作 (1-6): ").strip()
            
            if choice == '1':
                try:
                    new_timeout = int(input(f"请输入新的超时时间（当前: {self.monitor.timeout}秒）: "))
                    if new_timeout > 0:
                        self.monitor.timeout = new_timeout
                        print(f"✅ 超时时间已设置为 {new_timeout} 秒")
                    else:
                        print("❌ 超时时间必须大于0")
                except ValueError:
                    print("❌ 请输入有效的数字")
                input("按回车键继续...")
            elif choice == '2':
                try:
                    new_interval = int(input(f"请输入新的检查间隔（当前: {self.monitor.check_interval}秒）: "))
                    if new_interval > 0:
                        self.monitor.check_interval = new_interval
                        print(f"✅ 检查间隔已设置为 {new_interval} 秒")
                    else:
                        print("❌ 检查间隔必须大于0")
                except ValueError:
                    print("❌ 请输入有效的数字")
                input("按回车键继续...")
            elif choice == '3':
                self.batch_processing_settings()
            elif choice == '4':
                self.process_limit_settings()
            elif choice == '5':
                self.monitor.monitor_network = not self.monitor.monitor_network
                self.monitor._save_config()
                status = "开启" if self.monitor.monitor_network else "关闭"
                print(f"✅ 网络监控已{status}")
                input("按回车键继续...")
            elif choice == '6':
                break
    
    def toggle_monitoring(self) -> None:
        """
        启动/停止监控
        """
        status = self.monitor.get_status()
        
        if status['is_running']:
            print("🛑 正在停止监控...")
            self.monitor.stop_monitoring()
            print("✅ 监控已停止")
        else:
            print("🚀 正在启动监控...")
            self.monitor.start_monitoring()
            print("✅ 监控已启动")
        
        input("按回车键继续...")
    
    def start_status_display(self) -> None:
        """
        启动状态显示线程
        """
        def status_loop():
            while self.show_status and self.running:
                time.sleep(2)
                if self.show_status:
                    # 这里可以添加实时状态更新逻辑
                    pass
        
        self.show_status = True
        self.status_thread = threading.Thread(target=status_loop, daemon=True)
        self.status_thread.start()
    
    def stop_status_display(self) -> None:
        """
        停止状态显示线程
        """
        self.show_status = False
        if self.status_thread and self.status_thread.is_alive():
            self.status_thread.join(timeout=1)
    
    def run(self) -> None:
        """
        运行交互式菜单
        """
        try:
            while self.running:
                self.clear_screen()
                self.display_header()
                self.display_main_menu()
                
                choice = input("请选择操作 (0-9): ").strip()
                
                if choice == '1':
                    self.search_processes_menu()
                elif choice == '2':
                    process_name = input("请输入要监控的进程名称或关键词: ").strip()
                    if process_name:
                        self.monitor.add_monitored_process(process_name)
                        print(f"✅ 已添加 '{process_name}' 到监控列表")
                        input("按回车键继续...")
                elif choice == '3':
                    self.manage_monitored_processes()
                elif choice == '4':
                    status = self.monitor.get_status()
                    print("\n📊 监控状态详情:")
                    for key, value in status.items():
                        print(f"  {key}: {value}")
                    input("按回车键继续...")
                elif choice == '5':
                    self.view_history()
                elif choice == '6':
                    self.view_network_processes()
                elif choice == '7':
                    self.monitor_settings()
                elif choice == '8':
                    self.toggle_monitoring()
                elif choice == '9':
                    confirm = input("确认清理历史记录？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.monitor.clear_history()
                        print("✅ 历史记录已清理")
                        input("按回车键继续...")
                elif choice == '0':
                    print("👋 感谢使用进程监控工具！")
                    self.running = False
                else:
                    print("❌ 无效的选择，请重新输入")
                    input("按回车键继续...")
        
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，正在退出...")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")
        finally:
            self.stop_status_display()
            if self.monitor.is_running:
                self.monitor.stop_monitoring()
    
    def batch_processing_settings(self) -> None:
        """
        批量处理设置菜单
        """
        while True:
            self.clear_screen()
            self.display_header()
            print("\n🔄 批量处理设置")
            
            batch_settings = self.monitor.get_batch_settings()
            print(f"当前状态: {'开启' if batch_settings['batch_mode'] else '关闭'}")
            print(f"全局终止限制: {batch_settings['max_terminate_count'] if batch_settings['max_terminate_count'] != -1 else '无限制'}")
            
            print("\n📋 说明:")
            print("• 批量处理模式: 同时处理所有同名进程，而不是逐个处理")
            print("• 全局终止限制: 每个进程名最多终止的进程数量")
            print("• -1 表示无限制，会终止所有符合条件的进程")
            
            print("\n操作选项:")
            print("1. 切换批量处理模式")
            print("2. 设置全局终止限制")
            print("3. 返回上级菜单")
            
            choice = input("请选择操作 (1-3): ").strip()
            
            if choice == '1':
                new_mode = not batch_settings['batch_mode']
                self.monitor.set_batch_mode(new_mode)
                status = "开启" if new_mode else "关闭"
                print(f"✅ 批量处理模式已{status}")
                input("按回车键继续...")
            elif choice == '2':
                try:
                    print("\n请输入全局终止限制数量:")
                    print("• 输入 -1 表示无限制")
                    print("• 输入正整数表示最大终止数量")
                    limit = int(input("请输入: "))
                    if limit >= -1:
                        self.monitor.set_max_terminate_count(limit)
                        limit_text = "无限制" if limit == -1 else str(limit)
                        print(f"✅ 全局终止限制已设置为: {limit_text}")
                    else:
                        print("❌ 请输入 -1 或正整数")
                except ValueError:
                    print("❌ 请输入有效的数字")
                input("按回车键继续...")
            elif choice == '3':
                break
    
    def process_limit_settings(self) -> None:
        """
        进程终止数量设置菜单
        """
        while True:
            self.clear_screen()
            self.display_header()
            print("\n🎯 进程终止数量设置")
            
            batch_settings = self.monitor.get_batch_settings()
            limits = batch_settings['process_terminate_limits']
            
            if limits:
                print("\n📋 当前进程限制:")
                for i, (proc_name, limit) in enumerate(limits.items(), 1):
                    print(f"  {i}. {proc_name}: {limit}")
            else:
                print("\n📝 当前没有设置特定进程的终止限制")
            
            print(f"\n全局默认限制: {batch_settings['max_terminate_count'] if batch_settings['max_terminate_count'] != -1 else '无限制'}")
            
            print("\n📋 说明:")
            print("• 可以为特定进程名设置独立的终止数量限制")
            print("• 例如: node 进程限制为 5，表示最多终止 5 个 node 进程")
            print("• 特定限制优先于全局限制")
            
            print("\n操作选项:")
            print("1. 添加进程限制")
            if limits:
                print("2. 修改进程限制")
                print("3. 删除进程限制")
                print("4. 清空所有限制")
                print("5. 返回上级菜单")
            else:
                print("2. 返回上级菜单")
            
            max_choice = 5 if limits else 2
            choice = input(f"请选择操作 (1-{max_choice}): ").strip()
            
            if choice == '1':
                proc_name = input("请输入进程名称 (如: node, python, chrome): ").strip().lower()
                if proc_name:
                    try:
                        print("\n请输入终止数量限制:")
                        print("• 输入 -1 表示无限制（删除该进程的特定限制）")
                        print("• 输入正整数表示最大终止数量")
                        limit = int(input("请输入: "))
                        if limit >= -1:
                            self.monitor.set_process_terminate_limit(proc_name, limit)
                            if limit == -1:
                                print(f"✅ 已删除进程 '{proc_name}' 的特定限制")
                            else:
                                print(f"✅ 进程 '{proc_name}' 的终止限制已设置为: {limit}")
                        else:
                            print("❌ 请输入 -1 或正整数")
                    except ValueError:
                        print("❌ 请输入有效的数字")
                else:
                    print("❌ 进程名称不能为空")
                input("按回车键继续...")
            elif choice == '2' and limits:
                try:
                    idx = int(input("请输入要修改的进程序号: ")) - 1
                    proc_names = list(limits.keys())
                    if 0 <= idx < len(proc_names):
                        proc_name = proc_names[idx]
                        current_limit = limits[proc_name]
                        print(f"\n当前 '{proc_name}' 的限制: {current_limit}")
                        try:
                            limit = int(input("请输入新的限制数量 (-1表示无限制): "))
                            if limit >= -1:
                                self.monitor.set_process_terminate_limit(proc_name, limit)
                                if limit == -1:
                                    print(f"✅ 已删除进程 '{proc_name}' 的特定限制")
                                else:
                                    print(f"✅ 进程 '{proc_name}' 的终止限制已更新为: {limit}")
                            else:
                                print("❌ 请输入 -1 或正整数")
                        except ValueError:
                            print("❌ 请输入有效的数字")
                    else:
                        print("❌ 无效的序号")
                except ValueError:
                    print("❌ 请输入有效的数字")
                input("按回车键继续...")
            elif choice == '3' and limits:
                try:
                    idx = int(input("请输入要删除的进程序号: ")) - 1
                    proc_names = list(limits.keys())
                    if 0 <= idx < len(proc_names):
                        proc_name = proc_names[idx]
                        self.monitor.set_process_terminate_limit(proc_name, -1)
                        print(f"✅ 已删除进程 '{proc_name}' 的特定限制")
                    else:
                        print("❌ 无效的序号")
                except ValueError:
                    print("❌ 请输入有效的数字")
                input("按回车键继续...")
            elif choice == '4' and limits:
                confirm = input("确认清空所有进程限制？(y/N): ").strip().lower()
                if confirm == 'y':
                    self.monitor.clear_process_limits()
                    print("✅ 已清空所有进程的终止限制")
                input("按回车键继续...")
            elif (choice == '5' and limits) or (choice == '2' and not limits):
                break