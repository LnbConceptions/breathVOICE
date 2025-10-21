#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的提示词配置
验证orgasm、P4、P5、P6体位相关的提示词修改效果
"""

import os
import sys

def test_enhanced_prompts():
    """测试增强后的提示词配置"""
    
    print("🧪 测试增强后的提示词配置")
    print("=" * 80)
    
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
    
    # 测试1：检查orgasm台词的角色视角修正
    print("\n📋 测试1：检查orgasm台词的角色视角修正")
    
    orgasm_checks = [
        ("IMPORTANT: Focus ONLY on the female character's perspective", "强调角色视角"),
        ("never describe male ejaculation or 'filling' actions", "禁止描述男性行为"),
        ("Avoid phrases like '射进来', '子宫被你填满了'", "避免特定短语"),
        ("character's physical sensations, emotional responses", "关注角色感受"),
        ("from the character's viewpoint", "角色视角")
    ]
    
    for check_text, description in orgasm_checks:
        if check_text in content:
            print(f"✅ {description}：已添加")
        else:
            print(f"❌ {description}：缺失")
            all_tests_passed = False
    
    # 测试2：检查P5体位的强化主导性描述
    print("\n📋 测试2：检查P5体位的强化主导性描述")
    
    p5_enhanced_guidance = "STRONG active control, dominance, and taking charge of the rhythm and intensity. Show confidence and assertiveness."
    
    if p5_enhanced_guidance in content:
        print("✅ P5体位强化主导性描述已添加")
        
        # 检查在reaction和tease中都存在
        reaction_count = content.count(p5_enhanced_guidance)
        if reaction_count >= 2:
            print(f"✅ P5体位强化描述在多个位置存在 ({reaction_count}次)")
        else:
            print(f"⚠️  P5体位强化描述只在{reaction_count}个位置存在")
    else:
        print("❌ P5体位强化主导性描述缺失")
        all_tests_passed = False
    
    # 测试3：检查P4和P6体位的被动享受描述
    print("\n📋 测试3：检查P4和P6体位的被动享受描述")
    
    p4_p6_guidance = "For P4 (doggy style) and P6 (pin-down position): Show the character being passive but deeply enjoying the experience, expressing pleasure through submission and surrender."
    
    if p4_p6_guidance in content:
        print("✅ P4和P6体位被动享受描述已添加")
        
        # 检查在reaction和tease中都存在
        p4_p6_count = content.count(p4_p6_guidance)
        if p4_p6_count >= 2:
            print(f"✅ P4/P6体位描述在多个位置存在 ({p4_p6_count}次)")
        else:
            print(f"⚠️  P4/P6体位描述只在{p4_p6_count}个位置存在")
    else:
        print("❌ P4和P6体位被动享受描述缺失")
        all_tests_passed = False
    
    # 测试4：检查体位定义的一致性
    print("\n📋 测试4：检查体位定义的一致性")
    
    position_definitions = [
        ('"P4": "背后位 - 从后面进入"', "P4定义"),
        ('"P5": "骑乘位 - 女性在上"', "P5定义"),
        ('"P6": "压迫位"', "P6定义")
    ]
    
    for definition, description in position_definitions:
        if definition in content:
            print(f"✅ {description}：正确")
        else:
            print(f"❌ {description}：不正确或缺失")
            all_tests_passed = False
    
    # 测试5：检查关键词的存在
    print("\n📋 测试5：检查关键词的存在")
    
    key_terms = [
        ("STRONG active control", "强化主动控制"),
        ("dominance", "主导性"),
        ("taking charge", "掌控"),
        ("confidence and assertiveness", "自信和果断"),
        ("passive but deeply enjoying", "被动但享受"),
        ("submission and surrender", "顺从和投降"),
        ("female character's perspective", "女性角色视角"),
        ("never describe male ejaculation", "禁止描述男性射精")
    ]
    
    for term, description in key_terms:
        if term in content:
            print(f"✅ {description}：找到关键词 '{term}'")
        else:
            print(f"❌ {description}：缺少关键词 '{term}'")
            all_tests_passed = False
    
    # 测试6：验证提示词结构完整性
    print("\n📋 测试6：验证提示词结构完整性")
    
    event_types = ["reaction", "tease", "orgasm"]
    for event_type in event_types:
        event_section = f'"{event_type}": ['
        if event_section in content:
            print(f"✅ {event_type}类台词结构完整")
        else:
            print(f"❌ {event_type}类台词结构缺失")
            all_tests_passed = False
    
    # 测试7：检查是否有冲突的指导
    print("\n📋 测试7：检查是否有冲突的指导")
    
    # 检查是否同时存在旧的和新的P5描述
    old_p5_guidance = "Emphasize the character's active control and dominance in the sexual encounter."
    new_p5_guidance = "STRONG active control, dominance, and taking charge"
    
    if old_p5_guidance in content and new_p5_guidance in content:
        print("⚠️  同时存在旧的和新的P5描述，可能需要清理")
    elif new_p5_guidance in content:
        print("✅ 只存在新的增强P5描述")
    else:
        print("❌ 新的P5描述不存在")
        all_tests_passed = False
    
    # 总结
    print("\n" + "=" * 80)
    if all_tests_passed:
        print("🎉 所有测试通过！增强后的提示词配置已成功应用")
        print("\n📝 修改总结：")
        print("   🔸 orgasm台词：明确角色视角，避免用户视角描述")
        print("   🔸 P5体位：强化主导性、自信和掌控感")
        print("   🔸 P4/P6体位：强调被动但享受的状态")
        print("   🔸 关键词优化：更具体和明确的指导")
    else:
        print("❌ 部分测试失败，请检查修改内容")
    
    return all_tests_passed

def main():
    """主函数"""
    try:
        success = test_enhanced_prompts()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()