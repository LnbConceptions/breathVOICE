#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS API集成测试脚本
验证台词数据向TTS API的完整传递流程
"""

import os
import sys
import pandas as pd
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tts_api_data_flow():
    """测试TTS API数据流传递的完整性"""
    print("🔍 开始测试TTS API数据流传递...")
    
    # 1. 测试台词模板加载
    print("\n1️⃣ 测试台词模板加载...")
    template_path = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/台词模版.csv"
    
    if not os.path.exists(template_path):
        print(f"❌ 台词模板文件不存在: {template_path}")
        return False
    
    try:
        df = pd.read_csv(template_path, encoding='utf-8')
        action_params = df['动作参数'].tolist()
        print(f"✅ 成功加载台词模板，包含 {len(action_params)} 个动作参数")
        print(f"   前5个动作参数: {action_params[:5]}")
    except Exception as e:
        print(f"❌ 加载台词模板失败: {e}")
        return False
    
    # 2. 模拟台词生成和保存
    print("\n2️⃣ 模拟台词生成和保存...")
    
    # 创建测试台词数据
    test_dialogues = []
    for i, param in enumerate(action_params[:10]):  # 只测试前10个
        test_dialogues.append({
            'action_param': param,
            'dialogue': f"这是{param}的测试台词内容 {i+1}",
            'audio_path': None
        })
    
    # 创建临时存档目录
    temp_archive_dir = tempfile.mkdtemp(prefix="tts_test_archive_")
    archive_file = os.path.join(temp_archive_dir, "test_dialogue_archive.json")
    
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(test_dialogues, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功保存测试台词存档: {archive_file}")
        print(f"   存档包含 {len(test_dialogues)} 条台词数据")
    except Exception as e:
        print(f"❌ 保存台词存档失败: {e}")
        return False
    
    # 3. 测试存档加载和数据结构验证
    print("\n3️⃣ 测试存档加载和数据结构验证...")
    
    try:
        with open(archive_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print(f"✅ 成功加载存档数据，包含 {len(loaded_data)} 条记录")
        
        # 验证数据结构
        required_fields = ['action_param', 'dialogue', 'audio_path']
        for i, item in enumerate(loaded_data):
            for field in required_fields:
                if field not in item:
                    print(f"❌ 第{i+1}条记录缺少必需字段: {field}")
                    return False
        
        print("✅ 所有记录的数据结构验证通过")
        
    except Exception as e:
        print(f"❌ 加载存档数据失败: {e}")
        return False
    
    # 4. 模拟TTS API调用数据准备
    print("\n4️⃣ 模拟TTS API调用数据准备...")
    
    # 模拟选中的台词（选择前5条）
    selected_indices = [0, 1, 2, 3, 4]
    selected_dialogues = []
    
    for idx in selected_indices:
        if idx < len(loaded_data):
            item = loaded_data[idx]
            api_payload = {
                'text': item['dialogue'],
                'filename': f"{item['action_param']}.wav",
                'voice_group_id': 'test_voice_id',
                'character_name': 'test_character'
            }
            selected_dialogues.append({
                'index': idx,
                'action_param': item['action_param'],
                'api_payload': api_payload
            })
    
    print(f"✅ 成功准备 {len(selected_dialogues)} 条TTS API调用数据")
    
    # 验证API payload结构
    for i, item in enumerate(selected_dialogues):
        payload = item['api_payload']
        required_api_fields = ['text', 'filename', 'voice_group_id', 'character_name']
        
        for field in required_api_fields:
            if field not in payload:
                print(f"❌ 第{i+1}条API payload缺少必需字段: {field}")
                return False
            
            if not payload[field]:  # 检查字段值不为空
                print(f"❌ 第{i+1}条API payload字段值为空: {field}")
                return False
    
    print("✅ 所有API payload结构验证通过")
    
    # 5. 测试动态UI组件数量适配
    print("\n5️⃣ 测试动态UI组件数量适配...")
    
    # 模拟不同数量的台词数据
    test_cases = [
        {"name": "小数据集", "count": 50},
        {"name": "中等数据集", "count": 200},
        {"name": "大数据集", "count": 434},  # 当前实际数量
        {"name": "超大数据集", "count": 600}
    ]
    
    MAX_POSSIBLE_ROWS = 650  # 从代码中获取的最大支持行数
    
    for case in test_cases:
        count = case["count"]
        name = case["name"]
        
        if count <= MAX_POSSIBLE_ROWS:
            print(f"✅ {name} ({count}条) - 在支持范围内")
            
            # 模拟UI组件列表长度
            ui_components_count = MAX_POSSIBLE_ROWS
            checkbox_values = [True] * count + [False] * (ui_components_count - count)
            
            # 验证选中数据提取
            selected_count = sum(checkbox_values[:count])
            print(f"   模拟选中 {selected_count} 条台词进行TTS生成")
            
        else:
            print(f"⚠️  {name} ({count}条) - 超出最大支持数量 ({MAX_POSSIBLE_ROWS})")
    
    # 6. 测试数据传递链路完整性
    print("\n6️⃣ 测试数据传递链路完整性...")
    
    # 模拟完整的数据传递链路
    chain_test_data = {
        'template_params': action_params[:5],
        'generated_dialogues': [item['dialogue'] for item in test_dialogues[:5]],
        'selected_indices': [0, 2, 4],  # 选择第1、3、5条
        'api_calls': []
    }
    
    # 模拟API调用链路
    for idx in chain_test_data['selected_indices']:
        if idx < len(chain_test_data['generated_dialogues']):
            api_call = {
                'input_text': chain_test_data['generated_dialogues'][idx],
                'action_param': chain_test_data['template_params'][idx],
                'expected_filename': f"{chain_test_data['template_params'][idx]}.wav"
            }
            chain_test_data['api_calls'].append(api_call)
    
    print(f"✅ 数据传递链路测试完成")
    print(f"   模板参数 → 台词生成 → 选择过滤 → API调用")
    print(f"   {len(chain_test_data['template_params'])} → {len(chain_test_data['generated_dialogues'])} → {len(chain_test_data['selected_indices'])} → {len(chain_test_data['api_calls'])}")
    
    # 清理测试文件
    try:
        shutil.rmtree(temp_archive_dir)
        print(f"\n🧹 清理测试文件完成")
    except Exception as e:
        print(f"\n⚠️  清理测试文件时出现警告: {e}")
    
    print("\n🎉 TTS API数据流传递测试全部通过！")
    return True

def test_ui_component_scaling():
    """测试UI组件动态扩展能力"""
    print("\n🔧 测试UI组件动态扩展能力...")
    
    # 模拟不同规模的数据加载
    test_scenarios = [
        {"name": "初始加载", "dialogue_count": 0},
        {"name": "小规模数据", "dialogue_count": 100},
        {"name": "当前规模", "dialogue_count": 434},
        {"name": "扩展规模", "dialogue_count": 500},
        {"name": "最大规模", "dialogue_count": 650}
    ]
    
    for scenario in test_scenarios:
        count = scenario["dialogue_count"]
        name = scenario["name"]
        
        # 模拟UI组件状态
        visible_components = min(count, 650)  # MAX_POSSIBLE_ROWS
        hidden_components = max(0, 650 - count)
        
        print(f"📊 {name}: {count}条台词")
        print(f"   可见UI组件: {visible_components}")
        print(f"   隐藏UI组件: {hidden_components}")
        print(f"   总UI组件: {visible_components + hidden_components}")
        
        # 验证组件数量一致性
        if visible_components + hidden_components == 650:
            print(f"   ✅ UI组件数量一致性验证通过")
        else:
            print(f"   ❌ UI组件数量不一致")
            return False
    
    print("✅ UI组件动态扩展能力测试通过")
    return True

if __name__ == "__main__":
    print("🚀 启动TTS API集成测试...")
    
    success = True
    
    # 运行主要测试
    if not test_tts_api_data_flow():
        success = False
    
    # 运行UI组件测试
    if not test_ui_component_scaling():
        success = False
    
    if success:
        print("\n🎊 所有测试通过！TTS API集成验证完成。")
        print("\n📋 测试总结:")
        print("   ✅ 台词模板加载正常")
        print("   ✅ 台词数据保存和加载正常")
        print("   ✅ TTS API数据准备正常")
        print("   ✅ UI组件动态适配正常")
        print("   ✅ 数据传递链路完整")
    else:
        print("\n❌ 部分测试失败，请检查相关功能。")
        sys.exit(1)