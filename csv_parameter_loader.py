# CSV参数加载器 - 自动从台词模版.csv加载和分类参数
import csv
import os
import re
from typing import Dict, List, Tuple

class CSVParameterLoader:
    """从台词模版.csv自动加载和分类动作参数"""
    
    def __init__(self, csv_file_path: str = None):
        """
        初始化CSV参数加载器
        
        Args:
            csv_file_path: CSV文件路径，默认为当前目录下的台词模版.csv
        """
        if csv_file_path is None:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(current_dir, "台词模版.csv")
            
        self.csv_file_path = csv_file_path
        self.action_params_path = os.path.join(os.path.dirname(csv_file_path), "action_parameters.py")
        self.all_params = []
        self.param_categories = {}
        
    def load_parameters_from_csv(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        从CSV文件加载所有参数并自动分类
        返回: (所有参数列表, 分类字典)
        """
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"CSV文件不存在: {self.csv_file_path}")
            
        all_params = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过标题行
                
                for row in reader:
                    if row and row[0].strip():  # 确保参数名不为空
                        param_name = row[0].strip()
                        all_params.append(param_name)
                        
        except Exception as e:
            raise Exception(f"读取CSV文件时出错: {e}")
            
        # 自动分类参数
        param_categories = self._classify_parameters(all_params)
        
        self.all_params = all_params
        self.param_categories = param_categories
        
        return all_params, param_categories
    
    def _classify_parameters(self, params: List[str]) -> Dict[str, List[str]]:
        """
        根据参数名称模式自动分类参数
        """
        categories = {
            "greeting": [],
            "orgasm": [],
            "reaction": [],
            "tease": [],
            "impact": [],
            "touch": []
        }
        
        for param in params:
            if re.match(r'^greeting_\d+$', param):
                categories["greeting"].append(param)
            elif re.search(r'_orgasm_\d+$', param):
                categories["orgasm"].append(param)
            elif re.search(r'_reaction_\d+$', param):
                categories["reaction"].append(param)
            elif re.search(r'_tease_\d+$', param):
                categories["tease"].append(param)
            elif re.search(r'_impact_\d+$', param):
                categories["impact"].append(param)
            elif re.search(r'_(LTit|RTit|LButt|RButt)_(long|short)_\d+$', param):
                categories["touch"].append(param)
            else:
                # 如果无法分类，记录警告但不中断
                print(f"警告: 无法分类参数 '{param}'，将其归入reaction类别")
                categories["reaction"].append(param)
                
        return categories
    
    def generate_action_parameters_content(self) -> str:
        """
        生成action_parameters.py文件的内容
        """
        if not self.all_params or not self.param_categories:
            self.load_parameters_from_csv()
            
        content = f"""# 所有动作参数列表 - 从台词模版.csv自动生成
# 总共{len(self.all_params)}个参数，分为6个类别
# 自动生成时间: {self._get_current_timestamp()}

import csv
import os
from typing import Dict, List, Tuple

# 问候台词 ({len(self.param_categories['greeting'])}个)
GREETING_PARAMS = {self._format_param_list(self.param_categories['greeting'])}

# 高潮台词 ({len(self.param_categories['orgasm'])}个)
ORGASM_PARAMS = {self._format_param_list(self.param_categories['orgasm'])}

# 兴奋台词 ({len(self.param_categories['reaction'])}个)
REACTION_PARAMS = {self._format_param_list(self.param_categories['reaction'])}

# 挑逗台词 ({len(self.param_categories['tease'])}个)
TEASE_PARAMS = {self._format_param_list(self.param_categories['tease'])}

# 冲击台词 ({len(self.param_categories['impact'])}个)
IMPACT_PARAMS = {self._format_param_list(self.param_categories['impact'])}

# 触摸台词 ({len(self.param_categories['touch'])}个)
TOUCH_PARAMS = {self._format_param_list(self.param_categories['touch'])}

# 所有参数的完整列表
ALL_ACTION_PARAMS = (
    GREETING_PARAMS + 
    ORGASM_PARAMS + 
    REACTION_PARAMS + 
    TEASE_PARAMS + 
    IMPACT_PARAMS + 
    TOUCH_PARAMS
)

# 参数分类映射
PARAM_CATEGORIES = {{
    "greeting": GREETING_PARAMS,
    "orgasm": ORGASM_PARAMS,
    "reaction": REACTION_PARAMS,
    "tease": TEASE_PARAMS,
    "impact": IMPACT_PARAMS,
    "touch": TOUCH_PARAMS
}}

# 参数说明
PARAM_DESCRIPTIONS = {{
    "greeting": "Greeting lines — Character greets the user after system startup",
    "orgasm": "Orgasm lines — Dialogue when the female character herself is experiencing orgasm/climax (not approaching climax, but actually reaching it), expressing her own pleasure and sensations, tailored to different positions",
    "reaction": "Arousal reactions — Feedback when user thrusts actively for a period",
    "tease": "Tease lines — When user's motion pauses for a while, teasing dialogue",
    "impact": "Impact lines — Dialogue when insertion is detected after 20+ seconds idle",
    "touch": "Touch lines — Dialogue for touch parts, durations, positions, and breathing"
}}

# 体位说明
POSITION_DESCRIPTIONS = {{
    "P0": "Generic position (applies to all positions)",
    "P1": "Missionary (face-to-face traditional position)",
    "P2": "Left side entry",
    "P3": "Right side entry", 
    "P4": "Doggy style (rear entry)",
    "P5": "Cowgirl (female on top)",
    "P6": "Pin-down position"
}}

# 呼吸频率档位说明
BREATHING_DESCRIPTIONS = {{
    "B0": "Baseline state (steady breathing)",
    "B1": "Slight arousal (20 breaths/min)",
    "B2": "Moderate arousal (40 breaths/min)",
    "B3": "High arousal (60 breaths/min)",
    "B4": "Extreme arousal (80 breaths/min)",
    "B5": "Climax state (100 breaths/min)"
}}

# 触摸部位说明
TOUCH_PART_DESCRIPTIONS = {{
    "LTit": "Left breast",
    "RTit": "Right breast",
    "LButt": "Left thigh",
    "RButt": "Right thigh"
}}

# 触摸时长说明
TOUCH_DURATION_DESCRIPTIONS = {{
    "long": "Long touch (continuous contact over 200 ms)",
    "short": "Short touch (quick contact under 200 ms, e.g., slap)"
}}

def get_total_param_count():
    \"\"\"获取总参数数量\"\"\"
    return len(ALL_ACTION_PARAMS)

def get_params_by_category(category):
    \"\"\"根据类别获取参数列表\"\"\"
    return PARAM_CATEGORIES.get(category, [])

def split_params_into_batches(batch_size=15):
    \"\"\"将所有参数分批处理\"\"\"
    batches = []
    for i in range(0, len(ALL_ACTION_PARAMS), batch_size):
        batches.append(ALL_ACTION_PARAMS[i:i + batch_size])
    return batches

def auto_sync_from_csv(csv_path=None):
    \"\"\"
    从CSV文件自动同步参数
    如果检测到CSV文件更新，自动重新生成action_parameters.py
    \"\"\"
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "台词模版.csv")
    
    try:
        from csv_parameter_loader import CSVParameterLoader
        loader = CSVParameterLoader(csv_path)
        all_params, categories = loader.load_parameters_from_csv()
        
        # 更新全局变量
        global ALL_ACTION_PARAMS, PARAM_CATEGORIES
        global GREETING_PARAMS, ORGASM_PARAMS, REACTION_PARAMS
        global TEASE_PARAMS, IMPACT_PARAMS, TOUCH_PARAMS
        
        GREETING_PARAMS = categories["greeting"]
        ORGASM_PARAMS = categories["orgasm"]
        REACTION_PARAMS = categories["reaction"]
        TEASE_PARAMS = categories["tease"]
        IMPACT_PARAMS = categories["impact"]
        TOUCH_PARAMS = categories["touch"]
        
        ALL_ACTION_PARAMS = all_params
        PARAM_CATEGORIES = categories
        
        print(f"成功从CSV同步了{{len(all_params)}}个参数")
        return True
        
    except Exception as e:
        print(f"从CSV同步参数时出错: {{e}}")
        return False

