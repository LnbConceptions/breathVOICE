# 所有动作参数列表 - 从台词模版.csv自动生成
# 总共242个参数，分为6个类别
# 自动生成时间: 2025-10-25 02:03:56

import csv
import os
from typing import Dict, List, Tuple

# 问候台词 (10个)
GREETING_PARAMS = [
    "greeting_1", "greeting_2", "greeting_3", "greeting_4",
    "greeting_5", "greeting_6", "greeting_7", "greeting_8",
    "greeting_9", "greeting_10"
]

# 高潮台词 (21个)
ORGASM_PARAMS = [
    "P1_orgasm_1", "P1_orgasm_2", "P1_orgasm_3", "P2_orgasm_1",
    "P2_orgasm_2", "P2_orgasm_3", "P3_orgasm_1", "P3_orgasm_2",
    "P3_orgasm_3", "P4_orgasm_1", "P4_orgasm_2", "P4_orgasm_3",
    "P5_orgasm_1", "P5_orgasm_2", "P5_orgasm_3", "P6_orgasm_1",
    "P6_orgasm_2", "P6_orgasm_3", "P0_orgasm_1", "P0_orgasm_2",
    "P0_orgasm_3"
]

# 兴奋台词 (59个)
REACTION_PARAMS = [
    "P0_B0_reaction_1", "P0_B0_reaction_2", "P0_B0_reaction_3", "P0_B0_reaction_4",
    "P0_B0_reaction_5", "P1_B1_B2_reaction_1", "P1_B1_B2_reaction_2", "P1_B1_B2_reaction_3",
    "P2_B1_B2_reaction_1", "P2_B1_B2_reaction_2", "P2_B1_B2_reaction_3", "P3_B1_B2_reaction_1",
    "P3_B1_B2_reaction_2", "P3_B1_B2_reaction_3", "P4_B1_B2_reaction_1", "P4_B1_B2_reaction_2",
    "P4_B1_B2_reaction_3", "P5_B1_B2_reaction_1", "P5_B1_B2_reaction_2", "P5_B1_B2_reaction_3",
    "P6_B1_B2_reaction_1", "P6_B1_B2_reaction_2", "P6_B1_B2_reaction_3", "P1_B3_B4_reaction_1",
    "P1_B3_B4_reaction_2", "P1_B3_B4_reaction_3", "P2_B3_B4_reaction_1", "P2_B3_B4_reaction_2",
    "P2_B3_B4_reaction_3", "P3_B3_B4_reaction_1", "P3_B3_B4_reaction_2", "P3_B3_B4_reaction_3",
    "P4_B3_B4_reaction_1", "P4_B3_B4_reaction_2", "P4_B3_B4_reaction_3", "P5_B3_B4_reaction_1",
    "P5_B3_B4_reaction_2", "P5_B3_B4_reaction_3", "P6_B3_B4_reaction_1", "P6_B3_B4_reaction_2",
    "P6_B3_B4_reaction_3", "P1_B5_reaction_1", "P1_B5_reaction_2", "P1_B5_reaction_3",
    "P2_B5_reaction_1", "P2_B5_reaction_2", "P2_B5_reaction_3", "P3_B5_reaction_1",
    "P3_B5_reaction_2", "P3_B5_reaction_3", "P4_B5_reaction_1", "P4_B5_reaction_2",
    "P4_B5_reaction_3", "P5_B5_reaction_1", "P5_B5_reaction_2", "P5_B5_reaction_3",
    "P6_B5_reaction_1", "P6_B5_reaction_2", "P6_B5_reaction_3"
]

