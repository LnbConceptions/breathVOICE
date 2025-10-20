# BreathVOICE API 可用性测试指南

## 概述

本文档提供完整的 BreathVOICE API 可用性测试方案，包括自动化测试脚本、手动测试清单和性能基准测试。

**测试目标**: 确保 `https://tts.ioioioioio.com:1120` 上的 BreathVOICE API 功能完整、稳定、高效。

## 测试环境要求

### 软件依赖
```bash
pip install requests pytest pytest-html pytest-json-report
```

### 测试数据准备
```
test_data/
├── sample_texts.json          # 测试文本数据
├── test_voice_group.zip       # 测试角色组ZIP文件
└── expected_responses.json    # 预期响应数据
```

## 自动化测试脚本

### 1. 基础连通性测试

```python
import requests
import pytest
import time
import json
from typing import Dict, List, Optional

class BreathVOICEAPITester:
    """BreathVOICE API 测试类"""
    
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_basic_connectivity(self) -> Dict:
        """测试基础连通性"""
        test_results = {
            "test_name": "基础连通性测试",
            "tests": []
        }
        
        # 测试根端点
        try:
            response = self.session.get(f"{self.base_url}/")
            test_results["tests"].append({
                "endpoint": "/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else response.text
            })
        except Exception as e:
            test_results["tests"].append({
                "endpoint": "/",
                "status_code": None,
                "success": False,
                "response_time": None,
                "error": str(e)
            })
        
        # 测试健康检查端点
        endpoints_to_test = [
            "/v1/models",
            "/docs",
            "/openapi.json"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                test_results["tests"].append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response_time,
                    "error": None if response.status_code == 200 else response.text
                })
            except Exception as e:
                test_results["tests"].append({
                    "endpoint": endpoint,
                    "status_code": None,
                    "success": False,
                    "response_time": None,
                    "error": str(e)
                })
        
        return test_results
    
    def test_breathvoice_endpoints(self) -> Dict:
        """测试 BreathVOICE 专用端点"""
        test_results = {
            "test_name": "BreathVOICE 端点测试",
            "tests": []
        }
        
        breathvoice_endpoints = [
            "/breathvoice/voice-groups",
        ]
        
        for endpoint in breathvoice_endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                response_data = None
                
                if success:
                    try:
                        response_data = response.json()
                    except:
                        success = False
                        response_data = "无法解析JSON响应"
                
                test_results["tests"].append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "success": success,
                    "response_time": response_time,
                    "response_data": response_data,
                    "error": None if success else response.text
                })
            except Exception as e:
                test_results["tests"].append({
                    "endpoint": endpoint,
                    "status_code": None,
                    "success": False,
                    "response_time": None,
                    "response_data": None,
                    "error": str(e)
                })
        
        return test_results
    
    def test_voice_group_operations(self) -> Dict:
        """测试角色组操作"""
        test_results = {
            "test_name": "角色组操作测试",
            "tests": []
        }
        
        # 1. 获取角色组列表
        try:
            response = self.session.get(f"{self.base_url}/breathvoice/voice-groups")
            
            if response.status_code == 200:
                voice_groups_data = response.json()
                voice_groups = voice_groups_data.get("voice_groups", [])
                
                test_results["tests"].append({
                    "test": "获取角色组列表",
                    "success": True,
                    "voice_groups_count": len(voice_groups),
                    "voice_groups": voice_groups,
                    "response_time": response.elapsed.total_seconds()
                })
                
                # 2. 测试每个角色组的详细信息
                for voice_group_id in voice_groups:
                    try:
                        detail_response = self.session.get(
                            f"{self.base_url}/breathvoice/voice-groups/{voice_group_id}"
                        )
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            test_results["tests"].append({
                                "test": f"获取角色组详情 - {voice_group_id}",
                                "success": True,
                                "voice_group_id": voice_group_id,
                                "detail_data": detail_data,
                                "response_time": detail_response.elapsed.total_seconds()
                            })
                        else:
                            test_results["tests"].append({
                                "test": f"获取角色组详情 - {voice_group_id}",
                                "success": False,
                                "error": f"HTTP {detail_response.status_code}: {detail_response.text}"
                            })
                    except Exception as e:
                        test_results["tests"].append({
                            "test": f"获取角色组详情 - {voice_group_id}",
                            "success": False,
                            "error": str(e)
                        })
            else:
                test_results["tests"].append({
                    "test": "获取角色组列表",
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
        
        except Exception as e:
            test_results["tests"].append({
                "test": "获取角色组列表",
                "success": False,
                "error": str(e)
            })
        
        return test_results
    
    def test_batch_tts_functionality(self) -> Dict:
        """测试批量 TTS 功能"""
        test_results = {
            "test_name": "批量 TTS 功能测试",
            "tests": []
        }
        
        # 首先获取可用的角色组
        try:
            response = self.session.get(f"{self.base_url}/breathvoice/voice-groups")
            if response.status_code != 200:
                test_results["tests"].append({
                    "test": "批量 TTS - 前置条件检查",
                    "success": False,
                    "error": "无法获取角色组列表"
                })
                return test_results
            
            voice_groups = response.json().get("voice_groups", [])
            if not voice_groups:
                test_results["tests"].append({
                    "test": "批量 TTS - 前置条件检查",
                    "success": False,
                    "error": "没有可用的角色组"
                })
                return test_results
            
            # 使用第一个角色组进行测试
            test_voice_group = voice_groups[0]
            
            # 测试用例
            test_cases = [
                {
                    "name": "单个请求测试",
                    "requests": [
                        {
                            "text": "你好，这是一个测试。",
                            "filename": "greeting_test.wav"
                        }
                    ]
                },
                {
                    "name": "多个请求测试",
                    "requests": [
                        {
                            "text": "欢迎使用 BreathVOICE API！",
                            "filename": "greeting_welcome.wav"
                        },
                        {
                            "text": "这是 B1 情绪的测试文本。",
                            "filename": "emotion_B1_test.wav"
                        },
                        {
                            "text": "这是 B3 情绪的测试文本。",
                            "filename": "emotion_B3_test.wav"
                        }
                    ]
                },
                {
                    "name": "智能参考音频选择测试",
                    "requests": [
                        {
                            "text": "问候语测试",
                            "filename": "greeting_auto_select.wav"
                        },
                        {
                            "text": "B1情绪测试",
                            "filename": "B1_auto_select.wav"
                        },
                        {
                            "text": "B5情绪测试",
                            "filename": "B5_orgasm_auto_select.wav"
                        }
                    ]
                }
            ]
            
            for test_case in test_cases:
                try:
                    payload = {
                        "requests": [
                            {
                                "text": request["text"],
                                "filename": request["filename"],
                                "voice_group_id": test_voice_group
                            } for request in test_case["requests"]
                        ]
                    }
                    
                    start_time = time.time()
                    response = self.session.post(
                        f"{self.base_url}/breathvoice/batch-tts",
                        json=payload,
                        timeout=60
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        test_results["tests"].append({
                            "test": f"批量 TTS - {test_case['name']}",
                            "success": True,
                            "voice_group_id": test_voice_group,
                            "request_count": len(test_case["requests"]),
                            "successful_count": result_data.get("successful_count", 0),
                            "failed_count": result_data.get("failed_count", 0),
                            "response_time": response_time,
                            "results": result_data.get("results", [])
                        })
                    else:
                        test_results["tests"].append({
                            "test": f"批量 TTS - {test_case['name']}",
                            "success": False,
                            "error": f"HTTP {response.status_code}: {response.text}",
                            "response_time": response_time
                        })
                
                except Exception as e:
                    test_results["tests"].append({
                        "test": f"批量 TTS - {test_case['name']}",
                        "success": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            test_results["tests"].append({
                "test": "批量 TTS - 整体测试",
                "success": False,
                "error": str(e)
            })
        
        return test_results
    
    def test_error_handling(self) -> Dict:
        """测试错误处理"""
        test_results = {
            "test_name": "错误处理测试",
            "tests": []
        }
        
        error_test_cases = [
            {
                "name": "不存在的角色组",
                "endpoint": "/breathvoice/voice-groups/NonExistentGroup",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "无效的批量TTS请求 - 缺少voice_group_id",
                "endpoint": "/breathvoice/batch-tts",
                "method": "POST",
                "payload": {
                    "requests": [{"text": "test", "filename": "test.wav"}]
                },
                "expected_status": 400
            },
            {
                "name": "无效的批量TTS请求 - 空请求列表",
                "endpoint": "/breathvoice/batch-tts",
                "method": "POST",
                "payload": {
                    "requests": []
                },
                "expected_status": 400
            },
            {
                "name": "无效的批量TTS请求 - 缺少text字段",
                "endpoint": "/breathvoice/batch-tts",
                "method": "POST",
                "payload": {
                    "requests": [{"filename": "test.wav", "voice_group_id": "TestGroup"}]
                },
                "expected_status": 400
            }
        ]
        
        for test_case in error_test_cases:
            try:
                if test_case["method"] == "GET":
                    response = self.session.get(f"{self.base_url}{test_case['endpoint']}")
                elif test_case["method"] == "POST":
                    response = self.session.post(
                        f"{self.base_url}{test_case['endpoint']}",
                        json=test_case.get("payload", {})
                    )
                
                expected_status = test_case["expected_status"]
                actual_status = response.status_code
                
                test_results["tests"].append({
                    "test": f"错误处理 - {test_case['name']}",
                    "success": actual_status == expected_status,
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                    "response_text": response.text[:200] if response.text else None
                })
            
            except Exception as e:
                test_results["tests"].append({
                    "test": f"错误处理 - {test_case['name']}",
                    "success": False,
                    "error": str(e)
                })
        
        return test_results
    
    def run_full_test_suite(self) -> Dict:
        """运行完整测试套件"""
        print("🚀 开始 BreathVOICE API 完整测试...")
        
        all_results = {
            "test_suite": "BreathVOICE API 完整测试",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "test_results": []
        }
        
        # 运行各项测试
        test_methods = [
            self.test_basic_connectivity,
            self.test_breathvoice_endpoints,
            self.test_voice_group_operations,
            self.test_batch_tts_functionality,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            print(f"📋 运行 {test_method.__name__}...")
            try:
                result = test_method()
                all_results["test_results"].append(result)
                
                # 统计成功/失败
                success_count = sum(1 for test in result["tests"] if test.get("success", False))
                total_count = len(result["tests"])
                print(f"   ✅ {success_count}/{total_count} 测试通过")
                
            except Exception as e:
                print(f"   ❌ 测试执行失败: {e}")
                all_results["test_results"].append({
                    "test_name": test_method.__name__,
                    "error": str(e),
                    "tests": []
                })
        
        all_results["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 生成总结
        total_tests = sum(len(result["tests"]) for result in all_results["test_results"])
        successful_tests = sum(
            sum(1 for test in result["tests"] if test.get("success", False))
            for result in all_results["test_results"]
        )
        
        all_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return all_results

def main():
    """主测试函数"""
    tester = BreathVOICEAPITester()
    results = tester.run_full_test_suite()
    
    # 打印总结
    summary = results["summary"]
    print("\n" + "="*50)
    print("📊 测试总结")
    print("="*50)
    print(f"总测试数: {summary['total_tests']}")
    print(f"成功: {summary['successful_tests']}")
    print(f"失败: {summary['failed_tests']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    
    # 保存详细结果
    with open("breathvoice_api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细测试结果已保存到: breathvoice_api_test_results.json")
    
    return results

if __name__ == "__main__":
    main()
```

