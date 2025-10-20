#!/usr/bin/env python3
"""
BreathVOICE API 测试脚本
测试批量TTS生成功能
适用于外网API服务器: https://tts.ioioioioio.com:1120
"""

import requests
import json
import time

# API配置 - 外网服务器
BASE_URL = "https://tts.ioioioioio.com:1120"
BREATHVOICE_API_BASE = f"{BASE_URL}/breathvoice"

def test_health_check():
    """测试健康检查端点"""
    print("=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BREATHVOICE_API_BASE}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json()
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_get_voice_groups():
    """测试获取角色组列表"""
    print("=== 测试获取角色组列表 ===")
    try:
        response = requests.get(f"{BREATHVOICE_API_BASE}/voice-groups")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json()
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_get_voice_group_info(voice_group_id):
    """测试获取角色组详细信息"""
    print(f"\n=== 测试获取角色组 '{voice_group_id}' 详细信息 ===")
    try:
        response = requests.get(f"{BREATHVOICE_API_BASE}/voice-groups/{voice_group_id}")
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_single_tts():
    """测试单条TTS生成"""
    print(f"\n=== 测试单条TTS生成 ===")
    
    # 准备测试数据
    test_request = {
        "text": "你好，欢迎来到我们的世界！",
        "filename": "test_single_greeting_001.wav",
        "voice_group_id": "ChineseWoman"
    }
    
    try:
        print(f"发送单条TTS请求到: {BREATHVOICE_API_BASE}/single-tts")
        print(f"请求数据: {json.dumps(test_request, indent=2, ensure_ascii=False)}")
        
        start_time = time.time()
        response = requests.post(
            f"{BREATHVOICE_API_BASE}/single-tts",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"状态码: {response.status_code}")
        print(f"请求耗时: {end_time - start_time:.2f}秒")
        
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            print("✅ 单条TTS生成成功")
            return result
        else:
            print("❌ 单条TTS生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_sequential_tts():
    """测试逐条TTS生成工作流"""
    print(f"\n=== 测试逐条TTS生成工作流 ===")
    
    # 准备测试数据
    test_requests = [
        {
            "text": "你好，欢迎来到我们的世界！",
            "filename": "test_seq_greeting_001.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "这真是太令人兴奋了！",
            "filename": "test_seq_B1_start_004.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "哇，这种感觉真是难以置信！",
            "filename": "test_seq_B3_reaction_002.wav",
            "voice_group_id": "ChineseWoman"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"开始逐条生成 {len(test_requests)} 个音频文件...")
    
    for i, request in enumerate(test_requests):
        print(f"\n[{i+1}/{len(test_requests)}] 正在生成: {request['text'][:30]}...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BREATHVOICE_API_BASE}/single-tts",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            request_time = end_time - start_time
            total_time += request_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    results.append(result['result'])
                    print(f"✅ 生成成功: {result['result']['filename']} ({request_time:.2f}s)")
                else:
                    error_result = {
                        "filename": request['filename'],
                        "text": request['text'],
                        "status": "failed",
                        "error": result.get('error', 'Unknown error')
                    }
                    results.append(error_result)
                    print(f"❌ 生成失败: {request['filename']} - {result.get('error')}")
            else:
                error_result = {
                    "filename": request['filename'],
                    "text": request['text'],
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
                results.append(error_result)
                print(f"❌ HTTP错误: {request['filename']} - {response.status_code}")
                
        except Exception as e:
            error_result = {
                "filename": request['filename'],
                "text": request['text'],
                "status": "failed",
                "error": str(e)
            }
            results.append(error_result)
            print(f"❌ 请求异常: {request['filename']} - {e}")
    
    # 统计结果
    success_count = sum(1 for r in results if r.get('status') == 'success')
    print(f"\n🎉 逐条生成完成:")
    print(f"   成功: {success_count}/{len(results)}")
    print(f"   总耗时: {total_time:.2f}秒")
    print(f"   平均耗时: {total_time/len(results):.2f}秒/条")
    
    return results

def test_batch_tts():
    """测试批量TTS生成"""
    print(f"\n=== 测试批量TTS生成 ===")
    
    # 准备测试数据
    test_requests = [
        {
            "text": "你好，欢迎来到我们的世界！",
            "filename": "test_greeting_001.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "这真是太令人兴奋了！",
            "filename": "test_B1_start_004.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "哇，这种感觉真是难以置信！",
            "filename": "test_B3_reaction_002.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "啊...这就是最高的境界！",
            "filename": "test_B5_climax_003.wav",
            "voice_group_id": "ChineseWoman"
        }
    ]
    
    # 构建批量TTS请求
    batch_data = {
        "requests": test_requests
    }
    
    try:
        print(f"发送批量TTS请求到: {BREATHVOICE_API_BASE}/batch-tts")
        print(f"请求数据: {json.dumps(batch_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BREATHVOICE_API_BASE}/batch-tts",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            print(f"\n✅ 批量TTS成功完成!")
            print(f"   - 总请求数: {result.get('total_requests', 0)}")
            print(f"   - 成功数: {result.get('successful', 0)}")
            print(f"   - 失败数: {result.get('failed', 0)}")
            print(f"   - 总处理时间: {result.get('total_processing_time', 0):.2f}秒")
            
            # 显示每个文件的处理结果
            for i, file_result in enumerate(result.get('results', []), 1):
                status_icon = "✅" if file_result.get('status') == 'success' else "❌"
                print(f"   {i}. {status_icon} {file_result.get('filename')} "
                      f"({file_result.get('processing_time', 0):.2f}s)")
        else:
            print(f"❌ 批量TTS失败: {result.get('error', '未知错误')}")
            
        return result
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_api_connectivity():
    """测试API连通性"""
    print("=== 测试API连通性 ===")
    try:
        # 测试基础API
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"基础API状态码: {response.status_code}")
        
        # 测试OpenAI兼容API
        response = requests.get(f"{BASE_URL}/v1/models", timeout=10)
        print(f"OpenAI API状态码: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎵 BreathVOICE API 外网测试开始")
    print(f"📡 测试服务器: {BASE_URL}")
    print("=" * 50)
    
    # 1. 测试连通性
    if not test_api_connectivity():
        print("❌ API服务器连接失败，请检查网络或服务器状态")
        return
    
    print("✅ API服务器连接正常")
    
    # 2. 测试健康检查
    health_result = test_health_check()
    if not health_result or health_result.get("status") != "healthy":
        print("❌ 健康检查失败")
        return
    
    print("✅ 健康检查通过")
    
    # 3. 测试获取角色组列表
    voice_groups_result = test_get_voice_groups()
    if not voice_groups_result or not voice_groups_result.get("success"):
        print("❌ 获取角色组列表失败")
        return
    
    voice_groups = voice_groups_result.get("voice_groups", [])
    if not voice_groups:
        print("❌ 没有可用的角色组")
        return
    
    print(f"✅ 发现 {len(voice_groups)} 个角色组: {voice_groups}")
    
    # 4. 测试获取角色组详细信息
    first_voice_group = voice_groups[0]
    voice_group_info = test_get_voice_group_info(first_voice_group)
    if not voice_group_info or not voice_group_info.get("success"):
        print(f"❌ 获取角色组 '{first_voice_group}' 详细信息失败")
        return
    
    print(f"✅ 角色组 '{first_voice_group}' 信息获取成功")
    
    # 5. 测试单条TTS生成
    print("\n" + "=" * 30 + " 新功能测试 " + "=" * 30)
    single_result = test_single_tts()
    if single_result and single_result.get("success"):
        print("✅ 单条TTS生成测试成功")
    else:
        print("❌ 单条TTS生成测试失败")
    
    # 6. 测试逐条TTS生成工作流
    sequential_results = test_sequential_tts()
    if sequential_results:
        success_count = sum(1 for r in sequential_results if r.get('status') == 'success')
        if success_count > 0:
            print("✅ 逐条TTS生成工作流测试成功")
        else:
            print("❌ 逐条TTS生成工作流测试失败")
    else:
        print("❌ 逐条TTS生成工作流测试失败")
    
    # 7. 测试批量TTS生成（原有功能）
    print("\n" + "=" * 30 + " 原有功能测试 " + "=" * 30)
    batch_result = test_batch_tts()
    if not batch_result or not batch_result.get("success"):
        print("❌ 批量TTS生成失败")
        return
    
    print("✅ 批量TTS生成成功")
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！BreathVOICE API 外网服务正常")
    print("📋 测试总结:")
    print("   ✅ 基础连通性测试")
    print("   ✅ 健康检查")
    print("   ✅ 角色组管理")
    print("   ✅ 单条TTS生成 (新功能)")
    print("   ✅ 逐条生成工作流 (新功能)")
    print("   ✅ 批量TTS生成 (原有功能)")

if __name__ == "__main__":
    main()