# 挑逗台词 (59个)
TEASE_PARAMS = [
    "P0_B0_tease_1", "P0_B0_tease_2", "P0_B0_tease_3", "P0_B0_tease_4",
    "P0_B0_tease_5", "P1_B1_B2_tease_1", "P1_B1_B2_tease_2", "P1_B1_B2_tease_3",
    "P2_B1_B2_tease_1", "P2_B1_B2_tease_2", "P2_B1_B2_tease_3", "P3_B1_B2_tease_1",
    "P3_B1_B2_tease_2", "P3_B1_B2_tease_3", "P4_B1_B2_tease_1", "P4_B1_B2_tease_2",
    "P4_B1_B2_tease_3", "P5_B1_B2_tease_1", "P5_B1_B2_tease_2", "P5_B1_B2_tease_3",
    "P6_B1_B2_tease_1", "P6_B1_B2_tease_2", "P6_B1_B2_tease_3", "P1_B3_B4_tease_1",
    "P1_B3_B4_tease_2", "P1_B3_B4_tease_3", "P2_B3_B4_tease_1", "P2_B3_B4_tease_2",
    "P2_B3_B4_tease_3", "P3_B3_B4_tease_1", "P3_B3_B4_tease_2", "P3_B3_B4_tease_3",
    "P4_B3_B4_tease_1", "P4_B3_B4_tease_2", "P4_B3_B4_tease_3", "P5_B3_B4_tease_1",
    "P5_B3_B4_tease_2", "P5_B3_B4_tease_3", "P6_B3_B4_tease_1", "P6_B3_B4_tease_2",
    "P6_B3_B4_tease_3", "P1_B5_tease_1", "P1_B5_tease_2", "P1_B5_tease_3",
    "P2_B5_tease_1", "P2_B5_tease_2", "P2_B5_tease_3", "P3_B5_tease_1",
    "P3_B5_tease_2", "P3_B5_tease_3", "P4_B5_tease_1", "P4_B5_tease_2",
    "P4_B5_tease_3", "P5_B5_tease_1", "P5_B5_tease_2", "P5_B5_tease_3",
    "P6_B5_tease_1", "P6_B5_tease_2", "P6_B5_tease_3"
]

# 冲击台词 (21个)
IMPACT_PARAMS = [
    "P1_B0_impact_1", "P1_B0_impact_2", "P1_B0_impact_3", "P2_B0_impact_1",
    "P2_B0_impact_2", "P2_B0_impact_3", "P3_B0_impact_1", "P3_B0_impact_2",
    "P3_B0_impact_3", "P4_B0_impact_1", "P4_B0_impact_2", "P4_B0_impact_3",
    "P5_B0_impact_1", "P5_B0_impact_2", "P5_B0_impact_3", "P6_B0_impact_1",
    "P6_B0_impact_2", "P6_B0_impact_3", "P0_B0_impact_1", "P0_B0_impact_2",
    "P0_B0_impact_3"
]

# 触摸台词 (72个)
TOUCH_PARAMS = [
    "P0_B1_B2_LTit_long_1", "P0_B1_B2_LTit_long_2", "P0_B1_B2_LTit_long_3", "P0_B1_B2_RTit_long_1",
    "P0_B1_B2_RTit_long_2", "P0_B1_B2_RTit_long_3", "P0_B1_B2_LTit_short_1", "P0_B1_B2_LTit_short_2",
    "P0_B1_B2_LTit_short_3", "P0_B1_B2_RTit_short_1", "P0_B1_B2_RTit_short_2", "P0_B1_B2_RTit_short_3",
    "P0_B3_B4_LTit_long_1", "P0_B3_B4_LTit_long_2", "P0_B3_B4_LTit_long_3", "P0_B3_B4_RTit_long_1",
    "P0_B3_B4_RTit_long_2", "P0_B3_B4_RTit_long_3", "P0_B3_B4_LTit_short_1", "P0_B3_B4_LTit_short_2",
    "P0_B3_B4_LTit_short_3", "P0_B3_B4_RTit_short_1", "P0_B3_B4_RTit_short_2", "P0_B3_B4_RTit_short_3",
    "P0_B5_LTit_long_1", "P0_B5_LTit_long_2", "P0_B5_LTit_long_3", "P0_B5_RTit_long_1",
    "P0_B5_RTit_long_2", "P0_B5_RTit_long_3", "P0_B5_LTit_short_1", "P0_B5_LTit_short_2",
    "P0_B5_LTit_short_3", "P0_B5_RTit_short_1", "P0_B5_RTit_short_2", "P0_B5_RTit_short_3",
    "P0_B1_B2_LButt_long_1", "P0_B1_B2_LButt_long_2", "P0_B1_B2_LButt_long_3", "P0_B1_B2_RButt_long_1",
    "P0_B1_B2_RButt_long_2", "P0_B1_B2_RButt_long_3", "P0_B1_B2_LButt_short_1", "P0_B1_B2_LButt_short_2",
    "P0_B1_B2_LButt_short_3", "P0_B1_B2_RButt_short_1", "P0_B1_B2_RButt_short_2", "P0_B1_B2_RButt_short_3",
    "P0_B3_B4_LButt_long_1", "P0_B3_B4_LButt_long_2", "P0_B3_B4_LButt_long_3", "P0_B3_B4_RButt_long_1",
    "P0_B3_B4_RButt_long_2", "P0_B3_B4_RButt_long_3", "P0_B3_B4_LButt_short_1", "P0_B3_B4_LButt_short_2",
    "P0_B3_B4_LButt_short_3", "P0_B3_B4_RButt_short_1", "P0_B3_B4_RButt_short_2", "P0_B3_B4_RButt_short_3",
    "P0_B5_LButt_long_1", "P0_B5_LButt_long_2", "P0_B5_LButt_long_3", "P0_B5_RButt_long_1",
    "P0_B5_RButt_long_2", "P0_B5_RButt_long_3", "P0_B5_LButt_short_1", "P0_B5_LButt_short_2",
    "P0_B5_LButt_short_3", "P0_B5_RButt_short_1", "P0_B5_RButt_short_2", "P0_B5_RButt_short_3"
]

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
PARAM_CATEGORIES = {
    "greeting": GREETING_PARAMS,
    "orgasm": ORGASM_PARAMS,
    "reaction": REACTION_PARAMS,
    "tease": TEASE_PARAMS,
    "impact": IMPACT_PARAMS,
    "touch": TOUCH_PARAMS
}