### 2. 性能基准测试

```python
import time
import statistics
import concurrent.futures
from typing import List, Dict

class PerformanceTester:
    """性能测试类"""
    
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def measure_response_time(self, endpoint: str, method: str = "GET", payload: Dict = None, iterations: int = 10) -> Dict:
        """测量响应时间"""
        response_times = []
        success_count = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    success_count += 1
                
                # 避免过于频繁的请求
                time.sleep(0.1)
                
            except Exception as e:
                print(f"请求 {i+1} 失败: {e}")
        
        if response_times:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": success_count,
                "success_rate": success_count / iterations * 100,
                "min_time": min(response_times),
                "max_time": max(response_times),
                "avg_time": statistics.mean(response_times),
                "median_time": statistics.median(response_times),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "error": "所有请求都失败了"
            }
    
    def test_concurrent_requests(self, endpoint: str, concurrent_users: int = 5, requests_per_user: int = 3) -> Dict:
        """测试并发请求"""
        def make_request():
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                return {
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有任务
            futures = []
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    futures.append(executor.submit(make_request))
            
            # 收集结果
            for future in concurrent.futures.as_completed(futures):
                all_results.append(future.result())
        
        # 分析结果
        successful_requests = [r for r in all_results if r.get("success", False)]
        failed_requests = [r for r in all_results if not r.get("success", False)]
        
        response_times = [r["response_time"] for r in successful_requests]
        
        return {
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(all_results) * 100,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0
        }
    
    def run_performance_tests(self) -> Dict:
        """运行性能测试套件"""
        print("🚀 开始性能测试...")
        
        results = {
            "test_suite": "BreathVOICE API 性能测试",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": []
        }
        
        # 响应时间测试
        endpoints_to_test = [
            {"endpoint": "/", "method": "GET"},
            {"endpoint": "/breathvoice/voice-groups", "method": "GET"},
            {"endpoint": "/v1/models", "method": "GET"}
        ]
        
        for test_config in endpoints_to_test:
            print(f"📊 测试 {test_config['endpoint']} 响应时间...")
            result = self.measure_response_time(
                test_config["endpoint"],
                test_config["method"],
                iterations=20
            )
            results["tests"].append({
                "test_type": "response_time",
                "result": result
            })
        
        # 并发测试
        print("📊 测试并发请求...")
        concurrent_result = self.test_concurrent_requests(
            "/breathvoice/voice-groups",
            concurrent_users=3,
            requests_per_user=5
        )
        results["tests"].append({
            "test_type": "concurrent_requests",
            "result": concurrent_result
        })
        
        results["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return results

def run_performance_tests():
    """运行性能测试"""
    tester = PerformanceTester()
    results = tester.run_performance_tests()
    
    # 打印结果
    print("\n" + "="*50)
    print("📊 性能测试结果")
    print("="*50)
    
    for test in results["tests"]:
        if test["test_type"] == "response_time":
            result = test["result"]
            if "error" not in result:
                print(f"\n🔍 {result['endpoint']} ({result['method']}):")
                print(f"  成功率: {result['success_rate']:.1f}%")
                print(f"  平均响应时间: {result['avg_time']:.3f}s")
                print(f"  最小响应时间: {result['min_time']:.3f}s")
                print(f"  最大响应时间: {result['max_time']:.3f}s")
                print(f"  标准差: {result['std_dev']:.3f}s")
        
        elif test["test_type"] == "concurrent_requests":
            result = test["result"]
            print(f"\n🔄 并发测试 ({result['concurrent_users']} 用户, 每用户 {result['requests_per_user']} 请求):")
            print(f"  总请求数: {result['total_requests']}")
            print(f"  成功请求数: {result['successful_requests']}")
            print(f"  成功率: {result['success_rate']:.1f}%")
            print(f"  平均响应时间: {result['avg_response_time']:.3f}s")
    
    # 保存结果
    with open("breathvoice_performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 性能测试结果已保存到: breathvoice_performance_test_results.json")
```

