import os
import shutil
import zipfile
import soundfile as sf
import numpy as np
from tqdm import tqdm
import tempfile
import logging
import subprocess

class VoicePackExporter:
    """语音包导出器，负责处理音频格式转换、文件整理和压缩打包"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # wav_to_bre转换程序的路径
        self.wav_to_bre_path = os.path.join(os.path.dirname(__file__), 'voice_packs', 'wav_to_bre_single')
    
    def normalize_audio_to_dbfs(self, audio_data, target_dbfs=-10.0):
        """
        将音频数据标准化到指定的dBFS电平
        
        Args:
            audio_data (numpy.ndarray): 输入音频数据
            target_dbfs (float): 目标dBFS电平，默认-10.0
        
        Returns:
            numpy.ndarray: 标准化后的音频数据
        """
        # 计算当前音频的RMS值
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # 避免除零错误
        if rms == 0:
            return audio_data
        
        # 计算当前dBFS
        current_dbfs = 20 * np.log10(rms)
        
        # 计算需要的增益
        gain_db = target_dbfs - current_dbfs
        gain_linear = 10 ** (gain_db / 20)
        
        # 应用增益
        normalized_audio = audio_data * gain_linear
        
        # 防止削波，确保峰值不超过1.0
        peak = np.max(np.abs(normalized_audio))
        if peak > 1.0:
            normalized_audio = normalized_audio / peak
        
        return normalized_audio
        
    def convert_wav_to_bre(self, input_wav_path, output_bre_path):
        """
        使用wav_to_bre程序将WAV文件转换为BRE格式
        
        Args:
            input_wav_path (str): 输入WAV文件路径
            output_bre_path (str): 输出BRE文件路径
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_bre_path), exist_ok=True)
            
            # 调用wav_to_bre程序（不使用check=True，因为程序可能返回非零退出码但仍然成功）
            result = subprocess.run([
                self.wav_to_bre_path,
                input_wav_path,
                output_bre_path
            ], capture_output=True, text=True)
            
            # 检查输出文件是否存在来判断转换是否成功
            if os.path.exists(output_bre_path) and os.path.getsize(output_bre_path) > 0:
                self.logger.info(f"WAV转BRE成功: {input_wav_path} -> {output_bre_path}")
                return True
            else:
                self.logger.error(f"WAV转BRE失败 {input_wav_path}: 输出文件不存在或为空")
                if result.stderr:
                    self.logger.error(f"错误信息: {result.stderr}")
                return False
            
        except Exception as e:
            self.logger.error(f"WAV转BRE异常 {input_wav_path}: {str(e)}")
            return False
    
    def convert_audio_format(self, input_path, output_path, target_sr=48000, target_channels=1, target_subtype='PCM_16'):
        """
        转换音频格式为48KHz, 16bit, 单声道 WAV，并调整音频电平到-10dbfs
        
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
                # 使用numpy的线性插值重采样（避免scipy依赖）
                old_indices = np.arange(len(data))
                new_length = int(len(data) * target_sr / sr)
                new_indices = np.linspace(0, len(data) - 1, new_length)
                data = np.interp(new_indices, old_indices, data)
            
            # 调整音频电平到-10dbfs
            data = self.normalize_audio_to_dbfs(data, target_dbfs=-10.0)
            
            # 确保数据类型正确
            data = data.astype(np.float32)
            
            # 写入新的音频文件
            sf.write(output_path, data, target_sr, subtype=target_subtype)
            
            self.logger.info(f"音频转换成功: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"音频转换失败 {input_path}: {str(e)}")
            return False
    
    def copy_and_organize_voice_files(self, source_voices_dir, temp_export_dir, character_name, progress_callback=None, material_pack=None, stop_flag=None):
        """
        复制并整理语音文件，排除temp文件夹，转换音频格式并生成BRE文件
        
        Args:
            source_voices_dir (str): 源语音文件夹路径（角色文件夹路径）
            temp_export_dir (str): 临时导出目录
            character_name (str): 角色名称
            progress_callback (callable): 进度回调函数
            material_pack (str): 素材包名称，用于获取breath和moan文件
        
        Returns:
            tuple: (成功数量, 总数量, 错误列表)
        """
        if not os.path.exists(source_voices_dir):
            raise FileNotFoundError(f"源语音目录不存在: {source_voices_dir}")
        
        # 创建目标目录（使用角色名称，不带_Voices后缀）
        target_dir = os.path.join(temp_export_dir, character_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # 定义需要处理的子文件夹
        character_folders = ["greeting", "orgasm", "reaction", "tease", "impact", "touch"]  # 从角色文件夹获取
        material_folders = ["breath", "moan"]  # 从素材包获取
        
        success_count = 0
        total_count = 0
        errors = []
        
        # 统计角色文件夹中的文件数
        for folder_name in character_folders:
            folder_path = os.path.join(source_voices_dir, folder_name)
            if os.path.exists(folder_path):
                wav_files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
                total_count += len(wav_files)
        
        # 统计素材包中的文件数
        if material_pack:
            material_pack_dir = os.path.join(os.path.dirname(__file__), "Reference Voices", material_pack)
            for folder_name in material_folders:
                folder_path = os.path.join(material_pack_dir, folder_name)
                if os.path.exists(folder_path):
                    wav_files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
                    total_count += len(wav_files)
        
        processed_count = 0
        
        # 处理角色文件夹中的文件
        for folder_name in character_folders:
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
                # 检查停止标志
                if stop_flag and stop_flag.is_set():
                    break
                    
                source_file = os.path.join(source_folder, wav_file)
                
                # 创建临时WAV文件（48KHz格式）
                temp_wav_file = os.path.join(target_folder, wav_file)
                # 创建BRE文件
                bre_file = os.path.join(target_folder, wav_file.replace('.wav', '.bre'))
                
                try:
                    # 先转换音频格式到临时WAV文件
                    if self.convert_audio_format(source_file, temp_wav_file):
                        # 再将WAV转换为BRE格式
                        if self.convert_wav_to_bre(temp_wav_file, bre_file):
                            # 删除临时WAV文件，只保留BRE文件
                            os.remove(temp_wav_file)
                            success_count += 1
                        else:
                            errors.append(f"WAV转BRE失败: {wav_file}")
                    else:
                        errors.append(f"音频转换失败: {wav_file}")
                        
                except Exception as e:
                    errors.append(f"处理文件失败 {wav_file}: {str(e)}")
                
                processed_count += 1
                
                # 更新进度
                if progress_callback:
                    progress_callback(processed_count, total_count, f"处理角色文件: {wav_file}")
        
        # 处理素材包中的breath和moan文件
        if material_pack:
            material_pack_dir = os.path.join(os.path.dirname(__file__), "Reference Voices", material_pack)
            
            for folder_name in material_folders:
                source_folder = os.path.join(material_pack_dir, folder_name)
                target_folder = os.path.join(target_dir, folder_name)
                
                if not os.path.exists(source_folder):
                    self.logger.warning(f"素材包文件夹不存在，跳过: {source_folder}")
                    continue
                
                # 创建目标文件夹
                os.makedirs(target_folder, exist_ok=True)
                
                # 获取所有wav文件
                wav_files = [f for f in os.listdir(source_folder) if f.endswith('.wav')]
                
                for wav_file in wav_files:
                    source_file = os.path.join(source_folder, wav_file)
                    
                    # 创建临时WAV文件（48KHz格式）
                    temp_wav_file = os.path.join(target_folder, wav_file)
                    # 创建BRE文件
                    bre_file = os.path.join(target_folder, wav_file.replace('.wav', '.bre'))
                    
                    try:
                        # 先转换音频格式到临时WAV文件
                        if self.convert_audio_format(source_file, temp_wav_file):
                            # 再将WAV转换为BRE格式
                            if self.convert_wav_to_bre(temp_wav_file, bre_file):
                                # 删除临时WAV文件，只保留BRE文件
                                os.remove(temp_wav_file)
                                success_count += 1
                            else:
                                errors.append(f"WAV转BRE失败: {wav_file}")
                        else:
                            errors.append(f"音频转换失败: {wav_file}")
                            
                    except Exception as e:
                        errors.append(f"处理素材包文件失败 {wav_file}: {str(e)}")
                    
                    processed_count += 1
                    
                    # 更新进度
                    if progress_callback:
                        progress_callback(processed_count, total_count, f"处理素材包文件: {wav_file}")
        
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
                            progress_callback(processed_files, total_files, f"压缩文件: {file}")
            
            self.logger.info(f"ZIP文件创建成功: {output_zip_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建ZIP文件失败: {str(e)}")
            return False
    
    def copy_voice_pack_to_directory(self, source_voices_dir, target_directory, character_name, progress_callback=None, material_pack=None, stop_flag=None):
        """
        直接拷贝语音包文件夹到指定目录（不压缩zip），包含BRE转换和音频电平调整
        
        Args:
            source_voices_dir (str): 源语音文件夹路径（角色文件夹路径）
            target_directory (str): 目标目录路径
            character_name (str): 角色名称
            progress_callback (callable): 进度回调函数
            material_pack (str): 素材包名称，用于获取breath和moan文件
        
        Returns:
            dict: 包含成功状态、消息和详细信息的字典
        """
        try:
            if not os.path.exists(source_voices_dir):
                return {
                    "success": False,
                    "message": f"源语音目录不存在: {source_voices_dir}",
                    "details": {}
                }
            
            if not os.path.exists(target_directory):
                return {
                    "success": False,
                    "message": f"目标目录不存在: {target_directory}",
                    "details": {}
                }
            
            # 创建临时目录进行处理
            with tempfile.TemporaryDirectory() as temp_dir:
                # 检查停止标志
                if stop_flag and stop_flag.is_set():
                    return {"success": False, "message": "操作被用户取消", "details": {}}
                
                # 第一步：复制并整理语音文件，转换格式并调整电平
                if progress_callback:
                    progress_callback(0, "开始复制和转换音频文件...")
                
                success_count, total_count, errors = self.copy_and_organize_voice_files(
                    source_voices_dir, temp_dir, character_name, 
                    lambda current, total, msg: progress_callback(current / total * 70, msg) if progress_callback and total > 0 else None,
                    material_pack, stop_flag
                )
                
                # 检查停止标志
                if stop_flag and stop_flag.is_set():
                    return {"success": False, "message": "操作被用户取消", "details": {}}
                
                if success_count == 0:
                    return {
                        "success": False,
                        "message": "没有成功处理任何音频文件",
                        "details": {"errors": errors}
                    }
                
                # 第二步：转换WAV到BRE格式
                if progress_callback:
                    progress_callback(70, "开始转换BRE格式...")
                
                # 检查停止标志
                if stop_flag and stop_flag.is_set():
                    return {"success": False, "message": "操作被用户取消", "details": {}}
                
                temp_character_dir = os.path.join(temp_dir, character_name)
                bre_success_count, bre_total_count, bre_errors = self.convert_all_wav_to_bre(
                    temp_character_dir,
                    lambda progress, msg: progress_callback(70 + progress * 0.2, msg) if progress_callback else None,
                    stop_flag
                )
                
                # 检查停止标志
                if stop_flag and stop_flag.is_set():
                    return {"success": False, "message": "操作被用户取消", "details": {}}
                
                # 第三步：拷贝到目标目录
                if progress_callback:
                    progress_callback(90, "开始拷贝到目标位置...")
                
                final_target_dir = os.path.join(target_directory, character_name)
                
                # 如果目标目录已存在，先删除
                if os.path.exists(final_target_dir):
                    shutil.rmtree(final_target_dir)
                
                # 拷贝整个角色文件夹到目标位置
                shutil.copytree(temp_character_dir, final_target_dir)
                
                if progress_callback:
                    progress_callback(100, "拷贝完成！")
                
                return {
                    "success": True,
                    "message": f"语音包已成功拷贝到: {final_target_dir}",
                    "details": {
                        "character_name": character_name,
                        "target_path": final_target_dir,
                        "audio_files": {
                            "processed": success_count,
                            "total": total_count,
                            "errors": errors
                        },
                        "bre_files": {
                            "converted": bre_success_count,
                            "total": bre_total_count,
                            "errors": bre_errors
                        }
                    }
                }
                
        except Exception as e:
            error_msg = f"拷贝语音包时发生错误: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "details": {"exception": str(e)}
            }
    
    def convert_all_wav_to_bre(self, character_dir, progress_callback=None, stop_flag=None):
        """
        转换角色目录下所有WAV文件为BRE格式
        
        Args:
            character_dir (str): 角色目录路径
            progress_callback (callable): 进度回调函数
        
        Returns:
            tuple: (成功数量, 总数量, 错误列表)
        """
        success_count = 0
        total_count = 0
        errors = []
        
        # 统计所有WAV文件
        wav_files = []
        for root, dirs, files in os.walk(character_dir):
            for file in files:
                if file.endswith('.wav'):
                    wav_files.append(os.path.join(root, file))
        
        total_count = len(wav_files)
        
        if total_count == 0:
            return success_count, total_count, errors
        
        # 转换每个WAV文件
        for i, wav_file in enumerate(wav_files):
            # 检查停止标志
            if stop_flag and stop_flag.is_set():
                break
                
            try:
                # 生成BRE文件路径
                bre_file = wav_file.replace('.wav', '.bre')
                
                # 转换WAV到BRE
                if self.convert_wav_to_bre(wav_file, bre_file):
                    success_count += 1
                    # 删除原WAV文件（只保留BRE文件）
                    os.remove(wav_file)
                else:
                    errors.append(f"BRE转换失败: {wav_file}")
                
                # 更新进度
                if progress_callback:
                    progress = (i + 1) / total_count * 100
                    progress_callback(progress, f"转换BRE文件 {i + 1}/{total_count}")
                    
            except Exception as e:
                error_msg = f"处理文件 {wav_file} 时出错: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return success_count, total_count, errors
        """
        导出完整的语音包
        
        Args:
            character_name (str): 角色名称
            source_voices_dir (str): 源语音文件夹路径
            output_dir (str): 输出目录
            progress_callback (callable): 进度回调函数，接收(progress, message)参数
            material_pack (str): 素材包名称，用于获取breath和moan文件
        
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
                    progress_callback(0, 1, "开始处理语音文件...")
                
                # 复制并整理文件，传入素材包参数
                success_count, total_count, errors = self.copy_and_organize_voice_files(
                    source_voices_dir, temp_dir, character_name,
                    lambda current, total, message: progress_callback(int(0.1 * 100 + (current / total) * 70), 100, message) if progress_callback and total > 0 else None,
                    material_pack=material_pack
                )
                
                if progress_callback:
                    progress_callback(80, 100, "开始压缩打包...")
                
                # 创建ZIP文件
                zip_filename = f"{character_name}.zip"
                zip_path = os.path.join(output_dir, zip_filename)
                
                zip_success = self.create_voice_pack_zip(
                    temp_dir, zip_path, character_name,
                    lambda current, total, message: progress_callback(int(80 + (current / total) * 20), 100, message) if progress_callback and total > 0 else None
                )
                
                if progress_callback:
                    progress_callback(100, 100, "导出完成！")
                
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