# 启动时自动同步
if __name__ != "__main__":
    auto_sync_from_csv()
"""
        
        return content
    
    def _format_param_list(self, params: List[str]) -> str:
        """格式化参数列表为Python代码"""
        if not params:
            return "[]"
            
        # 每行最多4个参数，保持代码可读性
        lines = []
        for i in range(0, len(params), 4):
            chunk = params[i:i+4]
            line = "    " + ", ".join(f'"{param}"' for param in chunk)
            lines.append(line)
            
        return "[\n" + ",\n".join(lines) + "\n]"
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def sync_parameters(self) -> bool:
        """
        同步参数：从CSV加载参数并更新action_parameters.py文件
        """
        try:
            # 加载CSV参数
            self.all_params, self.param_categories = self.load_parameters_from_csv()
            
            # 更新action_parameters.py文件
            return self.update_action_parameters_file()
            
        except Exception as e:
            print(f"参数同步失败: {e}")
            return False
    
    def update_action_parameters_file(self, target_file_path: str = None) -> bool:
        """
        更新action_parameters.py文件
        """
        if target_file_path is None:
            target_file_path = os.path.join(os.path.dirname(self.csv_file_path), "action_parameters.py")
            
        try:
            content = self.generate_action_parameters_content()
            
            with open(target_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            print(f"成功更新 {target_file_path}")
            print(f"总参数数量: {len(self.all_params)}")
            for category, params in self.param_categories.items():
                print(f"  {category}: {len(params)}个")
                
            return True
            
        except Exception as e:
            print(f"更新action_parameters.py时出错: {e}")
            return False

def main():
    """主函数 - 用于命令行调用"""
    import sys
    
    if len(sys.argv) < 2:
        csv_path = "台词模版.csv"
    else:
        csv_path = sys.argv[1]
        
    loader = CSVParameterLoader(csv_path)
    success = loader.update_action_parameters_file()
    
    if success:
        print("参数同步完成！")
    else:
        print("参数同步失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()