#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试语音包导出功能修正
"""

import os
import sys
import tempfile
import shutil
from voice_pack_exporter import VoicePackExporter

def test_export_voice_pack():
    """测试语音包导出功能"""
    print("开始测试语音包导出功能...")
    
    # 测试参数
    character_name = "Elf Princess"
    source_voices_dir = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}"
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_output_dir:
        print(f"使用临时输出目录: {temp_output_dir}")
        
        # 创建导出器实例
        exporter = VoicePackExporter()
        
        # 定义进度回调函数
        def progress_callback(progress, message):
            print(f"进度: {progress:.1%} - {message}")
        
        try:
            # 执行导出
            print(f"开始导出角色: {character_name}")
            print(f"源目录: {source_voices_dir}")
            
            result = exporter.export_voice_pack(
                character_name=character_name,
                source_voices_dir=source_voices_dir,
                output_dir=temp_output_dir,
                progress_callback=progress_callback
            )
            
            print(f"\n导出结果: {result}")
            
            # 检查输出文件
            expected_zip_path = os.path.join(temp_output_dir, f"{character_name}.zip")
            if os.path.exists(expected_zip_path):
                file_size = os.path.getsize(expected_zip_path)
                print(f"✓ ZIP文件已创建: {expected_zip_path}")
                print(f"✓ 文件大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
                
                # 检查ZIP文件内容
                import zipfile
                with zipfile.ZipFile(expected_zip_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(f"✓ ZIP文件包含 {len(file_list)} 个文件")
                    
                    # 显示前10个文件
                    print("ZIP文件内容（前10个文件）:")
                    for i, file_name in enumerate(file_list[:10]):
                        print(f"  {i+1}. {file_name}")
                    
                    if len(file_list) > 10:
                        print(f"  ... 还有 {len(file_list) - 10} 个文件")
                    
                    # 检查BRE文件
                    bre_files = [f for f in file_list if f.endswith('.bre')]
                    print(f"✓ BRE文件数量: {len(bre_files)}")
                    
                    # 检查文件夹结构
                    folders = set()
                    for file_name in file_list:
                        if '/' in file_name:
                            folder = file_name.split('/')[1] if file_name.count('/') > 0 else file_name.split('/')[0]
                            folders.add(folder)
                    print(f"✓ 包含的文件夹: {sorted(folders)}")
                
                return True
            else:
                print(f"✗ ZIP文件未创建: {expected_zip_path}")
                return False
                
        except Exception as e:
            print(f"✗ 导出过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("语音包导出功能测试")
    print("=" * 60)
    
    # 检查源目录是否存在
    character_name = "Elf Princess"
    source_dir = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}"
    
    if not os.path.exists(source_dir):
        print(f"✗ 源目录不存在: {source_dir}")
        return False
    
    print(f"✓ 源目录存在: {source_dir}")
    
    # 统计源文件数量
    total_files = 0
    for root, dirs, files in os.walk(source_dir):
        # 排除temp文件夹
        if 'temp' in root:
            continue
        wav_files = [f for f in files if f.endswith('.wav')]
        total_files += len(wav_files)
    
    print(f"✓ 源目录包含 {total_files} 个WAV文件")
    
    # 执行测试
    success = test_export_voice_pack()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 测试通过！语音包导出功能正常工作")
    else:
        print("✗ 测试失败！语音包导出功能存在问题")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)