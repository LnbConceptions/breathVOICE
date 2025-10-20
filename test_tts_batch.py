#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import time

# API配置
API_BASE_URL = "https://tts.ioioioioio.com:1120"
VOICE_GROUP_ID = "ChineseWoman"

# 选择的5条台词数据
selected_dialogues = [
    {"action": "P1_B1_B2_RButt_short_1", "text": "Mmph! That was a nice little spank..."},
    {"action": "P0_B1_B2_reaction_3", "text": "I'm starting to enjoy this..."},
    {"action": "greeting_7", "text": "You're looking at me in that way again!"},
    {"action": "P0_B4_B5_reaction_17", "text": "OH MY GOD! DON'T STOP!"},
    {"action": "P0_B4_reaction_4", "text": "I'm so close! Don't you dare stop!"}
]

def test_breathvoice_batch_tts():
    """测试BreathVOICE批量TTS生成功能"""
    try:
        # 准备批量TTS请求数据
        batch_requests = {
            "requests": [
                {
                    "text": dialogue["text"],
                    "filename": dialogue["action"] + ".wav",
                    "voice_group_id": VOICE_GROUP_ID
                }
                for dialogue in selected_dialogues
            ]
        }
        
        print(f"准备发送批量TTS请求...")
        print(f"使用角色组: {VOICE_GROUP_ID}")
        print(f"请求数量: {len(batch_requests['requests'])}")
        
        # 发送批量TTS请求
        response = requests.post(
            f"{API_BASE_URL}/breathvoice/batch-tts",
            json=batch_requests,
            verify=False,
            timeout=60
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success", False):
                # 检查生成的结果
                results = result.get("results", [])
                print(f"\n✅ 批量TTS生成成功!")
                print(f"\n生成了 {len(results)} 个音频文件:")
                
                # 记录生成的文件信息
                generated_files = []
                for i, res in enumerate(results, 1):
                    filename = res.get("filename", "未知")
                    success = res.get("success", False)
                    message = res.get("message", "")
                    output_path = res.get("output_path", "")
                    reference_audio = res.get("reference_audio_used", "")
                    
                    print(f"{i}. 文件名: {filename}")
                    print(f"   状态: {'成功' if success else '失败'}")
                    if message:
                        print(f"   消息: {message}")
                    if output_path:
                        print(f"   服务器路径: {output_path}")
                    if reference_audio:
                        print(f"   参考音频: {reference_audio}")
                    
                    if success:
                        generated_files.append({
                            'filename': filename,
                            'output_path': output_path,
                            'reference_audio': reference_audio
                        })
                    print()
                
                return generated_files
            else:
                print(f"❌ 批量TTS生成失败: {result.get('message', '未知错误')}")
                return []
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误信息: {error_info}")
            except:
                print(f"响应内容: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 批量TTS处理异常: {e}")
        return []

def verify_generated_files(generated_files, expected_filenames):
    """验证生成的文件名是否与动作参数一致"""
    print("\n" + "="*60)
    print("验证生成的音频文件...")
    print(f"期望的文件列表:")
    for i, filename in enumerate(expected_filenames, 1):
        print(f"{i}. {filename}")
    
    print(f"\n实际生成的文件:")
    for i, file_info in enumerate(generated_files, 1):
        print(f"{i}. {file_info['filename']}")
        print(f"   服务器路径: {file_info['output_path']}")
        print(f"   参考音频: {file_info['reference_audio']}")
    
    print(f"\n文件名验证结果:")
    all_match = True
    for expected_filename in expected_filenames:
        found = any(file_info['filename'] == expected_filename for file_info in generated_files)
        status = "✅" if found else "❌"
        print(f"{status} {expected_filename} - {'存在' if found else '不存在'}")
        if not found:
            all_match = False
    
    print(f"\n验证结果: {'✅ 所有文件名都符合要求' if all_match else '❌ 部分文件名不符合要求'}")
    return all_match

if __name__ == "__main__":
    print("开始测试 BreathVOICE 批量TTS生成...")
    
    # 创建输出目录
    output_dir = "voice_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成音频文件
    generated_files = test_breathvoice_batch_tts()
    
    if generated_files:
        print("\n等待文件生成完成...")
        time.sleep(3)  # 等待文件生成完成
        
        # 验证生成的文件名
        expected_filenames = [dialogue["action"] + ".wav" for dialogue in selected_dialogues]
        verify_generated_files(generated_files, expected_filenames)
    else:
        print("❌ 批量TTS生成失败，无法进行文件验证")
    
    print("\n测试完成!")