#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import time
from typing import Dict, Any, Set, List

import psutil


# 系统进程名称列表（根据不同操作系统）
SYSTEM_PROCESS_NAMES = {
    'Darwin': {  # macOS
        'kernel_task', 'launchd', 'kextd', 'UserEventAgent', 'cfprefsd',
        'loginwindow', 'WindowServer', 'Dock', 'Finder', 'SystemUIServer',
        'coreaudiod', 'bluetoothd', 'WiFiAgent', 'networkd', 'mDNSResponder',
        'syslogd', 'diskarbitrationd', 'configd', 'powerd', 'thermald',
        'kernel', 'ksecdd', 'csrss', 'winlogon', 'services', 'lsass',
        'spoolsv', 'explorer', 'dwm', 'audiodg', 'conhost'
    },
    'Linux': {
        'init', 'kthreadd', 'ksoftirqd', 'migration', 'rcu_', 'watchdog',
        'systemd', 'dbus', 'NetworkManager', 'sshd', 'cron', 'rsyslog',
        'udev', 'kernel', 'kworker', 'ksoftirqd', 'migration', 'rcu_gp',
        'rcu_par_gp', 'kcompactd', 'oom_reaper', 'khugepaged'
    },
    'Windows': {
        'System', 'smss.exe', 'csrss.exe', 'wininit.exe', 'winlogon.exe',
        'services.exe', 'lsass.exe', 'svchost.exe', 'spoolsv.exe',
        'explorer.exe', 'dwm.exe', 'audiodg.exe', 'conhost.exe'
    }
}

# 系统用户名列表
SYSTEM_USERS = {
    'root', 'daemon', 'bin', 'sys', 'sync', 'games', 'man', 'lp',
    'mail', 'news', 'uucp', 'proxy', 'www-data', 'backup', 'list',
    'irc', 'gnats', 'nobody', '_system', '_daemon', '_unknown',
    'SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE'
}

# 重要的系统目录
SYSTEM_DIRECTORIES = {
    'Darwin': {'/System/', '/usr/libexec/', '/sbin/', '/usr/sbin/'},
    'Linux': {'/sbin/', '/usr/sbin/', '/bin/', '/usr/bin/', '/lib/', '/usr/lib/'},
    'Windows': {'C:\\Windows\\System32\\', 'C:\\Windows\\SysWOW64\\'}
}


def is_system_process(proc: psutil.Process) -> bool:
    """
    判断进程是否为系统进程
    
    Args:
        proc: psutil.Process对象
        
    Returns:
        bool: 是否为系统进程
    """
    try:
        # 获取进程信息
        proc_info = proc.as_dict(['pid', 'name', 'username', 'exe', 'ppid'])
        
        pid = proc_info.get('pid', 0)
        name = proc_info.get('name', '').lower()
        username = proc_info.get('username', '')
        exe_path = proc_info.get('exe', '')
        ppid = proc_info.get('ppid', 0)
        
        # 1. PID为0或1的进程通常是系统进程
        if pid <= 1:
            return True
        
        # 2. 检查进程名称
        system_names = SYSTEM_PROCESS_NAMES.get(platform.system(), set())
        if any(sys_name.lower() in name for sys_name in system_names):
            return True
        
        # 3. 检查用户名
        if username and any(sys_user.lower() in username.lower() for sys_user in SYSTEM_USERS):
            return True
        
        # 4. 检查可执行文件路径
        if exe_path:
            system_dirs = SYSTEM_DIRECTORIES.get(platform.system(), set())
            if any(exe_path.startswith(sys_dir) for sys_dir in system_dirs):
                return True
        
        # 5. 检查父进程（如果父进程是系统进程，子进程可能也是）
        if ppid <= 1:
            return True
        
        # 6. macOS特定检查
        if platform.system() == 'Darwin':
            # 检查是否是内核线程
            if name.startswith('kernel') or '[' in name and ']' in name:
                return True
            
            # 检查是否是系统守护进程
            if name.endswith('d') and len(name) > 3:  # 很多系统守护进程以'd'结尾
                return True
        
        # 7. Linux特定检查
        elif platform.system() == 'Linux':
            # 检查是否是内核线程
            if name.startswith('[') and name.endswith(']'):
                return True
            
            # 检查是否是kthread
            if name.startswith('k') and any(keyword in name for keyword in ['worker', 'thread', 'soft']):
                return True
        
        # 8. Windows特定检查
        elif platform.system() == 'Windows':
            # 检查是否是Windows系统进程
            if name in ['system idle process', 'system interrupts']:
                return True
        
        # 9. 检查进程是否具有特殊权限
        try:
            # 尝试获取进程的详细信息，如果无法访问可能是系统进程
            proc.memory_info()
            proc.cpu_times()
        except psutil.AccessDenied:
            # 如果无法访问进程信息，可能是系统进程
            return True
        
        return False
        
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return True  # 无法访问的进程当作系统进程处理
    except Exception:
        return False