## 手动测试清单

### 1. 基础功能测试

#### ✅ API 连通性测试
- [ ] 访问根端点 `/` 返回 200 状态码
- [ ] 访问 `/docs` 显示 Swagger UI
- [ ] 访问 `/openapi.json` 返回有效的 OpenAPI 规范
- [ ] 访问 `/v1/models` 返回模型列表

#### ✅ BreathVOICE 端点测试
- [ ] `GET /breathvoice/voice-groups` 返回角色组列表
- [ ] `GET /breathvoice/voice-groups/{id}` 返回角色组详情
- [ ] `POST /breathvoice/batch-tts` 接受有效请求
- [ ] `POST /breathvoice/upload-voice-group` 接受文件上传

### 2. 功能完整性测试

#### ✅ 角色组管理
- [ ] 能够获取所有可用角色组
- [ ] 每个角色组都有完整的参考文件信息
- [ ] 角色组详情包含所有必需字段
- [ ] 不存在的角色组返回 404 错误

#### ✅ 批量 TTS 生成
- [ ] 单个文本请求正常处理
- [ ] 多个文本请求批量处理
- [ ] 智能参考音频选择正常工作
- [ ] 生成结果包含详细信息
- [ ] 错误请求得到适当处理

#### ✅ 文件上传功能
- [ ] ZIP 文件正确上传和解压
- [ ] 文件验证机制正常工作
- [ ] 覆盖保护机制有效
- [ ] 上传结果提供详细反馈

