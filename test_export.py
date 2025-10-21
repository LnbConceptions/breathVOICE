#!/usr/bin/env python3
"""
测试语音包导出功能的脚本
"""

import os
import sys
from voice_pack_exporter import VoicePackExporter

def test_export():
    """测试导出功能"""
    print("🚀 开始测试语音包导出功能...")
    
    # 创建导出器实例
    exporter = VoicePackExporter()
    
    # 设置参数
    character_name = "Elf Princess"
    source_voices_dir = f"Characters/{character_name}"
    output_dir = "output"
    
    # 检查源目录是否存在
    if not os.path.exists(source_voices_dir):
        print(f"❌ 源目录不存在: {source_voices_dir}")
        return False
    
    print(f"📁 角色名称: {character_name}")
    print(f"📁 源目录: {source_voices_dir}")
    print(f"📁 输出目录: {output_dir}")
    
    # 进度回调函数
    def progress_callback(current, total, message=""):
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"📊 进度: {current}/{total} ({percentage:.1f}%) - {message}")
    
    try:
        # 执行导出
        result = exporter.export_voice_pack(
            character_name=character_name,
            source_voices_dir=source_voices_dir,
            output_dir=output_dir,
            progress_callback=progress_callback
        )
        
        if result["success"]:
            print(f"✅ 导出成功!")
            print(f"📦 ZIP文件: {result['zip_path']}")
            print(f"📊 统计信息:")
            print(f"   - 总文件数: {result['stats']['total_files']}")
            print(f"   - 成功转换: {result['stats']['converted_files']}")
            print(f"   - 跳过文件: {result['stats']['skipped_files']}")
            print(f"   - 失败文件: {result['stats']['failed_files']}")
            
            # 检查ZIP文件
            if os.path.exists(result['zip_path']):
                file_size = os.path.getsize(result['zip_path'])
                print(f"📏 ZIP文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                
                # 验证ZIP内容
                import zipfile
                try:
                    with zipfile.ZipFile(result['zip_path'], 'r') as zip_file:
                        file_list = zip_file.namelist()
                        print(f"📋 ZIP内容: {len(file_list)} 个文件")
                        if len(file_list) > 0:
                            print("   前5个文件:")
                            for i, filename in enumerate(file_list[:5]):
                                print(f"     {i+1}. {filename}")
                        if len(file_list) > 5:
                            print(f"     ... 还有 {len(file_list) - 5} 个文件")
                except Exception as e:
                    print(f"❌ ZIP文件验证失败: {e}")
            
            return True
        else:
            print(f"❌ 导出失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 导出过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export()
    sys.exit(0 if success else 1)