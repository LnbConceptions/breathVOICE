import os
import shutil
from PIL import Image
import json
import sys

class CharacterFileManager:
    def __init__(self, base_path=None):
        if base_path is None:
            # 检测是否为打包环境
            if getattr(sys, 'frozen', False):
                # 打包环境：使用用户文档目录
                user_docs = os.path.expanduser("~/Documents")
                self.base_path = os.path.join(user_docs, "breathVOICE", "Characters")
            else:
                # 开发环境：使用项目根目录
                self.base_path = 'Characters'
        else:
            self.base_path = base_path
        self.ensure_base_directory()
    
    def ensure_base_directory(self):
        """确保Characters基础目录存在"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def create_character_directory(self, character_name):
        """为角色创建完整的目录结构"""
        character_path = os.path.join(self.base_path, character_name)
        
        # 创建主目录
        if not os.path.exists(character_path):
            os.makedirs(character_path)
        
        # 创建子目录
        subdirs = ['avatars', 'reference_sound', 'description', 'script', f'{character_name}_Voices']
        for subdir in subdirs:
            subdir_path = os.path.join(character_path, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
        
        # 在Voices目录下创建台词类型子目录
        voice_path = os.path.join(character_path, f'{character_name}_Voices')
        voice_subdirs = ['greeting', 'impact', 'orgasm', 'reaction', 'tease', 'touch', 'breath', 'moan']
        for voice_subdir in voice_subdirs:
            voice_subdir_path = os.path.join(voice_path, voice_subdir)
            if not os.path.exists(voice_subdir_path):
                os.makedirs(voice_subdir_path)
        
        return character_path
    
    def save_character_avatar(self, character_name, avatar_file):
        """保存角色头像并生成缩略图"""
        character_path = os.path.join(self.base_path, character_name)
        avatars_path = os.path.join(character_path, 'avatars')
        
        if not os.path.exists(avatars_path):
            os.makedirs(avatars_path)
        
        # 保存原始头像
        original_path = os.path.join(avatars_path, f'original{os.path.splitext(avatar_file.name)[1]}')
        with open(original_path, 'wb') as f:
            f.write(avatar_file.read())
        
        # 生成50x50缩略图
        thumbnail_path = os.path.join(avatars_path, 'thumbnail_50x50.jpg')
        try:
            with Image.open(original_path) as img:
                img.thumbnail((50, 50), Image.Resampling.LANCZOS)
                # 创建正方形背景
                background = Image.new('RGB', (50, 50), (255, 255, 255))
                # 计算居中位置
                x = (50 - img.width) // 2
                y = (50 - img.height) // 2
                background.paste(img, (x, y))
                background.save(thumbnail_path, 'JPEG', quality=95)
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return original_path, None
        
        return original_path, thumbnail_path
    
    def save_character_description(self, character_name, description):
        """保存角色描述到文本文件"""
        character_path = os.path.join(self.base_path, character_name)
        description_path = os.path.join(character_path, 'description')
        
        if not os.path.exists(description_path):
            os.makedirs(description_path)
        
        description_file = os.path.join(description_path, 'character_info.txt')
        with open(description_file, 'w', encoding='utf-8') as f:
            f.write(description)
        
        return description_file
    
    def save_llm_config(self, character_name, config_data):
        """保存LLM配置到JSON文件"""
        character_path = os.path.join(self.base_path, character_name)
        config_file = os.path.join(character_path, 'llm_config.json')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        return config_file
    
    def get_character_avatar_path(self, character_name):
        """获取角色头像路径"""
        avatars_path = os.path.join(self.base_path, character_name, 'avatars')
        
        # 优先返回缩略图路径
        thumbnail_path = os.path.join(avatars_path, 'thumbnail_50x50.jpg')
        if os.path.exists(thumbnail_path):
            return thumbnail_path
        
        # 查找原始头像文件
        if os.path.exists(avatars_path):
            for file in os.listdir(avatars_path):
                if file.startswith('original'):
                    return os.path.join(avatars_path, file)
        
        return None

    def get_character_original_avatar_path(self, character_name):
        """获取角色原始头像路径"""
        avatars_path = os.path.join(self.base_path, character_name, 'avatars')
        if os.path.exists(avatars_path):
            for file in os.listdir(avatars_path):
                if file.startswith('original'):
                    return os.path.join(avatars_path, file)
        return None
    
    def get_character_description(self, character_name):
        """读取角色描述"""
        description_file = os.path.join(self.base_path, character_name, 'description', 'character_info.txt')
        
        if os.path.exists(description_file):
            with open(description_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def delete_character_directory(self, character_name):
        """删除角色的整个目录"""
        character_path = os.path.join(self.base_path, character_name)
        
        if os.path.exists(character_path):
            shutil.rmtree(character_path)
            return True
        
        return False
    
    def list_characters(self):
        """列出所有角色目录"""
        if not os.path.exists(self.base_path):
            return []
        
        characters = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                characters.append(item)
        
        return characters
    
    def get_script_directory(self, character_name):
        """获取角色脚本目录路径"""
        return os.path.join(self.base_path, character_name, 'script')
    
    def get_voice_directory(self, character_name):
        """获取角色语音目录路径"""
        return os.path.join(self.base_path, character_name, f'{character_name}_Voices')
    
    def save_reference_sound(self, character_name, sound_file):
        """保存角色参考声音文件"""
        character_path = os.path.join(self.base_path, character_name)
        reference_sound_path = os.path.join(character_path, 'reference_sound')
        
        if not os.path.exists(reference_sound_path):
            os.makedirs(reference_sound_path)
        
        # 保存参考声音文件
        file_extension = os.path.splitext(sound_file.name)[1]
        sound_path = os.path.join(reference_sound_path, f'reference{file_extension}')
        
        with open(sound_path, 'wb') as f:
            f.write(sound_file.read())
        
        return sound_path
    
    def get_reference_sound_path(self, character_name):
        """获取角色参考声音文件路径"""
        reference_sound_path = os.path.join(self.base_path, character_name, 'reference_sound')
        
        if os.path.exists(reference_sound_path):
            # 查找参考声音文件
            for file in os.listdir(reference_sound_path):
                if file.startswith('reference'):
                    return os.path.join(reference_sound_path, file)
        
        return None