### 3. 错误处理测试

#### ✅ 输入验证
- [ ] 缺少必需参数时返回 400 错误
- [ ] 无效参数格式时返回 400 错误
- [ ] 空文本请求被正确拒绝
- [ ] 无效文件名被正确处理

#### ✅ 资源不存在
- [ ] 不存在的角色组返回 404
- [ ] 不存在的端点返回 404
- [ ] 错误响应包含有用的错误信息

### 4. 性能测试

#### ✅ 响应时间
- [ ] 基础端点响应时间 < 1 秒
- [ ] 角色组列表响应时间 < 2 秒
- [ ] 单个 TTS 请求响应时间 < 10 秒
- [ ] 批量 TTS 请求合理的响应时间

#### ✅ 并发处理
- [ ] 支持多个并发请求
- [ ] 并发请求不互相影响
- [ ] 系统在负载下保持稳定

## 测试数据

### 示例测试文本

```json
{
  "test_texts": [
    {
      "category": "greeting",
      "texts": [
        "你好，欢迎使用 BreathVOICE！",
        "Hello, welcome to BreathVOICE!",
        "こんにちは、BreathVOICE へようこそ！"
      ]
    },
    {
      "category": "emotion_B1",
      "texts": [
        "这是一个温和的情绪测试。",
        "轻柔的声音让人感到舒适。",
        "平静的语调传达着安宁。"
      ]
    },
    {
      "category": "emotion_B3",
      "texts": [
        "这是一个激动的情绪测试！",
        "充满活力的声音！",
        "热情洋溢的表达！"
      ]
    },
    {
      "category": "emotion_B5",
      "texts": [
        "这是最高潮的情绪表达。",
        "极致的情感体验。",
        "巅峰的声音表现。"
      ]
    }
  ]
}
```