def get_process_info(proc: psutil.Process) -> Dict[str, Any]:
    """
    获取进程详细信息
    
    Args:
        proc: psutil.Process对象
        
    Returns:
        Dict: 进程信息字典
    """
    try:
        info = proc.as_dict([
            'pid', 'name', 'username', 'exe', 'cmdline',
            'create_time', 'status', 'cpu_percent', 'memory_percent'
        ])
        
        # 添加额外信息
        try:
            info['memory_info'] = proc.memory_info()._asdict()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info['memory_info'] = None
        
        try:
            info['cpu_times'] = proc.cpu_times()._asdict()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info['cpu_times'] = None
        
        # 格式化创建时间
        if info.get('create_time'):
            import datetime
            info['create_time_formatted'] = datetime.datetime.fromtimestamp(
                info['create_time']
            ).strftime('%Y-%m-%d %H:%M:%S')
        
        return info
        
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        return {
            'pid': getattr(proc, 'pid', None),
            'error': str(e),
            'name': 'Unknown',
            'status': 'Error'
        }


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        Dict: 系统信息字典
    """
    return {
        'os': platform.system(),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'total_memory': format_bytes(psutil.virtual_memory().total),
        'boot_time': psutil.boot_time()
    }


def is_safe_to_terminate(proc: psutil.Process) -> bool:
    """
    检查进程是否可以安全终止
    
    Args:
        proc: psutil.Process对象
        
    Returns:
        bool: 是否可以安全终止
    """
    try:
        # 系统进程不能终止
        if is_system_process(proc):
            return False
        
        # 检查进程是否是当前Python进程或其父进程
        current_pid = os.getpid()
        if proc.pid == current_pid:
            return False
        
        # 检查是否是父进程
        try:
            current_proc = psutil.Process(current_pid)
            if proc.pid == current_proc.ppid():
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # 检查是否是重要的用户进程（如IDE、浏览器等）
        proc_info = proc.as_dict(['name', 'exe'])
        name = proc_info.get('name', '').lower()
        exe = proc_info.get('exe', '').lower()
        
        # 重要应用程序列表
        important_apps = {
            'code', 'vscode', 'pycharm', 'intellij', 'eclipse', 'atom',
            'sublime', 'vim', 'emacs', 'chrome', 'firefox', 'safari',
            'terminal', 'iterm', 'cmd', 'powershell', 'bash', 'zsh',
            'ssh', 'docker', 'mysql', 'postgres', 'redis', 'mongodb'
        }
        
        if any(app in name or app in exe for app in important_apps):
            return False
        
        return True
        
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def format_bytes(bytes_value: int) -> str:
    """
    格式化字节数为人类可读格式
    
    Args:
        bytes_value: 字节数
        
    Returns:
        str: 格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f}分钟"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}小时"
    else:
        return f"{seconds/86400:.1f}天"


def get_network_connections() -> List[Dict[str, Any]]:
    """
    获取网络连接信息
    
    Returns:
        List[Dict]: 网络连接列表
    """
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            conn_info = {
                'fd': conn.fd,
                'family': conn.family.name if conn.family else None,
                'type': conn.type.name if conn.type else None,
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            }
            connections.append(conn_info)
    except (psutil.AccessDenied, PermissionError):
        # 如果没有权限获取所有连接，尝试获取当前进程的连接
        try:
            current_proc = psutil.Process()
            for conn in current_proc.connections():
                conn_info = {
                    'fd': conn.fd,
                    'family': conn.family.name if conn.family else None,
                    'type': conn.type.name if conn.type else None,
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': current_proc.pid
                }
                connections.append(conn_info)
        except Exception:
            pass
    except Exception as e:
        print(f"获取网络连接时出错: {e}")
    
    return connections


def get_current_time_info() -> Dict[str, Any]:
    """
    获取当前时间和系统信息
    
    Returns:
        Dict: 时间和系统信息
    """
    import datetime
    now = datetime.datetime.now()
    
    return {
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp': now.timestamp(),
        'weekday': now.strftime('%A'),
        'os': platform.system(),
        'system_uptime': format_duration(time.time() - psutil.boot_time()),
        'cpu_count': psutil.cpu_count(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent
    }