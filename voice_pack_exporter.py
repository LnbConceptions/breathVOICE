import os
import shutil
import zipfile
import soundfile as sf
import numpy as np
from tqdm import tqdm
import tempfile
import logging

class VoicePackExporter:
    """语音包导出器，负责处理音频格式转换、文件整理和压缩打包"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def convert_audio_format(self, input_path, output_path, target_sr=48000, target_channels=1, target_subtype='PCM_16'):
        """
        转换音频格式为48KHz, 16bit, 单声道 WAV
        
        Args:
            input_path (str): 输入音频文件路径
            output_path (str): 输出音频文件路径
            target_sr (int): 目标采样率，默认48000Hz
            target_channels (int): 目标声道数，默认1（单声道）
            target_subtype (str): 目标位深度，默认PCM_16（16bit）
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 读取音频文件
            data, sr = sf.read(input_path)
            
            # 如果是多声道，转换为单声道
            if len(data.shape) > 1 and data.shape[1] > 1:
                # 取平均值转换为单声道
                data = np.mean(data, axis=1)
            
            # 重采样到目标采样率
            if sr != target_sr:
                # 使用简单的线性插值重采样
                from scipy import signal
                # 如果没有scipy，使用numpy的插值
                try:
                    data = signal.resample(data, int(len(data) * target_sr / sr))
                except ImportError:
                    # 使用numpy的线性插值作为备选方案
                    old_indices = np.arange(len(data))
                    new_length = int(len(data) * target_sr / sr)
                    new_indices = np.linspace(0, len(data) - 1, new_length)
                    data = np.interp(new_indices, old_indices, data)
            
            # 确保数据类型正确
            data = data.astype(np.float32)
            
            # 写入新的音频文件
            sf.write(output_path, data, target_sr, subtype=target_subtype)
            
            self.logger.info(f"音频转换成功: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"音频转换失败 {input_path}: {str(e)}")
            return False
    
    def copy_and_organize_voice_files(self, source_voices_dir, temp_export_dir, character_name, progress_callback=None):
        """
        复制并整理语音文件，排除temp文件夹，转换音频格式
        
        Args:
            source_voices_dir (str): 源语音文件夹路径（如：精灵公主_Voices）
            temp_export_dir (str): 临时导出目录
            character_name (str): 角色名称
            progress_callback (callable): 进度回调函数
        
        Returns:
            tuple: (成功数量, 总数量, 错误列表)
        """
        if not os.path.exists(source_voices_dir):
            raise FileNotFoundError(f"源语音目录不存在: {source_voices_dir}")
        
        # 创建目标目录（使用角色名称，不带_Voices后缀）
        target_dir = os.path.join(temp_export_dir, character_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # 定义需要处理的子文件夹（排除temp）
        target_folders = ["greeting", "orgasm", "reaction", "tease", "impact", "touch"]
        
        success_count = 0
        total_count = 0
        errors = []
        
        # 统计总文件数
        for folder_name in target_folders:
            folder_path = os.path.join(source_voices_dir, folder_name)
            if os.path.exists(folder_path):
                wav_files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
                total_count += len(wav_files)
        
        processed_count = 0
        
        # 处理每个子文件夹
        for folder_name in target_folders:
            source_folder = os.path.join(source_voices_dir, folder_name)
            target_folder = os.path.join(target_dir, folder_name)
            
            if not os.path.exists(source_folder):
                self.logger.warning(f"源文件夹不存在，跳过: {source_folder}")
                continue
            
            # 创建目标文件夹
            os.makedirs(target_folder, exist_ok=True)
            
            # 获取所有wav文件
            wav_files = [f for f in os.listdir(source_folder) if f.endswith('.wav')]
            
            for wav_file in wav_files:
                source_file = os.path.join(source_folder, wav_file)
                target_file = os.path.join(target_folder, wav_file)
                
                try:
                    # 转换音频格式
                    if self.convert_audio_format(source_file, target_file):
                        success_count += 1
                    else:
                        errors.append(f"音频转换失败: {wav_file}")
                        
                except Exception as e:
                    errors.append(f"处理文件失败 {wav_file}: {str(e)}")
                
                processed_count += 1
                
                # 更新进度
                if progress_callback:
                    progress = processed_count / total_count if total_count > 0 else 0
                    progress_callback(progress, f"处理文件: {wav_file}")
        
        return success_count, total_count, errors
    
    def create_voice_pack_zip(self, temp_export_dir, output_zip_path, character_name, progress_callback=None):
        """
        创建语音包ZIP文件
        
        Args:
            temp_export_dir (str): 临时导出目录
            output_zip_path (str): 输出ZIP文件路径
            character_name (str): 角色名称
            progress_callback (callable): 进度回调函数
        
        Returns:
            bool: 是否成功创建ZIP文件
        """
        try:
            character_dir = os.path.join(temp_export_dir, character_name)
            
            if not os.path.exists(character_dir):
                raise FileNotFoundError(f"角色目录不存在: {character_dir}")
            
            # 统计需要压缩的文件数量
            total_files = 0
            for root, dirs, files in os.walk(character_dir):
                total_files += len(files)
            
            processed_files = 0
            
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(character_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 计算在ZIP中的相对路径
                        arcname = os.path.relpath(file_path, temp_export_dir)
                        zipf.write(file_path, arcname)
                        
                        processed_files += 1
                        
                        # 更新进度
                        if progress_callback:
                            progress = processed_files / total_files if total_files > 0 else 0
                            progress_callback(progress, f"压缩文件: {file}")
            
            self.logger.info(f"ZIP文件创建成功: {output_zip_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建ZIP文件失败: {str(e)}")
            return False
    
    def export_voice_pack(self, character_name, source_voices_dir, output_dir, progress_callback=None):
        """
        导出完整的语音包
        
        Args:
            character_name (str): 角色名称
            source_voices_dir (str): 源语音文件夹路径
            output_dir (str): 输出目录
            progress_callback (callable): 进度回调函数，接收(progress, message)参数
        
        Returns:
            dict: 导出结果 {
                'success': bool,
                'zip_path': str,
                'message': str,
                'stats': {
                    'success_count': int,
                    'total_count': int,
                    'errors': list
                }
            }
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                if progress_callback:
                    progress_callback(0.1, "开始处理语音文件...")
                
                # 复制并整理文件
                success_count, total_count, errors = self.copy_and_organize_voice_files(
                    source_voices_dir, temp_dir, character_name,
                    lambda p, m: progress_callback(0.1 + p * 0.7, m) if progress_callback else None
                )
                
                if progress_callback:
                    progress_callback(0.8, "开始压缩打包...")
                
                # 创建ZIP文件
                zip_filename = f"{character_name}.zip"
                zip_path = os.path.join(output_dir, zip_filename)
                
                zip_success = self.create_voice_pack_zip(
                    temp_dir, zip_path, character_name,
                    lambda p, m: progress_callback(0.8 + p * 0.2, m) if progress_callback else None
                )
                
                if progress_callback:
                    progress_callback(1.0, "导出完成！")
                
                if zip_success:
                    return {
                        'success': True,
                        'zip_path': zip_path,
                        'message': f"语音包导出成功！文件保存在: {zip_path}",
                        'stats': {
                            'success_count': success_count,
                            'total_count': total_count,
                            'errors': errors
                        }
                    }
                else:
                    return {
                        'success': False,
                        'zip_path': None,
                        'message': "ZIP文件创建失败",
                        'stats': {
                            'success_count': success_count,
                            'total_count': total_count,
                            'errors': errors
                        }
                    }
                    
        except Exception as e:
            error_msg = f"导出语音包失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'zip_path': None,
                'message': error_msg,
                'stats': {
                    'success_count': 0,
                    'total_count': 0,
                    'errors': [error_msg]
                }
            }