### 测试用例模板

```python
TEST_CASES = [
    {
        "name": "基础功能测试",
        "voice_group_id": "ChineseWoman",
        "requests": [
            {
                "text": "你好，这是一个基础测试。",
                "filename": "basic_test.wav"
            }
        ],
        "expected_success": True
    },
    {
        "name": "智能选择测试 - Greeting",
        "voice_group_id": "ChineseWoman",
        "requests": [
            {
                "text": "欢迎使用我们的服务！",
                "filename": "greeting_welcome.wav"
            }
        ],
        "expected_reference": "ChineseWoman_greeting.wav"
    },
    {
        "name": "智能选择测试 - B1情绪",
        "voice_group_id": "ChineseWoman",
        "requests": [
            {
                "text": "这是一个温和的测试。",
                "filename": "emotion_B1_gentle.wav"
            }
        ],
        "expected_reference": "ChineseWoman_B1_B2.wav"
    },
    {
        "name": "批量处理测试",
        "voice_group_id": "ChineseWoman",
        "requests": [
            {
                "text": "第一个测试文本。",
                "filename": "batch_test_1.wav"
            },
            {
                "text": "第二个测试文本。",
                "filename": "batch_test_2.wav"
            },
            {
                "text": "第三个测试文本。",
                "filename": "batch_test_3.wav"
            }
        ],
        "expected_success_count": 3
    },
    {
        "name": "错误处理测试 - 空文本",
        "voice_group_id": "ChineseWoman",
        "requests": [
            {
                "text": "",
                "filename": "empty_text_test.wav"
            }
        ],
        "expected_success": False
    }
]
```

