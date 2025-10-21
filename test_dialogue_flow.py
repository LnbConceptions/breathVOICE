#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试台词保存和加载的完整流程
验证数据一致性和UI组件动态调整
"""

import pandas as pd
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from action_parameters import ALL_ACTION_PARAMS

def test_template_loading():
    """测试台词模板文件加载"""
    print("=== 测试台词模板文件加载 ===")
    
    template_path = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/台词模版.csv"
    
    if not os.path.exists(template_path):
        print(f"❌ 台词模板文件不存在: {template_path}")
        return False
    
    try:
        df = pd.read_csv(template_path, encoding='utf-8')
        print(f"✅ 成功加载台词模板文件")
        print(f"   - 文件路径: {template_path}")
        print(f"   - 数据行数: {len(df)}")
        print(f"   - 列名: {list(df.columns)}")
        
        # 检查是否包含动作参数列
        if '动作参数' in df.columns:
            action_params = df['动作参数'].dropna().tolist()
            print(f"   - 动作参数数量: {len(action_params)}")
            print(f"   - 前5个动作参数: {action_params[:5]}")
            return True, action_params
        else:
            print("❌ 台词模板文件中缺少'动作参数'列")
            return False, []
            
    except Exception as e:
        print(f"❌ 加载台词模板文件失败: {e}")
        return False, []

def test_action_parameters_consistency():
    """测试动作参数一致性"""
    print("\n=== 测试动作参数一致性 ===")
    
    # 从代码中获取的参数
    code_params = ALL_ACTION_PARAMS
    print(f"代码中定义的参数数量: {len(code_params)}")
    
    # 从模板文件中获取的参数
    success, template_params = test_template_loading()
    if not success:
        return False
    
    print(f"模板文件中的参数数量: {len(template_params)}")
    
    # 比较参数
    code_set = set(code_params)
    template_set = set(template_params)
    
    # 检查差异
    only_in_code = code_set - template_set
    only_in_template = template_set - code_set
    common = code_set & template_set
    
    print(f"共同参数数量: {len(common)}")
    
    if only_in_code:
        print(f"⚠️  仅在代码中存在的参数 ({len(only_in_code)}个):")
        for param in list(only_in_code)[:5]:  # 只显示前5个
            print(f"   - {param}")
        if len(only_in_code) > 5:
            print(f"   ... 还有 {len(only_in_code) - 5} 个")
    
    if only_in_template:
        print(f"⚠️  仅在模板文件中存在的参数 ({len(only_in_template)}个):")
        for param in list(only_in_template)[:5]:  # 只显示前5个
            print(f"   - {param}")
        if len(only_in_template) > 5:
            print(f"   ... 还有 {len(only_in_template) - 5} 个")
    
    if len(only_in_code) == 0 and len(only_in_template) == 0:
        print("✅ 代码和模板文件中的参数完全一致")
        return True
    else:
        print("⚠️  代码和模板文件中的参数存在差异")
        return False

def test_dialogue_generation_simulation():
    """模拟台词生成过程"""
    print("\n=== 模拟台词生成过程 ===")
    
    # 模拟生成的台词数据
    success, template_params = test_template_loading()
    if not success:
        return False
    
    # 创建模拟的台词DataFrame
    dialogue_data = []
    for i, param in enumerate(template_params[:10]):  # 只测试前10个参数
        dialogue_data.append({
            '动作参数': param,
            '台词': f"这是针对{param}的测试台词 {i+1}",
            '选中': True
        })
    
    df = pd.DataFrame(dialogue_data)
    print(f"✅ 模拟生成了 {len(df)} 条台词")
    
    # 测试保存
    test_save_path = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/存档/test_dialogue_set.csv"
    
    # 确保存档目录存在
    os.makedirs(os.path.dirname(test_save_path), exist_ok=True)
    
    try:
        df.to_csv(test_save_path, index=False, encoding='utf-8')
        print(f"✅ 成功保存测试台词集: {test_save_path}")
        
        # 验证保存的文件
        loaded_df = pd.read_csv(test_save_path, encoding='utf-8')
        print(f"✅ 成功加载保存的台词集，包含 {len(loaded_df)} 条台词")
        
        # 验证数据完整性
        if len(loaded_df) == len(df):
            print("✅ 保存和加载的数据数量一致")
        else:
            print(f"❌ 数据数量不一致: 保存{len(df)}条，加载{len(loaded_df)}条")
            
        return True, test_save_path
        
    except Exception as e:
        print(f"❌ 保存台词集失败: {e}")
        return False, None

def test_ui_component_capacity():
    """测试UI组件容量"""
    print("\n=== 测试UI组件容量 ===")
    
    # 获取当前参数数量
    success, template_params = test_template_loading()
    if not success:
        return False
    
    current_param_count = len(template_params)
    max_possible_rows = 650  # 从代码中获取的MAX_POSSIBLE_ROWS值
    
    print(f"当前参数数量: {current_param_count}")
    print(f"UI组件最大容量: {max_possible_rows}")
    
    if current_param_count <= max_possible_rows:
        print(f"✅ UI组件容量充足，剩余容量: {max_possible_rows - current_param_count}")
        return True
    else:
        print(f"❌ UI组件容量不足，超出: {current_param_count - max_possible_rows}")
        return False

def test_archive_directory():
    """测试存档目录"""
    print("\n=== 测试存档目录 ===")
    
    archive_dir = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/存档"
    
    if not os.path.exists(archive_dir):
        print(f"⚠️  存档目录不存在，正在创建: {archive_dir}")
        try:
            os.makedirs(archive_dir, exist_ok=True)
            print("✅ 成功创建存档目录")
        except Exception as e:
            print(f"❌ 创建存档目录失败: {e}")
            return False
    else:
        print(f"✅ 存档目录存在: {archive_dir}")
    
    # 列出现有的存档文件
    try:
        archive_files = [f for f in os.listdir(archive_dir) if f.endswith('.csv')]
        print(f"现有存档文件数量: {len(archive_files)}")
        
        if archive_files:
            print("存档文件列表:")
            for i, file in enumerate(archive_files[:5]):  # 只显示前5个
                file_path = os.path.join(archive_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   {i+1}. {file} ({file_size} bytes)")
            
            if len(archive_files) > 5:
                print(f"   ... 还有 {len(archive_files) - 5} 个文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取存档目录失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("\n=== 清理测试文件 ===")
    
    test_file = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/存档/test_dialogue_set.csv"
    
    if os.path.exists(test_file):
        try:
            os.remove(test_file)
            print(f"✅ 已删除测试文件: {test_file}")
        except Exception as e:
            print(f"⚠️  删除测试文件失败: {e}")
    else:
        print("ℹ️  没有需要清理的测试文件")

def main():
    """主测试函数"""
    print("开始台词保存和加载流程测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_template_loading,
        test_action_parameters_consistency,
        test_dialogue_generation_simulation,
        test_ui_component_capacity,
        test_archive_directory
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            if isinstance(result, tuple):
                results.append(result[0])
            else:
                results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 执行失败: {e}")
            results.append(False)
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！台词保存和加载流程正常")
    else:
        print("⚠️  部分测试未通过，请检查相关问题")
    
    # 清理测试文件
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    main()