#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import logging
import json
import os
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta

import psutil

from .utils import is_system_process, get_process_info, get_network_connections


class ProcessMonitor:
    """
    进程监控器类，用于监控和管理系统进程
    """
    
    def __init__(self, timeout: int = 30, check_interval: int = 5, log_level: str = "INFO", config_file: str = "process_monitor_config.json", dry_run: bool = False, verbose: bool = False):
        """
        初始化进程监控器
        
        Args:
            timeout: 进程超时时间（秒），默认30秒
            check_interval: 检查间隔（秒），默认5秒
            log_level: 日志级别，默认INFO
            config_file: 配置文件路径
            dry_run: 干运行模式，只检测不实际终止进程
            verbose: 详细输出模式
        """
        self.timeout = timeout
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.verbose = verbose
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.config_file = config_file
        
        # 存储进程的最后活动时间
        self.process_last_activity: Dict[int, datetime] = {}
        
        # 存储已知的系统进程PID
        self.system_processes: Set[int] = set()
        
        # 监控的进程名称列表（支持模糊匹配）
        self.monitored_processes: Set[str] = set()
        
        # 批量处理设置
        self.batch_mode = True  # 是否启用批量处理模式
        self.max_terminate_count = -1  # 每个进程名最大终止数量，-1表示全部
        self.process_terminate_limits: Dict[str, int] = {}  # 每个进程名的终止数量限制
        
        # 历史记录
        self.process_history: List[Dict] = []
        self.menu_history: List[str] = []
        
        # 网络连接监控
        self.monitor_network = False
        
        # 设置日志
        self._setup_logging(log_level)
        
        # 加载配置
        self._load_config()
        
        # 初始化系统进程列表
        self._initialize_system_processes()
    
    def _setup_logging(self, log_level: str) -> None:
        """
        设置日志配置
        """
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('process_monitor.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> None:
        """
        加载配置文件
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.monitored_processes = set(config.get('monitored_processes', []))
                    self.process_history = config.get('process_history', [])
                    self.menu_history = config.get('menu_history', [])
                    self.monitor_network = config.get('monitor_network', False)
                    # 加载批量处理设置
                    self.batch_mode = config.get('batch_mode', True)
                    self.max_terminate_count = config.get('max_terminate_count', -1)
                    self.process_terminate_limits = config.get('process_terminate_limits', {})
                    self.logger.info(f"已加载配置文件: {self.config_file}")
            else:
                self.logger.info("配置文件不存在，使用默认配置")
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
    
    def _save_config(self) -> None:
        """
        保存配置文件
        """
        try:
            config = {
                'monitored_processes': list(self.monitored_processes),
                'process_history': self.process_history[-100:],  # 只保留最近100条记录
                'menu_history': self.menu_history[-50:],  # 只保留最近50条菜单历史
                'monitor_network': self.monitor_network,
                # 保存批量处理设置
                'batch_mode': self.batch_mode,
                'max_terminate_count': self.max_terminate_count,
                'process_terminate_limits': self.process_terminate_limits
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def _initialize_system_processes(self) -> None:
        """
        初始化系统进程列表
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    if is_system_process(proc):
                        self.system_processes.add(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.logger.info(f"已识别 {len(self.system_processes)} 个系统进程")
        except Exception as e:
            self.logger.error(f"初始化系统进程列表时出错: {e}")
    
    def search_processes(self, query: str) -> List[Dict]:
        """
        搜索进程（支持模糊匹配）
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict]: 匹配的进程列表
        """
        matching_processes = []
        query_lower = query.lower()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    name = proc_info.get('name', '').lower()
                    exe = proc_info.get('exe', '').lower() if proc_info.get('exe') else ''
                    
                    # 安全处理cmdline
                    cmdline_raw = proc_info.get('cmdline', [])
                    if isinstance(cmdline_raw, list):
                        cmdline = ' '.join(cmdline_raw).lower()
                    else:
                        cmdline = str(cmdline_raw).lower() if cmdline_raw else ''
                    
                    # 模糊匹配：进程名、可执行文件路径、命令行参数
                    if (query_lower in name or 
                        query_lower in exe or 
                        query_lower in cmdline):
                        
                        process_data = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info.get('exe', ''),
                            'cmdline': proc_info.get('cmdline', []),
                            'is_system': is_system_process(proc)
                        }
                        matching_processes.append(process_data)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"搜索进程时出错: {e}")
        
        return matching_processes
    
    def add_monitored_process(self, process_name: str) -> None:
        """
        添加要监控的进程
        
        Args:
            process_name: 进程名称或关键词
        """
        self.monitored_processes.add(process_name)
        self._save_config()
        self.logger.info(f"已添加监控进程: {process_name}")
    
    def remove_monitored_process(self, process_name: str) -> None:
        """
        移除监控的进程
        
        Args:
            process_name: 进程名称或关键词
        """
        self.monitored_processes.discard(process_name)
        self._save_config()
        self.logger.info(f"已移除监控进程: {process_name}")
    
    def _is_monitored_process(self, proc: psutil.Process) -> bool:
        """
        检查进程是否在监控列表中
        
        Args:
            proc: psutil.Process对象
            
        Returns:
            bool: 是否在监控列表中
        """
        if not self.monitored_processes:
            return True  # 如果没有指定监控进程，则监控所有进程
        
        try:
            proc_info = proc.as_dict(['name', 'exe', 'cmdline'])
            name = proc_info.get('name', '').lower()
            exe = proc_info.get('exe', '').lower() if proc_info.get('exe') else ''
            cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
            
            for monitored in self.monitored_processes:
                monitored_lower = monitored.lower()
                if (monitored_lower in name or 
                    monitored_lower in exe or 
                    monitored_lower in cmdline):
                    return True
            
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _is_process_active(self, proc: psutil.Process) -> bool:
        """
        检查进程是否活跃
        
        Args:
            proc: psutil.Process对象
            
        Returns:
            bool: 进程是否活跃
        """
        try:
            # 检查进程状态
            status = proc.status()
            if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                return False
            
            # 检查CPU使用率（需要两次调用来获取准确值）
            cpu_percent = proc.cpu_percent()
            if cpu_percent > 0.1:  # CPU使用率大于0.1%认为是活跃的
                return True
            
            # 检查内存使用情况
            memory_info = proc.memory_info()
            if memory_info.rss > 0:  # 有内存使用
                # 检查是否有网络连接或文件操作
                try:
                    connections = proc.connections()
                    if connections:
                        return True
                    
                    open_files = proc.open_files()
                    if open_files:
                        return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
            
            return False
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def _should_terminate_process(self, proc: psutil.Process) -> bool:
        """
        判断是否应该终止进程
        
        Args:
            proc: psutil.Process对象
            
        Returns:
            bool: 是否应该终止
        """
        try:
            pid = proc.pid
            
            # 检查是否是系统进程
            if pid in self.system_processes or is_system_process(proc):
                return False
            
            # 检查是否在监控列表中
            if not self._is_monitored_process(proc):
                return False
            
            # 检查进程是否活跃
            if self._is_process_active(proc):
                # 进程活跃，更新最后活动时间
                self.process_last_activity[pid] = datetime.now()
                return False
            
            # 进程不活跃，检查是否超时
            current_time = datetime.now()
            if pid not in self.process_last_activity:
                # 第一次发现不活跃，记录时间
                self.process_last_activity[pid] = current_time
                return False
            
            # 检查是否超过超时时间
            inactive_duration = current_time - self.process_last_activity[pid]
            if inactive_duration.total_seconds() > self.timeout:
                return True
            
            return False
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _terminate_process(self, proc: psutil.Process) -> bool:
        """
        终止进程
        
        Args:
            proc: psutil.Process对象
            
        Returns:
            bool: 是否成功终止
        """
        try:
            proc_info = get_process_info(proc)
            
            # 记录到历史
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'terminate' if not self.dry_run else 'dry_run_terminate',
                'process': proc_info,
                'reason': 'timeout'
            }
            self.process_history.append(history_entry)
            
            if self.dry_run:
                # 干运行模式，只记录不实际终止
                if self.verbose:
                    print(f"[干运行] 将要终止进程: {proc_info}")
                self.logger.info(f"[干运行] 将要终止进程: {proc_info}")
                history_entry['result'] = 'dry_run'
                return True
            
            self.logger.warning(f"准备终止进程: {proc_info}")
            if self.verbose:
                print(f"终止进程: {proc_info}")
            
            # 首先尝试优雅终止
            proc.terminate()
            
            # 等待进程终止
            try:
                proc.wait(timeout=5)
                self.logger.info(f"成功终止进程: {proc_info}")
                if self.verbose:
                    print(f"成功终止进程: {proc_info}")
                history_entry['result'] = 'success'
                return True
            except psutil.TimeoutExpired:
                # 如果优雅终止失败，强制杀死
                self.logger.warning(f"优雅终止失败，强制杀死进程: {proc_info}")
                if self.verbose:
                    print(f"强制杀死进程: {proc_info}")
                proc.kill()
                proc.wait(timeout=3)
                self.logger.info(f"强制杀死进程: {proc_info}")
                history_entry['result'] = 'force_killed'
                return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
            self.logger.error(f"终止进程失败: {e}")
            if 'history_entry' in locals():
                history_entry['result'] = f'failed: {e}'
            return False
    
    def _monitor_loop(self) -> None:
        """
        监控循环
        """
        self.logger.info("开始进程监控")
        
        while self.is_running:
            try:
                current_processes = set()
                terminated_count = 0
                
                if self.batch_mode:
                    # 批量处理模式：按进程名分组处理
                    process_groups = {}
                    
                    # 收集所有需要处理的进程，按名称分组
                    for proc in psutil.process_iter():
                        try:
                            current_processes.add(proc.pid)
                            
                            if self._should_terminate_process(proc):
                                proc_name = proc.name().lower()
                                if proc_name not in process_groups:
                                    process_groups[proc_name] = []
                                process_groups[proc_name].append(proc)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    # 批量处理每组进程
                    for proc_name, processes in process_groups.items():
                        # 获取该进程名的终止数量限制
                        limit = self.process_terminate_limits.get(proc_name, self.max_terminate_count)
                        
                        # 如果限制为-1，处理所有进程；否则只处理指定数量
                        processes_to_terminate = processes if limit == -1 else processes[:limit]
                        
                        for proc in processes_to_terminate:
                            try:
                                if self._terminate_process(proc):
                                    terminated_count += 1
                                    # 从跟踪列表中移除
                                    self.process_last_activity.pop(proc.pid, None)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                        
                        if len(processes_to_terminate) > 0:
                            self.logger.info(f"批量处理 '{proc_name}': 终止了 {len(processes_to_terminate)} 个进程")
                else:
                    # 单个处理模式：逐个处理进程
                    for proc in psutil.process_iter():
                        try:
                            current_processes.add(proc.pid)
                            
                            if self._should_terminate_process(proc):
                                if self._terminate_process(proc):
                                    terminated_count += 1
                                    # 从跟踪列表中移除
                                    self.process_last_activity.pop(proc.pid, None)
                        
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                
                # 清理已不存在的进程记录
                existing_pids = set(self.process_last_activity.keys())
                for pid in existing_pids - current_processes:
                    self.process_last_activity.pop(pid, None)
                
                if terminated_count > 0:
                    self.logger.info(f"本轮监控终止了 {terminated_count} 个进程")
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环中出现错误: {e}")
                time.sleep(self.check_interval)
        
        self.logger.info("进程监控已停止")
    
    def start_monitoring(self) -> None:
        """
        启动进程监控
        """
        if self.is_running:
            self.logger.warning("监控已在运行中")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"进程监控已启动 - 超时时间: {self.timeout}秒, 检查间隔: {self.check_interval}秒")
    
    def stop_monitoring(self) -> None:
        """
        停止进程监控
        """
        if not self.is_running:
            self.logger.warning("监控未在运行")
            return
        
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("进程监控已停止")
    
    def get_status(self) -> Dict:
        """
        获取监控状态
        
        Returns:
            Dict: 监控状态信息
        """
        return {
            "is_running": self.is_running,
            "timeout": self.timeout,
            "check_interval": self.check_interval,
            "tracked_processes": len(self.process_last_activity),
            "system_processes": len(self.system_processes),
            "monitored_processes": list(self.monitored_processes),
            "monitor_network": self.monitor_network,
            "history_count": len(self.process_history),
            "menu_history_count": len(self.menu_history)
        }
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """
        获取历史记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 历史记录列表
        """
        return self.process_history[-limit:] if self.process_history else []
    
    def clear_history(self) -> None:
        """
        清空历史记录
        """
        self.process_history.clear()
        self._save_config()
        self.logger.info("历史记录已清空")
    
    def get_network_processes(self) -> List[Dict]:
        """
        获取有网络连接的进程
        
        Returns:
            List[Dict]: 网络进程列表
        """
        network_processes = []
        try:
            connections = get_network_connections()
            for conn in connections:
                if conn.get('pid'):
                    try:
                        proc = psutil.Process(conn['pid'])
                        proc_info = get_process_info(proc)
                        proc_info['connection'] = conn
                        network_processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            self.logger.error(f"获取网络进程失败: {e}")
        
        return network_processes
    
    def set_batch_mode(self, enabled: bool) -> None:
        """
        设置批量处理模式
        
        Args:
            enabled: 是否启用批量处理
        """
        self.batch_mode = enabled
        self._save_config()
        self.logger.info(f"批量处理模式已{'启用' if enabled else '禁用'}")
    
    def set_max_terminate_count(self, count: int) -> None:
        """
        设置全局最大终止数量
        
        Args:
            count: 最大终止数量，-1表示无限制
        """
        self.max_terminate_count = count
        self._save_config()
        self.logger.info(f"全局最大终止数量设置为: {count if count != -1 else '无限制'}")
    
    def set_process_terminate_limit(self, process_name: str, limit: int) -> None:
        """
        设置特定进程的终止数量限制
        
        Args:
            process_name: 进程名称
            limit: 终止数量限制，-1表示无限制
        """
        if limit == -1:
            self.process_terminate_limits.pop(process_name.lower(), None)
        else:
            self.process_terminate_limits[process_name.lower()] = limit
        self._save_config()
        self.logger.info(f"进程 '{process_name}' 的终止数量限制设置为: {limit if limit != -1 else '无限制'}")
    
    def get_batch_settings(self) -> Dict:
        """
        获取批量处理设置
        
        Returns:
            Dict: 批量处理设置信息
        """
        return {
            'batch_mode': self.batch_mode,
            'max_terminate_count': self.max_terminate_count,
            'process_terminate_limits': dict(self.process_terminate_limits)
        }
    
    def clear_process_limits(self) -> None:
        """
        清空所有进程的终止数量限制
        """
        self.process_terminate_limits.clear()
        self._save_config()
        self.logger.info("已清空所有进程的终止数量限制")