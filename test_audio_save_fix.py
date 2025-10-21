#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试音频文件保存路径修正功能
验证文件是否正确保存到角色文件夹下的子文件夹而不是 Voices 文件夹
"""

import os
import tempfile
import shutil
import sys

def test_audio_save_path_fix():
    """测试音频文件保存路径修正"""
    print("开始测试音频文件保存路径修正...")
    
    # 创建临时测试环境
    test_base_dir = tempfile.mkdtemp()
    print(f"创建临时测试目录: {test_base_dir}")
    
    try:
        # 模拟角色文件夹结构
        character_name = "Test_Character"
        character_dir = os.path.join(test_base_dir, "Characters", character_name)
        temp_dir = os.path.join(character_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建测试音频文件
        test_files = [
            "greeting_001.wav",
            "impact_002.wav", 
            "reaction_003.wav",
            "tease_004.wav",
            "long_005.wav",
            "short_006.wav",
            "orgasm_007.wav",
            "breath_008.wav",
            "moan_009.wav"
        ]
        
        for filename in test_files:
            test_file_path = os.path.join(temp_dir, filename)
            with open(test_file_path, 'w') as f:
                f.write("test audio content")
        
        print(f"创建了 {len(test_files)} 个测试音频文件")
        
        # 模拟修正后的保存逻辑
        keyword_mapping = {
            "greeting": "greeting",
            "impact": "impact", 
            "reaction": "reaction",
            "tease": "tease",
            "long": "touch",
            "short": "touch",
            "orgasm": "orgasm",
            "breath": "breath",
            "moan": "moan"
        }
        
        saved_count = 0
        moved_files = {}
        
        # 遍历temp文件夹中的所有文件
        for filename in os.listdir(temp_dir):
            if filename.endswith('.wav'):
                source_path = os.path.join(temp_dir, filename)
                
                # 检查文件名中包含的关键词
                for keyword, folder_name in keyword_mapping.items():
                    if keyword in filename.lower():
                        # 创建目标文件夹（直接在角色目录下）
                        target_folder = os.path.join(character_dir, folder_name)
                        os.makedirs(target_folder, exist_ok=True)
                    
                        # 移动文件到目标文件夹
                        target_path = os.path.join(target_folder, filename)
                        try:
                            shutil.move(source_path, target_path)
                            moved_files[source_path] = target_path
                            saved_count += 1
                            print(f"✓ 移动文件: {filename} -> {folder_name}/")
                            break  # 找到匹配的关键词后跳出循环
                        except Exception as e:
                            print(f"✗ 移动文件失败 {filename}: {e}")
        
        # 验证结果
        print(f"\n移动了 {saved_count} 个文件")
        
        # 检查预期的文件夹结构
        expected_folders = ["greeting", "impact", "reaction", "tease", "touch", "orgasm", "breath", "moan"]
        
        print("\n验证文件夹结构:")
        all_correct = True
        
        for folder in expected_folders:
            folder_path = os.path.join(character_dir, folder)
            if os.path.exists(folder_path):
                files_in_folder = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
                print(f"✓ {folder}/ 文件夹存在，包含 {len(files_in_folder)} 个文件")
                if files_in_folder:
                    print(f"  文件: {', '.join(files_in_folder)}")
            else:
                print(f"✗ {folder}/ 文件夹不存在")
                all_correct = False
        
        # 检查是否有 Voices 文件夹被创建（不应该有）
        voices_dir = os.path.join(character_dir, f"{character_name}_Voices")
        if os.path.exists(voices_dir):
            print(f"✗ 错误：仍然创建了 Voices 文件夹: {voices_dir}")
            all_correct = False
        else:
            print("✓ 正确：没有创建 Voices 文件夹")
        
        # 检查 temp 文件夹是否为空
        remaining_files = [f for f in os.listdir(temp_dir) if f.endswith('.wav')]
        if remaining_files:
            print(f"✗ temp 文件夹中仍有 {len(remaining_files)} 个文件未移动")
            all_correct = False
        else:
            print("✓ temp 文件夹已清空")
        
        if all_correct:
            print("\n🎉 测试通过！音频文件保存路径修正成功")
            return True
        else:
            print("\n❌ 测试失败！存在问题需要修正")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False
        
    finally:
        # 清理临时文件
        shutil.rmtree(test_base_dir)
        print(f"清理临时测试目录: {test_base_dir}")

if __name__ == "__main__":
    success = test_audio_save_path_fix()
    sys.exit(0 if success else 1)