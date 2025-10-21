#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版orgasm提示词修正测试
直接检查文件内容，避免模块导入问题
"""

import os
import re

def test_action_parameters_file():
    """测试action_parameters.py中的orgasm描述"""
    print("1. 检查 action_parameters.py:")
    
    try:
        with open("action_parameters.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找orgasm描述
        orgasm_pattern = r'"orgasm":\s*"([^"]+)"'
        match = re.search(orgasm_pattern, content)
        
        if match:
            description = match.group(1)
            print(f"   描述: {description}")
            
            # 检查关键词
            key_terms = ["female character herself", "own pleasure", "sensations"]
            found_terms = [term for term in key_terms if term in description]
            
            print(f"   包含关键词: {found_terms}")
            
            if len(found_terms) >= 2:
                print("   ✓ 描述已正确更新")
                return True
            else:
                print("   ✗ 描述可能未完全更新")
                return False
        else:
            print("   ✗ 未找到orgasm描述")
            return False
            
    except Exception as e:
        print(f"   ✗ 读取文件失败: {e}")
        return False

def test_csv_parameter_loader_file():
    """测试csv_parameter_loader.py中的orgasm描述"""
    print("\n2. 检查 csv_parameter_loader.py:")
    
    try:
        with open("csv_parameter_loader.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找orgasm描述
        orgasm_pattern = r'"orgasm":\s*"([^"]+)"'
        match = re.search(orgasm_pattern, content)
        
        if match:
            description = match.group(1)
            print(f"   描述: {description}")
            
            # 检查关键词
            key_terms = ["female character herself", "own pleasure", "sensations"]
            found_terms = [term for term in key_terms if term in description]
            
            print(f"   包含关键词: {found_terms}")
            
            if len(found_terms) >= 2:
                print("   ✓ 描述已正确更新")
                return True
            else:
                print("   ✗ 描述可能未完全更新")
                return False
        else:
            print("   ✗ 未找到orgasm描述")
            return False
            
    except Exception as e:
        print(f"   ✗ 读取文件失败: {e}")
        return False

def test_dialogue_generator_file():
    """测试dialogue_generator.py中的orgasm相关内容"""
    print("\n3. 检查 dialogue_generator.py:")
    
    try:
        with open("dialogue_generator.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查示例描述
        example_updated = False
        if "female character's own climax sensations" in content:
            print("   ✓ 示例描述已更新")
            example_updated = True
        else:
            print("   ✗ 示例描述可能未更新")
        
        # 检查事件指导
        guidance_updated = False
        if "Express the character's own pleasure" in content:
            print("   ✓ 事件指导已更新")
            guidance_updated = True
        else:
            print("   ✗ 事件指导可能未更新")
        
        # 检查是否移除了用户射精相关描述
        user_ejaculation_removed = True
        if "user's ejaculation" in content.lower() or "user ejaculation" in content.lower():
            print("   ⚠️  仍包含用户射精相关描述")
            user_ejaculation_removed = False
        else:
            print("   ✓ 已移除用户射精相关描述")
        
        return example_updated and guidance_updated and user_ejaculation_removed
        
    except Exception as e:
        print(f"   ✗ 读取文件失败: {e}")
        return False

def test_consistency_across_files():
    """测试各文件间描述的一致性"""
    print("\n4. 检查文件间一致性:")
    
    files = ["action_parameters.py", "csv_parameter_loader.py"]
    descriptions = []
    
    for file_name in files:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read()
            
            orgasm_pattern = r'"orgasm":\s*"([^"]+)"'
            match = re.search(orgasm_pattern, content)
            
            if match:
                descriptions.append((file_name, match.group(1)))
        except Exception as e:
            print(f"   ✗ 无法读取 {file_name}: {e}")
    
    if len(descriptions) >= 2:
        desc1 = descriptions[0][1]
        desc2 = descriptions[1][1]
        
        if desc1 == desc2:
            print("   ✓ 两个文件中的描述完全一致")
            return True
        else:
            print("   ⚠️  两个文件中的描述略有差异")
            print(f"     {descriptions[0][0]}: {desc1}")
            print(f"     {descriptions[1][0]}: {desc2}")
            
            # 检查是否包含相同的关键概念
            key_concepts = ["female character herself", "own pleasure"]
            both_have_concepts = all(
                any(concept in desc1 for concept in key_concepts) and
                any(concept in desc2 for concept in key_concepts)
            )
            
            if both_have_concepts:
                print("   ✓ 两个文件都包含关键概念")
                return True
            else:
                print("   ✗ 文件间缺少一致的关键概念")
                return False
    else:
        print("   ✗ 无法获取足够的描述进行比较")
        return False

def main():
    """主测试函数"""
    print("=== 测试orgasm提示词修正效果 ===\n")
    
    # 运行各项测试
    test1 = test_action_parameters_file()
    test2 = test_csv_parameter_loader_file()
    test3 = test_dialogue_generator_file()
    test4 = test_consistency_across_files()
    
    # 总结结果
    print(f"\n=== 测试结果总结 ===")
    print(f"action_parameters.py: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"csv_parameter_loader.py: {'✓ 通过' if test2 else '✗ 失败'}")
    print(f"dialogue_generator.py: {'✓ 通过' if test3 else '✗ 失败'}")
    print(f"文件间一致性: {'✓ 通过' if test4 else '✗ 失败'}")
    
    all_passed = all([test1, test2, test3, test4])
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        print("✅ orgasm提示词已成功修正为女性角色自身高潮时的台词")
        print("💡 建议：重新生成orgasm相关台词以应用新的提示词逻辑")
    else:
        print("\n❌ 部分测试失败")
        print("请检查相关文件的修改是否完整")
    
    return all_passed

if __name__ == "__main__":
    main()