## 自动化测试执行

### 使用 pytest 运行测试

```python
# test_breathvoice_api.py
import pytest
from breathvoice_api_tester import BreathVOICEAPITester

class TestBreathVOICEAPI:
    
    @pytest.fixture
    def api_tester(self):
        return BreathVOICEAPITester()
    
    def test_basic_connectivity(self, api_tester):
        """测试基础连通性"""
        results = api_tester.test_basic_connectivity()
        
        # 检查所有基础端点都能正常访问
        for test in results["tests"]:
            assert test["success"], f"端点 {test['endpoint']} 测试失败: {test.get('error', '未知错误')}"
    
    def test_breathvoice_endpoints(self, api_tester):
        """测试 BreathVOICE 端点"""
        results = api_tester.test_breathvoice_endpoints()
        
        # 至少要有一个成功的测试
        success_count = sum(1 for test in results["tests"] if test.get("success", False))
        assert success_count > 0, "没有任何 BreathVOICE 端点测试成功"
    
    def test_voice_group_operations(self, api_tester):
        """测试角色组操作"""
        results = api_tester.test_voice_group_operations()
        
        # 检查是否能获取角色组列表
        list_test = next((test for test in results["tests"] if test.get("test") == "获取角色组列表"), None)
        assert list_test is not None, "未找到角色组列表测试"
        assert list_test["success"], f"角色组列表测试失败: {list_test.get('error', '未知错误')}"
    
    def test_batch_tts_functionality(self, api_tester):
        """测试批量 TTS 功能"""
        results = api_tester.test_batch_tts_functionality()
        
        # 检查是否有成功的 TTS 测试
        success_count = sum(1 for test in results["tests"] if test.get("success", False))
        assert success_count > 0, "没有任何批量 TTS 测试成功"

# 运行测试
# pytest test_breathvoice_api.py -v --html=report.html
```

### 持续集成配置

```yaml
# .github/workflows/api_test.yml
name: BreathVOICE API Tests

on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时运行一次
  workflow_dispatch:  # 手动触发

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install requests pytest pytest-html
    
    - name: Run API tests
      run: |
        python breathvoice_api_tester.py
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-results
        path: |
          breathvoice_api_test_results.json
          breathvoice_performance_test_results.json
```

## 测试报告生成

### HTML 报告生成器

