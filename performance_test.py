#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py-process-monitor 性能测试

这个脚本测试进程监控工具在不同负载下的性能表现。
"""

import os
import sys
import time
import threading
import subprocess
from typing import List

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_monitor import ProcessMonitor
from process_monitor.utils import get_system_info, get_current_time_info


class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.results = []
        
    def test_search_performance(self):
        """测试搜索性能"""
        print("\n🔍 测试进程搜索性能...")
        monitor = ProcessMonitor()
        
        # 测试不同查询的搜索时间
        queries = ["python", "node", "chrome", "system", "kernel", "nonexistent"]
        
        for query in queries:
            start_time = time.time()
            results = monitor.search_processes(query)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # 转换为毫秒
            print(f"  查询 '{query}': {len(results)} 个结果, 耗时 {duration:.2f}ms")
            
            self.results.append({
                'test': 'search',
                'query': query,
                'results_count': len(results),
                'duration_ms': duration
            })
    
    def test_status_performance(self):
        """测试状态获取性能"""
        print("\n📊 测试状态获取性能...")
        monitor = ProcessMonitor()
        
        # 添加一些监控进程
        test_processes = ["python", "node", "chrome", "firefox", "safari"]
        for proc in test_processes:
            monitor.add_monitored_process(proc)
        
        # 测试状态获取时间
        iterations = 10
        total_time = 0
        
        for i in range(iterations):
            start_time = time.time()
            status = monitor.get_status()
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000
            total_time += duration
        
        avg_time = total_time / iterations
        print(f"  平均状态获取时间: {avg_time:.2f}ms (测试 {iterations} 次)")
        
        self.results.append({
            'test': 'status',
            'iterations': iterations,
            'avg_duration_ms': avg_time
        })
    
    def test_config_performance(self):
        """测试配置文件操作性能"""
        print("\n⚙️ 测试配置文件操作性能...")
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config = f.name
        
        try:
            monitor = ProcessMonitor(config_file=temp_config)
            
            # 添加大量监控进程
            test_processes = [f"test_process_{i}" for i in range(100)]
            
            # 测试添加进程和保存配置的时间
            start_time = time.time()
            for proc in test_processes:
                monitor.add_monitored_process(proc)
            monitor._save_config()
            end_time = time.time()
            
            save_duration = (end_time - start_time) * 1000
            print(f"  添加 {len(test_processes)} 个进程并保存配置: {save_duration:.2f}ms")
            
            # 测试加载配置的时间
            new_monitor = ProcessMonitor(config_file=temp_config)
            start_time = time.time()
            new_monitor._load_config()
            end_time = time.time()
            
            load_duration = (end_time - start_time) * 1000
            print(f"  加载包含 {len(test_processes)} 个进程的配置: {load_duration:.2f}ms")
            
            self.results.append({
                'test': 'config_save',
                'processes_count': len(test_processes),
                'duration_ms': save_duration
            })
            
            self.results.append({
                'test': 'config_load',
                'processes_count': len(test_processes),
                'duration_ms': load_duration
            })
            
        finally:
            if os.path.exists(temp_config):
                os.unlink(temp_config)
    
    def test_concurrent_operations(self):
        """测试并发操作性能"""
        print("\n🔄 测试并发操作性能...")
        monitor = ProcessMonitor()
        
        def search_worker(query, results_list):
            """搜索工作线程"""
            start_time = time.time()
            results = monitor.search_processes(query)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000
            results_list.append({
                'query': query,
                'results_count': len(results),
                'duration_ms': duration
            })
        
        # 创建多个并发搜索线程
        queries = ["python", "node", "chrome", "system"] * 3  # 12个查询
        threads = []
        concurrent_results = []
        
        start_time = time.time()
        
        for query in queries:
            thread = threading.Thread(target=search_worker, args=(query, concurrent_results))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        print(f"  {len(queries)} 个并发搜索总耗时: {total_duration:.2f}ms")
        print(f"  平均每个搜索耗时: {sum(r['duration_ms'] for r in concurrent_results) / len(concurrent_results):.2f}ms")
        
        self.results.append({
            'test': 'concurrent_search',
            'concurrent_count': len(queries),
            'total_duration_ms': total_duration,
            'avg_duration_ms': sum(r['duration_ms'] for r in concurrent_results) / len(concurrent_results)
        })
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        print("\n💾 测试内存使用情况...")
        
        try:
            import psutil
            process = psutil.Process()
            
            # 获取初始内存使用
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            monitor = ProcessMonitor()
            
            # 执行一些操作
            for i in range(50):
                monitor.search_processes("python")
                monitor.add_monitored_process(f"test_{i}")
                monitor.get_status()
            
            # 获取操作后内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"  初始内存使用: {initial_memory:.2f} MB")
            print(f"  操作后内存使用: {final_memory:.2f} MB")
            print(f"  内存增长: {memory_increase:.2f} MB")
            
            self.results.append({
                'test': 'memory_usage',
                'initial_mb': initial_memory,
                'final_mb': final_memory,
                'increase_mb': memory_increase
            })
            
        except ImportError:
            print("  ⚠️ psutil 不可用，跳过内存测试")
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("🚀 开始进程监控工具性能测试")
        print("="*60)
        
        # 显示系统信息
        system_info = get_system_info()
        time_info = get_current_time_info()
        
        print(f"💻 测试环境:")
        print(f"  操作系统: {system_info['os']} {system_info['architecture']}")
        print(f"  CPU核心数: {system_info['cpu_count']}")
        print(f"  总内存: {system_info['total_memory']}")
        print(f"  当前时间: {time_info['current_time']}")
        
        # 运行各项测试
        self.test_search_performance()
        self.test_status_performance()
        self.test_config_performance()
        self.test_concurrent_operations()
        self.test_memory_usage()
        
        # 显示测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印性能测试总结"""
        print("\n" + "="*60)
        print("📊 性能测试总结")
        print("="*60)
        
        # 按测试类型分组显示结果
        test_types = {}
        for result in self.results:
            test_type = result['test']
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        for test_type, results in test_types.items():
            print(f"\n🔍 {test_type.upper()} 测试:")
            for result in results:
                if 'duration_ms' in result:
                    print(f"  - 耗时: {result['duration_ms']:.2f}ms")
                if 'avg_duration_ms' in result:
                    print(f"  - 平均耗时: {result['avg_duration_ms']:.2f}ms")
                if 'results_count' in result:
                    print(f"  - 结果数量: {result['results_count']}")
                if 'increase_mb' in result:
                    print(f"  - 内存增长: {result['increase_mb']:.2f}MB")
        
        # 性能评估
        print("\n🎯 性能评估:")
        
        # 搜索性能评估
        search_results = [r for r in self.results if r['test'] == 'search']
        if search_results:
            avg_search_time = sum(r['duration_ms'] for r in search_results) / len(search_results)
            if avg_search_time < 100:
                print("  ✅ 搜索性能: 优秀 (< 100ms)")
            elif avg_search_time < 500:
                print("  🟡 搜索性能: 良好 (< 500ms)")
            else:
                print("  ❌ 搜索性能: 需要优化 (> 500ms)")
        
        # 内存使用评估
        memory_results = [r for r in self.results if r['test'] == 'memory_usage']
        if memory_results:
            memory_increase = memory_results[0]['increase_mb']
            if memory_increase < 10:
                print("  ✅ 内存使用: 优秀 (< 10MB)")
            elif memory_increase < 50:
                print("  🟡 内存使用: 良好 (< 50MB)")
            else:
                print("  ❌ 内存使用: 需要优化 (> 50MB)")


if __name__ == "__main__":
    test = PerformanceTest()
    test.run_all_tests()