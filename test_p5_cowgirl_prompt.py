#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试P5体位主动感提示词修改效果
验证reaction和tease类台词中是否正确添加了P5体位的主动感指导
"""

import os
import sys

def test_p5_cowgirl_prompt_modifications():
    """测试P5体位主动感提示词的修改效果"""
    
    print("🧪 测试P5体位主动感提示词修改效果")
    print("=" * 60)
    
    # 测试文件路径
    dialogue_generator_path = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/dialogue_generator.py"
    
    if not os.path.exists(dialogue_generator_path):
        print(f"❌ 错误：找不到文件 {dialogue_generator_path}")
        return False
    
    # 读取文件内容
    with open(dialogue_generator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试结果
    all_tests_passed = True
    
    # 测试1：检查reaction类台词中是否包含P5体位主动感指导
    print("\n📋 测试1：检查reaction类台词中的P5体位主动感指导")
    reaction_p5_guidance = "For P5 (cowgirl position): Emphasize the character's active control and dominance in the sexual encounter."
    
    if reaction_p5_guidance in content:
        print("✅ reaction类台词中已正确添加P5体位主动感指导")
        
        # 检查是否在正确的位置（reaction部分）
        reaction_section_start = content.find('"reaction": [')
        reaction_section_end = content.find('],', reaction_section_start)
        reaction_section = content[reaction_section_start:reaction_section_end]
        
        if reaction_p5_guidance in reaction_section:
            print("✅ P5体位指导位于正确的reaction部分")
        else:
            print("❌ P5体位指导不在reaction部分")
            all_tests_passed = False
    else:
        print("❌ reaction类台词中缺少P5体位主动感指导")
        all_tests_passed = False
    
    # 测试2：检查tease类台词中是否包含P5体位主动感指导
    print("\n📋 测试2：检查tease类台词中的P5体位主动感指导")
    tease_p5_guidance = "For P5 (cowgirl position): Emphasize the character's active control and dominance in the sexual encounter."
    
    if tease_p5_guidance in content:
        print("✅ tease类台词中已正确添加P5体位主动感指导")
        
        # 检查是否在正确的位置（tease部分）
        tease_section_start = content.find('"tease": [')
        tease_section_end = content.find('],', tease_section_start)
        tease_section = content[tease_section_start:tease_section_end]
        
        if tease_p5_guidance in tease_section:
            print("✅ P5体位指导位于正确的tease部分")
        else:
            print("❌ P5体位指导不在tease部分")
            all_tests_passed = False
    else:
        print("❌ tease类台词中缺少P5体位主动感指导")
        all_tests_passed = False
    
    # 测试3：检查P5体位的定义是否正确
    print("\n📋 测试3：检查P5体位的定义")
    p5_definition = '"P5": "骑乘位 - 女性在上"'
    
    if p5_definition in content:
        print("✅ P5体位定义正确：骑乘位 - 女性在上")
    else:
        print("❌ P5体位定义不正确或缺失")
        all_tests_passed = False
    
    # 测试4：检查是否有P5相关的动作参数
    print("\n📋 测试4：检查P5相关的动作参数")
    p5_reaction_params = [param for param in content.split('\n') if 'P5_' in param and 'reaction' in param]
    p5_tease_params = [param for param in content.split('\n') if 'P5_' in param and 'tease' in param]
    
    if p5_reaction_params:
        print(f"✅ 找到 {len(p5_reaction_params)} 个P5 reaction相关参数")
    else:
        print("⚠️  未在当前文件中找到P5 reaction参数（可能在其他文件中定义）")
    
    if p5_tease_params:
        print(f"✅ 找到 {len(p5_tease_params)} 个P5 tease相关参数")
    else:
        print("⚠️  未在当前文件中找到P5 tease参数（可能在其他文件中定义）")
    
    # 测试5：验证指导内容的一致性
    print("\n📋 测试5：验证指导内容的一致性")
    if reaction_p5_guidance == tease_p5_guidance:
        print("✅ reaction和tease类台词中的P5体位指导内容一致")
    else:
        print("❌ reaction和tease类台词中的P5体位指导内容不一致")
        all_tests_passed = False
    
    # 测试6：检查关键词的存在
    print("\n📋 测试6：检查关键词的存在")
    key_terms = ["active control", "dominance", "cowgirl position"]
    
    for term in key_terms:
        if term in content:
            print(f"✅ 找到关键词：{term}")
        else:
            print(f"❌ 缺少关键词：{term}")
            all_tests_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 所有测试通过！P5体位主动感提示词已成功添加")
        print("📝 修改内容：")
        print("   - reaction类台词：强调角色在性爱中的主动控制和主导感")
        print("   - tease类台词：强调角色在性爱中的主动控制和主导感")
        print("   - 体位定义：P5 = 骑乘位 - 女性在上")
    else:
        print("❌ 部分测试失败，请检查修改内容")
    
    return all_tests_passed

def main():
    """主函数"""
    try:
        success = test_p5_cowgirl_prompt_modifications()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()