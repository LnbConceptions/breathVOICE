#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import platform
import subprocess
import psutil
import tempfile
import struct
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class BreathKitExporter:
    """breathKIT导出器 - 处理USB设备检测和bre文件导出"""
    
    def __init__(self):
        self.system = platform.system()
    
    def detect_usb_devices(self) -> List[Dict[str, str]]:
        """检测所有USB存储设备"""
        usb_devices = []
        
        try:
            # 获取所有磁盘分区
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                # 跳过系统分区和网络驱动器
                if 'cdrom' in partition.opts or partition.fstype == '':
                    continue
                
                # 在macOS上，USB设备通常挂载在/Volumes下
                if self.system == "Darwin":
                    if not partition.mountpoint.startswith('/Volumes/'):
                        continue
                # 在Windows上，检查驱动器类型
                elif self.system == "Windows":
                    try:
                        import win32file
                        drive_type = win32file.GetDriveType(partition.device)
                        # DRIVE_REMOVABLE = 2
                        if drive_type != 2:
                            continue
                    except ImportError:
                        # 如果没有win32file，跳过类型检查
                        pass
                
                # 检查是否可访问
                try:
                    if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                        device_info = {
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype,
                            'name': os.path.basename(partition.mountpoint) if partition.mountpoint != '/' else partition.device
                        }
                        usb_devices.append(device_info)
                except (PermissionError, OSError):
                    continue
        
        except Exception as e:
            print(f"检测USB设备时出错: {e}")
        
        return usb_devices
    
    def check_lb_folder(self, mountpoint: str) -> bool:
        """检查USB设备根目录是否有LB文件夹"""
        try:
            lb_path = os.path.join(mountpoint, "LB")
            return os.path.exists(lb_path) and os.path.isdir(lb_path)
        except Exception:
            return False
    
    def is_fat32_filesystem(self, device_info: Dict[str, str]) -> bool:
        """检查文件系统是否为FAT32"""
        fstype = device_info.get('fstype', '').lower()
        # FAT32可能显示为fat32, vfat, fat等
        return fstype in ['fat32', 'vfat', 'fat', 'msdos']
    
    def find_breathkit_devices(self) -> List[Dict[str, str]]:
        """查找符合breathKIT要求的USB设备（FAT32格式且有LB文件夹）"""
        usb_devices = self.detect_usb_devices()
        breathkit_devices = []
        
        for device in usb_devices:
            # 检查文件系统格式
            if not self.is_fat32_filesystem(device):
                continue
            
            # 检查LB文件夹
            if not self.check_lb_folder(device['mountpoint']):
                continue
            
            # 添加LB文件夹路径信息
            device['lb_path'] = os.path.join(device['mountpoint'], "LB")
            breathkit_devices.append(device)
        
        return breathkit_devices
    
    def get_bre_files_from_zip(self, zip_path: str) -> List[str]:
        """从导出的ZIP文件中提取bre文件列表"""
        import zipfile
        bre_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('.bre') and not file_info.is_dir():
                        bre_files.append(file_info.filename)
        except Exception as e:
            print(f"读取ZIP文件时出错: {e}")
        
        return bre_files
    
    def extract_bre_files_to_temp(self, zip_path: str, temp_dir: str) -> bool:
        """将ZIP文件中的bre文件解压到临时目录"""
        import zipfile
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('.bre') and not file_info.is_dir():
                        zip_ref.extract(file_info, temp_dir)
            
            return True
        except Exception as e:
            print(f"解压bre文件时出错: {e}")
            return False
    
    def copy_bre_files_to_breathkit(self, zip_path: str, device_info: Dict[str, str], 
                                   progress_callback=None) -> Tuple[bool, str, Dict]:
        """将bre文件从ZIP包复制到breathKIT设备"""
        import tempfile
        import zipfile
        
        try:
            lb_path = device_info['lb_path']
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解压bre文件到临时目录
                if not self.extract_bre_files_to_temp(zip_path, temp_dir):
                    return False, "解压bre文件失败", {}
                
                # 统计文件
                total_files = 0
                copied_files = 0
                errors = []
                
                # 遍历临时目录中的所有bre文件
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.bre'):
                            total_files += 1
                
                if total_files == 0:
                    return False, "ZIP文件中没有找到bre文件", {}
                
                # 复制文件
                current_file = 0
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.bre'):
                            current_file += 1
                            
                            if progress_callback:
                                progress_callback(current_file, total_files, f"复制文件: {file}")
                            
                            try:
                                src_path = os.path.join(root, file)
                                
                                # 保持目录结构
                                rel_path = os.path.relpath(root, temp_dir)
                                if rel_path == '.':
                                    dst_dir = lb_path
                                else:
                                    dst_dir = os.path.join(lb_path, rel_path)
                                
                                os.makedirs(dst_dir, exist_ok=True)
                                dst_path = os.path.join(dst_dir, file)
                                
                                shutil.copy2(src_path, dst_path)
                                copied_files += 1
                                
                            except Exception as e:
                                error_msg = f"复制文件 {file} 失败: {str(e)}"
                                errors.append(error_msg)
                                print(error_msg)
            
            # 返回结果
            stats = {
                'total_files': total_files,
                'copied_files': copied_files,
                'errors': errors
            }
            
            if copied_files > 0:
                success_msg = f"成功复制 {copied_files}/{total_files} 个bre文件到breathKIT设备"
                if errors:
                    success_msg += f"，{len(errors)} 个文件复制失败"
                return True, success_msg, stats
            else:
                return False, "没有文件被成功复制", stats
                
        except Exception as e:
            return False, f"导出到breathKIT时出错: {str(e)}", {}
    
    def export_to_breathkit(self, zip_path: str, progress_callback=None) -> Tuple[bool, str, Dict]:
        """导出bre文件到breathKIT设备"""
        # 查找breathKIT设备
        devices = self.find_breathkit_devices()
        
        if not devices:
            return False, "未找到符合条件的breathKIT设备（需要FAT32格式且包含LB文件夹）", {}
        
        if len(devices) > 1:
            device_names = [d['name'] for d in devices]
            return False, f"找到多个breathKIT设备，请只连接一个设备: {', '.join(device_names)}", {}
        
        # 使用找到的设备
        device = devices[0]
        
        # 检查ZIP文件是否存在
        if not os.path.exists(zip_path):
            return False, f"ZIP文件不存在: {zip_path}", {}
        
        # 执行复制
        return self.copy_bre_files_to_breathkit(zip_path, device, progress_callback)
    
    def get_folder_size(self, folder_path):
        """
        计算文件夹的总大小（字节）
        
        Args:
            folder_path (str): 文件夹路径
            
        Returns:
            int: 文件夹大小（字节）
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"计算文件夹大小失败: {str(e)}")
        return total_size
    
    def get_wav_info(self, wav_path):
        """获取WAV文件信息"""
        try:
            with open(wav_path, 'rb') as f:
                # 读取WAV头部
                riff = f.read(4)
                if riff != b'RIFF':
                    return None
                
                file_size = struct.unpack('<I', f.read(4))[0]
                wave = f.read(4)
                if wave != b'WAVE':
                    return None
                
                fmt_chunk = f.read(4)
                if fmt_chunk != b'fmt ':
                    return None
                
                fmt_size = struct.unpack('<I', f.read(4))[0]
                audio_format = struct.unpack('<H', f.read(2))[0]
                num_channels = struct.unpack('<H', f.read(2))[0]
                sample_rate = struct.unpack('<I', f.read(4))[0]
                byte_rate = struct.unpack('<I', f.read(4))[0]
                block_align = struct.unpack('<H', f.read(2))[0]
                bits_per_sample = struct.unpack('<H', f.read(2))[0]
                
                data_chunk = f.read(4)
                if data_chunk != b'data':
                    return None
                
                data_size = struct.unpack('<I', f.read(4))[0]
                
                return {
                    'file_size': file_size,
                    'audio_format': audio_format,
                    'num_channels': num_channels,
                    'sample_rate': sample_rate,
                    'bits_per_sample': bits_per_sample,
                    'data_size': data_size,
                    'header_size': 44  # 标准WAV头部大小
                }
        except Exception as e:
            print(f"Error reading {wav_path}: {e}")
            return None

    def calculate_bre_size(self, wav_path):
        """计算转换为BRE后的文件大小"""
        info = self.get_wav_info(wav_path)
        if not info:
            return 0
        
        # 根据C代码分析：
        # 1. WAV头部保持不变 (44字节)
        # 2. 音频数据大小保持不变 (只是从int16_t转换为uint16_t)
        # 3. BRE文件大小 = WAV文件大小
        return info['header_size'] + info['data_size']

    def calculate_bre_folder_size(self, folder_path):
        """计算文件夹中所有WAV文件转换为BRE后的总大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.endswith('.wav'):
                        file_path = os.path.join(dirpath, filename)
                        if os.path.exists(file_path):
                            bre_size = self.calculate_bre_size(file_path)
                            total_size += bre_size
        except Exception as e:
            print(f"计算BRE文件夹大小失败: {str(e)}")
        return total_size
    
    def get_disk_free_space(self, path):
        """
        获取指定路径所在磁盘的可用空间（字节）
        
        Args:
            path (str): 文件或文件夹路径
            
        Returns:
            int: 可用空间（字节）
        """
        try:
            if self.system == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), ctypes.pointer(free_bytes), None, None)
                return free_bytes.value
            else:
                statvfs = os.statvfs(path)
                return statvfs.f_frsize * statvfs.f_bavail
        except Exception as e:
            print(f"获取磁盘空间失败: {str(e)}")
            return 0
    
    def check_disk_space(self, source_folder, target_folder, character_name=None, reference_voices=None):
        """
        检查目标磁盘是否有足够空间存储源文件夹
        
        Args:
            source_folder (str): 源文件夹路径
            target_folder (str): 目标文件夹路径
            character_name (str): 角色名称（可选）
            reference_voices (dict): 参考声音配置（可选）
            
        Returns:
            tuple: (bool, str) - (是否有足够空间, 详细信息)
        """
        try:
            # 如果提供了角色和参考声音信息，使用精确计算
            if character_name and reference_voices:
                required_space = self.calculate_required_space_for_export(character_name, reference_voices)
            else:
                # 回退到原有逻辑：计算源文件夹大小
                source_size = self.get_folder_size(source_folder)
                # 添加10%的安全余量
                required_space = int(source_size * 1.1)
            
            # 获取目标磁盘可用空间
            free_space = self.get_disk_free_space(target_folder)
            
            required_gb = required_space / (1024**3)
            free_gb = free_space / (1024**3)
            
            if free_space >= required_space:
                return True, f"磁盘空间充足。需要: {required_gb:.2f} GB，可用: {free_gb:.2f} GB"
            else:
                return False, f"磁盘空间不足。需要: {required_gb:.2f} GB，可用: {free_gb:.2f} GB，建议至少: {required_gb:.2f} GB"
                
        except Exception as e:
            return False, f"检查磁盘空间时出错: {str(e)}"
    
    def calculate_required_space_for_export(self, character_name, reference_voices):
        """
        计算导出特定角色和参考声音所需的磁盘空间
        
        Args:
            character_name (str): 角色名称
            reference_voices (list or dict): 参考声音配置
            
        Returns:
            int: 所需空间（字节）
        """
        total_size = 0
        
        try:
            # 角色文件夹路径
            character_folder = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}"
            if os.path.exists(character_folder):
                total_size += self.calculate_bre_folder_size(character_folder)
            
            # 参考声音文件夹路径
            if isinstance(reference_voices, dict):
                # 如果是字典格式
                for voice_type, voice_name in reference_voices.items():
                    if voice_name:
                        voice_folder = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Reference Voices/{voice_name}"
                        if os.path.exists(voice_folder):
                            total_size += self.calculate_bre_folder_size(voice_folder)
            elif isinstance(reference_voices, list):
                # 如果是列表格式
                for voice_name in reference_voices:
                    if voice_name:
                        voice_folder = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Reference Voices/{voice_name}"
                        if os.path.exists(voice_folder):
                            total_size += self.calculate_bre_folder_size(voice_folder)
            
            # 添加10%的安全余量
            return int(total_size * 1.1)
            
        except Exception as e:
            print(f"计算所需空间失败: {str(e)}")
            # 如果计算失败，返回一个保守的估计值（500MB）
            return 500 * 1024 * 1024
    
    def move_folder_with_progress(self, source_folder, target_folder, progress_callback=None):
        """
        移动文件夹并提供进度反馈
        
        Args:
            source_folder (str): 源文件夹路径
            target_folder (str): 目标文件夹路径
            progress_callback (callable): 进度回调函数，接收(progress, desc)参数
            
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_folder), exist_ok=True)
            
            # 统计总文件数
            total_files = 0
            for root, dirs, files in os.walk(source_folder):
                total_files += len(files)
            
            if total_files == 0:
                return False, "源文件夹为空"
            
            # 创建目标文件夹
            os.makedirs(target_folder, exist_ok=True)
            
            current_file = 0
            
            # 复制所有文件
            for root, dirs, files in os.walk(source_folder):
                # 计算相对路径
                rel_path = os.path.relpath(root, source_folder)
                if rel_path == '.':
                    target_root = target_folder
                else:
                    target_root = os.path.join(target_folder, rel_path)
                
                # 创建目标目录
                os.makedirs(target_root, exist_ok=True)
                
                # 复制文件
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_root, file)
                    
                    shutil.copy2(source_file, target_file)
                    current_file += 1
                    
                    # 计算进度百分比
                    progress_percent = (current_file / total_files) * 100
                    
                    if progress_callback:
                        progress_callback(progress_percent / 100, f"移动文件 ({current_file}/{total_files}): {file}")
            
            # 验证复制是否成功
            if os.path.exists(target_folder):
                # 删除源文件夹
                shutil.rmtree(source_folder)
                return True, f"文件夹移动成功: {target_folder}"
            else:
                return False, "文件夹移动失败: 目标文件夹未创建"
                
        except Exception as e:
            return False, f"移动文件夹时出错: {str(e)}"
    
    def export_to_device_path(self, zip_path: str, character_name: str, lb_path: str, progress_callback=None) -> Dict:
        """
        导出到指定的LB文件夹路径（移动文件夹而非复制ZIP）
        
        Args:
            zip_path (str): 语音包ZIP文件路径（实际上是临时文件夹路径）
            character_name (str): 角色名称
            lb_path (str): LB文件夹路径
            progress_callback (callable): 进度回调函数
            
        Returns:
            Dict: 导出结果
        """
        try:
            # 验证LB文件夹路径
            if not os.path.exists(lb_path):
                return {
                    'success': False,
                    'message': f"LB文件夹路径不存在: {lb_path}",
                    'device': None
                }
            
            if not os.path.isdir(lb_path):
                return {
                    'success': False,
                    'message': f"指定路径不是文件夹: {lb_path}",
                    'device': None
                }
            
            # 查找角色文件夹（zip_path实际上是临时目录）
            character_folder = os.path.join(zip_path, character_name)
            if not os.path.exists(character_folder):
                return {
                    'success': False,
                    'message': f"角色文件夹不存在: {character_folder}",
                    'device': None
                }
            
            # 验证8个子文件夹是否存在
            required_folders = ["breath", "moan", "greeting", "reaction", "tease", "touch", "orgasm", "impact"]
            missing_folders = []
            for folder in required_folders:
                folder_path = os.path.join(character_folder, folder)
                if not os.path.exists(folder_path):
                    missing_folders.append(folder)
            
            if missing_folders:
                return {
                    'success': False,
                    'message': f"缺少必需的子文件夹: {', '.join(missing_folders)}",
                    'device': None
                }
            
            # 检查磁盘空间
            space_ok, space_msg = self.check_disk_space(character_folder, lb_path, character_name=character_name)
            if not space_ok:
                return {
                    'success': False,
                    'message': space_msg,
                    'device': None
                }
            
            # 目标路径
            target_folder = os.path.join(lb_path, character_name)
            
            # 如果目标文件夹已存在，询问是否覆盖（这里直接覆盖）
            if os.path.exists(target_folder):
                shutil.rmtree(target_folder)
            
            # 移动文件夹
            move_success, move_msg = self.move_folder_with_progress(
                character_folder, target_folder, progress_callback
            )
            
            if move_success:
                return {
                    'success': True,
                    'message': f"角色文件夹已成功移动到: {target_folder}",
                    'device': {
                        'device': 'manual',
                        'fstype': 'unknown',
                        'lb_path': lb_path
                    }
                }
            else:
                return {
                    'success': False,
                    'message': move_msg,
                    'device': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"导出到LB文件夹失败: {str(e)}",
                'device': None
            }