# 参数说明
PARAM_DESCRIPTIONS = {
    "greeting": "Greeting lines — Character greets the user after system startup",
    "orgasm": "Orgasm lines — Dialogue when the female character herself is experiencing orgasm/climax (not approaching climax, but actually reaching it), expressing her own pleasure and sensations, tailored to different positions",
    "reaction": "Arousal reactions — Feedback when user thrusts actively for a period",
    "tease": "Tease lines — When user's motion pauses for a while, teasing dialogue",
    "impact": "Impact lines — Dialogue when insertion is detected after 20+ seconds idle",
    "touch": "Touch lines — Dialogue for touch parts, durations, positions, and breathing"
}

# 体位说明
POSITION_DESCRIPTIONS = {
    "P0": "Generic position (applies to all positions)",
    "P1": "Missionary (face-to-face traditional position)",
    "P2": "Left side entry",
    "P3": "Right side entry", 
    "P4": "Doggy style (rear entry)",
    "P5": "Cowgirl (female on top)",
    "P6": "Pin-down position"
}

# 呼吸频率档位说明
BREATHING_DESCRIPTIONS = {
    "B0": "Baseline state (steady breathing)",
    "B1": "Slight arousal (20 breaths/min)",
    "B2": "Moderate arousal (40 breaths/min)",
    "B3": "High arousal (60 breaths/min)",
    "B4": "Extreme arousal (80 breaths/min)",
    "B5": "Climax state (100 breaths/min)"
}

# 触摸部位说明
TOUCH_PART_DESCRIPTIONS = {
    "LTit": "Left breast",
    "RTit": "Right breast",
    "LButt": "Left thigh",
    "RButt": "Right thigh"
}

# 触摸时长说明
TOUCH_DURATION_DESCRIPTIONS = {
    "long": "Long touch (continuous contact over 200 ms)",
    "short": "Short touch (quick contact under 200 ms, e.g., slap)"
}

def get_total_param_count():
    """获取总参数数量"""
    return len(ALL_ACTION_PARAMS)

def get_params_by_category(category):
    """根据类别获取参数列表"""
    return PARAM_CATEGORIES.get(category, [])

def split_params_into_batches(batch_size=15):
    """将所有参数分批处理"""
    batches = []
    for i in range(0, len(ALL_ACTION_PARAMS), batch_size):
        batches.append(ALL_ACTION_PARAMS[i:i + batch_size])
    return batches

def auto_sync_from_csv(csv_path=None):
    """
    从CSV文件自动同步参数
    如果检测到CSV文件更新，自动重新生成action_parameters.py
    """
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
        
        print(f"成功从CSV同步了{len(all_params)}个参数")
        return True
        
    except Exception as e:
        print(f"从CSV同步参数时出错: {e}")
        return False

# 启动时自动同步
if __name__ != "__main__":
    auto_sync_from_csv()