```python
def generate_html_report(test_results: Dict, output_file: str = "test_report.html"):
    """生成 HTML 测试报告"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BreathVOICE API 测试报告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
            .summary { background-color: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }
            .test-section { margin: 20px 0; }
            .test-item { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
            .success { border-left-color: #4CAF50; background-color: #f8fff8; }
            .failure { border-left-color: #f44336; background-color: #fff8f8; }
            .details { font-size: 0.9em; color: #666; margin-top: 5px; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>BreathVOICE API 测试报告</h1>
            <p><strong>测试时间:</strong> {start_time} - {end_time}</p>
            <p><strong>API 地址:</strong> {base_url}</p>
        </div>
        
        <div class="summary">
            <h2>测试总结</h2>
            <p><strong>总测试数:</strong> {total_tests}</p>
            <p><strong>成功:</strong> {successful_tests}</p>
            <p><strong>失败:</strong> {failed_tests}</p>
            <p><strong>成功率:</strong> {success_rate:.1f}%</p>
        </div>
        
        {test_sections}
    </body>
    </html>
    """
    
    # 生成测试部分的 HTML
    test_sections = ""
    for test_result in test_results["test_results"]:
        test_sections += f"""
        <div class="test-section">
            <h3>{test_result['test_name']}</h3>
        """
        
        for test in test_result["tests"]:
            success = test.get("success", False)
            css_class = "success" if success else "failure"
            status = "✅ 成功" if success else "❌ 失败"
            
            test_sections += f"""
            <div class="test-item {css_class}">
                <strong>{test.get('test', test.get('endpoint', '未知测试'))}</strong> - {status}
            """
            
            if not success and test.get("error"):
                test_sections += f'<div class="details">错误: {test["error"]}</div>'
            
            if test.get("response_time"):
                test_sections += f'<div class="details">响应时间: {test["response_time"]:.3f}s</div>'
            
            test_sections += "</div>"
        
        test_sections += "</div>"
    
    # 填充模板
    html_content = html_template.format(
        start_time=test_results.get("start_time", "未知"),
        end_time=test_results.get("end_time", "未知"),
        base_url=test_results.get("base_url", "未知"),
        total_tests=test_results["summary"]["total_tests"],
        successful_tests=test_results["summary"]["successful_tests"],
        failed_tests=test_results["summary"]["failed_tests"],
        success_rate=test_results["summary"]["success_rate"],
        test_sections=test_sections
    )
    
    # 保存文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"📄 HTML 测试报告已生成: {output_file}")
```

## 监控和告警

### 健康检查脚本

```python
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class APIHealthMonitor:
    """API 健康监控"""
    
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120"):
        self.base_url = base_url.rstrip('/')
    
    def check_api_health(self) -> Dict:
        """检查 API 健康状态"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": []
        }
        
        # 检查基础端点
        basic_endpoints = ["/", "/v1/models", "/breathvoice/voice-groups"]
        
        for endpoint in basic_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                check_result = {
                    "endpoint": endpoint,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code != 200:
                    health_status["overall_status"] = "unhealthy"
                    check_result["error"] = response.text[:100]
                
            except Exception as e:
                check_result = {
                    "endpoint": endpoint,
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["overall_status"] = "unhealthy"
            
            health_status["checks"].append(check_result)
        
        return health_status
    
    def send_alert(self, health_status: Dict):
        """发送告警（示例实现）"""
        if health_status["overall_status"] == "unhealthy":
            print(f"🚨 API 健康检查失败: {health_status['timestamp']}")
            
            for check in health_status["checks"]:
                if check["status"] == "unhealthy":
                    print(f"   ❌ {check['endpoint']}: {check.get('error', '未知错误')}")

# 使用示例
def run_health_check():
    monitor = APIHealthMonitor()
    health_status = monitor.check_api_health()
    
    print(f"🏥 API 健康检查 - {health_status['timestamp']}")
    print(f"总体状态: {'✅ 健康' if health_status['overall_status'] == 'healthy' else '❌ 不健康'}")
    
    for check in health_status["checks"]:
        status_icon = "✅" if check["status"] == "healthy" else "❌"
        print(f"  {status_icon} {check['endpoint']}: {check['status']}")
        
        if check.get("response_time"):
            print(f"     响应时间: {check['response_time']:.3f}s")
    
    # 如果不健康，发送告警
    monitor.send_alert(health_status)
    
    return health_status
```

## 总结

本可用性测试指南提供了完整的 BreathVOICE API 测试方案：

1. **自动化测试脚本** - 全面的功能和性能测试
2. **手动测试清单** - 系统化的验证步骤
3. **性能基准测试** - 响应时间和并发能力评估
4. **错误处理验证** - 异常情况的处理能力
5. **持续监控** - 健康检查和告警机制
6. **测试报告生成** - 详细的测试结果文档

通过这些测试工具和流程，可以确保 BreathVOICE API 的质量、稳定性和性能满足生产环境的要求。

---

**使用建议**:
1. 在部署后立即运行完整测试套件
2. 设置定期的健康检查和性能监控
3. 在每次更新后重新运行测试
4. 根据测试结果持续优化 API 性能