import gradio as gr
import json
import csv
import os
import time
from typing import List

from dialogue_generator import DialogueGenerator
from file_manager import CharacterFileManager

TEMPLATE_CSV_PATH = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/台词模版.csv"

# 控制生成/停止的即时标志（事件函数可修改，生成协程可读取）
stop_requested_flag = [False]
is_generating_flag = [False]


def build_dialogue_generation_ui(db):
    generator = DialogueGenerator()
    file_manager = CharacterFileManager()

    css = """
    #start_btn { background-color: #166534 !important; color: white !important; }
    #stop_btn { background-color: #991b1b !important; color: white !important; }
    #save_btn { background-color: #166534 !important; color: white !important; }
    #char_desc_box { height: 400px; overflow-y: auto; }
    """

    with gr.Blocks(title="Dialogue Generation", theme=gr.themes.Default(), css=css) as dialogue_generation_interface:
        gr.Markdown("## 第三步：台词生成")

        # 顶部选择区
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    character_dropdown = gr.Dropdown(
                        label="选择角色",
                        choices=[(c[1], c[0]) for c in db.get_characters()],
                        interactive=True,
                        scale=4
                    )
                    refresh_char_btn = gr.Button("🔄", variant="secondary", size="sm", min_width=40, scale=0)
            with gr.Column():
                with gr.Row():
                    llm_config_dropdown = gr.Dropdown(
                        label="选择LLM配置",
                        choices=[(c[1], c[0]) for c in db.get_llm_configs()],
                        interactive=True,
                        scale=4
                    )
                    refresh_llm_btn = gr.Button("🔄", variant="secondary", size="sm", min_width=40, scale=0)
            language_dropdown = gr.Dropdown(
                label="语言",
                choices=["中文", "English", "日本語"],
                value="中文",
                interactive=True,
            )

        # 角色形象与描述展示
        with gr.Row():
            char_image = gr.Image(label="", interactive=False, width=300, height=400)
            char_desc_box = gr.Textbox(label="", interactive=False, lines=18, elem_id="char_desc_box", max_lines=18)

        # 在"语言"与"提示词预览"之间增加开始/停止按钮（并排）
        with gr.Row():
            start_btn = gr.Button("🎯 生成选中的台词", variant="primary", interactive=False)
            stop_btn = gr.Button("🛑 停止生成", elem_id="stop_btn", interactive=False)

        # 提示词预览（可折叠，默认收起）
        with gr.Accordion("提示词预览（最终注入LLM的JSON）", open=False):
            prompt_preview_tb = gr.Textbox(lines=16)

        # 编辑布局
        with gr.Tab("固定台词"):
            rows_init = _load_rows_from_template_all()
            select_checks: List[gr.Checkbox] = []
            ap_texts: List[gr.Textbox] = []
            line_texts: List[gr.Textbox] = []

            # 全选/全不选置于顶部
            with gr.Row():
                select_all_btn = gr.Button("全选")
                select_none_btn = gr.Button("全不选")

            with gr.Column():
                for sel, ap, tx in rows_init:
                    with gr.Row():
                        chk = gr.Checkbox(label="", value=True, scale=0, min_width=32, show_label=False)  # 默认选中
                        ap_tb = gr.Textbox(label="", value=ap, interactive=False, scale=3, show_label=False)
                        line_tb = gr.Textbox(label="", value=tx or "", interactive=True, scale=9, show_label=False)
                    select_checks.append(chk)
                    ap_texts.append(ap_tb)
                    line_texts.append(line_tb)

            def select_all_v2():
                return [True] * len(select_checks)

            def select_none_v2():
                return [False] * len(select_checks)

            select_all_btn.click(fn=select_all_v2, inputs=[], outputs=select_checks)
            select_none_btn.click(fn=select_none_v2, inputs=[], outputs=select_checks)

            # 生成流函数（由‘开始生成’触发），支持停止标志
            def gen_selected_v2(character_id: int, llm_config_id: int, language: str, *vals):
                n = len(select_checks)
                sel_vals = list(vals[:n])
                aps = list(vals[n:2*n])
                lines_in = list(vals[2*n:3*n])

                # 按键状态：生成中 -> 开始不可用、停止可用
                is_generating_flag[0] = True
                stop_requested_flag[0] = False

                if not character_id or not llm_config_id or not language:
                    is_generating_flag[0] = False
                    yield gr.update(value=""), *lines_in, gr.update(interactive=False), gr.update(interactive=False)
                    return

                char = db.get_character(character_id)
                character_name = char[1]
                # 读取角色描述文本，优先从文件系统，找不到则回退数据库
                character_description = file_manager.get_character_description(character_name)
                if not isinstance(character_description, str) or not character_description.strip():
                    character_description = char[2] or ""
                # 占位符替换
                character_description = character_description.replace("{{char}}", character_name).replace("{{user}}", "用户")
                llm_cfg = db.get_llm_config(llm_config_id)

                # 找到选中的项目索引
                indices = [i for i in range(n) if bool(sel_vals[i])]
                # 如果没有选中任何项目，则不生成任何内容
                if not indices:
                    is_generating_flag[0] = False
                    yield gr.update(value=""), *lines_in, gr.update(interactive=True), gr.update(interactive=False)
                    return
                current_lines = [l if isinstance(l, str) else "" for l in lines_in]

                # 先更新一次按键状态（开始禁用、停止启用）
                yield gr.update(value=""), *current_lines, gr.update(interactive=False), gr.update(interactive=True)

                for idx in indices:
                    if stop_requested_flag[0]:
                        break
                    param = aps[idx]
                    if not isinstance(param, str) or not param:
                        continue
                    prompt = generator.create_comprehensive_prompt_template(
                        character_name=character_name,
                        character_description=character_description,
                        language=language,
                        action_params=[param],
                        event_category=None,
                    )
                    prompt_text = json.dumps(prompt, ensure_ascii=False, indent=2)

                    def status_cb(msg: str):
                        pass  # 不再显示状态日志

                    try:
                        result_text = generator.call_llm_api_with_status(
                            llm_cfg, prompt, status_callback=status_cb, max_retries=2
                        )
                    except Exception:
                        result_text = ""

                    parsed = _parse_json_flex(result_text) if result_text else None
                    line = _extract_line_for_param(parsed, param) if parsed is not None else ""
                    if not line and isinstance(parsed, dict) and param in parsed:
                        v = parsed[param]
                        line = "" if v is None else str(v)
                    if not line and isinstance(parsed, str):
                        line = parsed
                    current_lines[idx] = line

                    # 生成过程中保持按键状态（开始禁用、停止启用）并更新提示词预览
                    yield gr.update(value=prompt_text), *current_lines, gr.update(interactive=False), gr.update(interactive=True)

                # 结束/停止后，恢复按键状态
                is_generating_flag[0] = False
                stop_requested_flag[0] = False

                valid_sel = bool(character_id) and bool(llm_config_id) and bool(language)
                start_state = gr.update(interactive=valid_sel)
                stop_state = gr.update(interactive=False)
                yield gr.update(), *current_lines, start_state, stop_state

            # 开始生成：绑定到顶部按钮
            gen_inputs = [character_dropdown, llm_config_dropdown, language_dropdown] + select_checks + ap_texts + line_texts
            gen_outputs = [prompt_preview_tb] + line_texts + [start_btn, stop_btn]
            start_btn.click(
                fn=gen_selected_v2,
                inputs=gen_inputs,
                outputs=gen_outputs,
            )

            # 停止生成：仅设置停止标志，并保持按钮状态（生成中保持停止可用）
            def on_stop_clicked(character_id: int, llm_config_id: int, language: str):
                stop_requested_flag[0] = True
                if is_generating_flag[0]:
                    return gr.update(interactive=False), gr.update(interactive=True)
                valid_sel = bool(character_id) and bool(llm_config_id) and bool(language)
                return gr.update(interactive=valid_sel), gr.update(interactive=False)

            stop_btn.click(
                fn=on_stop_clicked,
                inputs=[character_dropdown, llm_config_dropdown, language_dropdown],
                outputs=[start_btn, stop_btn],
            )

            # 底部添加“保存”按钮：保存为 CSV 到角色 script 文件夹
            save_btn = gr.Button("💾 保存", elem_id="save_btn")

            def on_save_clicked(character_id: int, language: str, *vals):
                n = len(ap_texts)
                aps = list(vals[:n])
                lines = list(vals[n:2*n])
                if not character_id:
                    return gr.update(value="保存失败：未选择角色")
                char = db.get_character(character_id)
                character_name = char[1]
                base_dir = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters"
                target_dir = os.path.join(base_dir, character_name, "script")
                os.makedirs(target_dir, exist_ok=True)
                # 语言代码（用于文件名）
                lang_map = {"中文": "zh", "English": "en", "日本語": "ja"}
                lang_code = lang_map.get(language, "zh") if isinstance(language, str) else "zh"
                date_str = time.strftime("%Y%m%d")
                time_str = time.strftime("%H%M%S")
                file_path = os.path.join(target_dir, f"dialogue_{lang_code}_{date_str}_{time_str}.csv")
                try:
                    with open(file_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["动作参数", "台词"])  # 标题行
                        for ap, line in zip(aps, lines):
                            writer.writerow([ap, line or ""]) 
                    return gr.update(value=f"已保存：{file_path}")
                except Exception as e:
                    return gr.update(value=f"保存失败：{e}")

            # 保存结果提示（用一个简短文本显示保存路径或错误）
            save_status = gr.Textbox(label="保存状态", interactive=False)
            save_btn.click(
                fn=on_save_clicked,
                inputs=[character_dropdown, language_dropdown] + ap_texts + line_texts,
                outputs=[save_status],
            )

        # 自定义项目区域
        with gr.Tab("自定义台词"):
            gr.Markdown("### 自定义项目")
            gr.Markdown("在此处添加您自己的动作参数，系统将为您生成相应的台词。")
            
            # 自定义项目列表（预创建10行）
            custom_select_checks: List[gr.Checkbox] = []
            custom_ap_texts: List[gr.Textbox] = []
            custom_line_texts: List[gr.Textbox] = []
            custom_rows: List[gr.Row] = []
            
            # 预创建多行自定义项目
            with gr.Column(elem_id="custom_items_container"):
                for i in range(10):  # 预创建10行
                    with gr.Row(visible=(i == 0)) as custom_row:  # 只显示第一行
                        custom_chk = gr.Checkbox(label="", value=True, scale=0, min_width=32, show_label=False)  # 默认选中
                        custom_ap_tb = gr.Textbox(label="", value="", interactive=True, scale=3, show_label=False, placeholder="输入动作参数...")
                        custom_line_tb = gr.Textbox(label="", value="", interactive=False, scale=9, show_label=False, placeholder="生成的台词将显示在这里...")
                    custom_select_checks.append(custom_chk)
                    custom_ap_texts.append(custom_ap_tb)
                    custom_line_texts.append(custom_line_tb)
                    custom_rows.append(custom_row)
            
            # 自定义项目操作按钮
            with gr.Row():
                add_custom_btn = gr.Button("➕ 添加新项目")
                custom_select_all_btn = gr.Button("全选")
                custom_select_none_btn = gr.Button("全不选")
                delete_custom_btn = gr.Button("🗑️ 删除选中")
                generate_custom_btn = gr.Button("🎯 生成选中的台词")
            
            # 自定义项目状态显示
            custom_status = gr.Textbox(label="操作状态", interactive=False)
            
            # 自定义项目功能实现
            def add_custom_item():
                """添加新的自定义项目"""
                # 找到第一个隐藏的行并显示它
                for i, row in enumerate(custom_rows):
                    if not row.visible:
                        return [gr.update(visible=True) if j == i else gr.update() for j, _ in enumerate(custom_rows)] + [gr.update(value="已添加新项目")]
                return [gr.update() for _ in custom_rows] + [gr.update(value="已达到最大项目数量(10个)")]
            
            def delete_custom_items(*vals):
                """删除选中的自定义项目"""
                n = len(custom_select_checks)
                selected = list(vals[:n])
                ap_values = list(vals[n:2*n])
                line_values = list(vals[2*n:3*n])
                
                # 创建新的值列表，未选中的项目保持原值，选中的项目清空并隐藏
                new_checks = []
                new_aps = []
                new_lines = []
                new_visibility = []
                deleted_count = 0
                
                for i, (is_selected, ap_val, line_val) in enumerate(zip(selected, ap_values, line_values)):
                    if is_selected and custom_rows[i].visible:
                        # 选中的项目：清空并隐藏
                        new_checks.append(False)
                        new_aps.append("")
                        new_lines.append("")
                        new_visibility.append(gr.update(visible=False))
                        deleted_count += 1
                    else:
                        # 未选中的项目：保持原值
                        new_checks.append(False)  # 取消选中状态
                        new_aps.append(ap_val)
                        new_lines.append(line_val)
                        new_visibility.append(gr.update())
                
                status_msg = f"已删除 {deleted_count} 个项目" if deleted_count > 0 else "没有选中要删除的项目"
                return new_checks + new_aps + new_lines + new_visibility + [gr.update(value=status_msg)]
            
            def custom_select_all():
                """全选自定义项目"""
                return [True for _ in custom_rows]
            
            def custom_select_none():
                """全不选自定义项目"""
                return [False for _ in custom_rows]
            
            # 绑定按钮事件
            add_custom_btn.click(
                fn=add_custom_item,
                inputs=[],
                outputs=custom_rows + [custom_status]
            )
            
            delete_custom_btn.click(
                fn=delete_custom_items,
                inputs=custom_select_checks + custom_ap_texts + custom_line_texts,
                outputs=custom_select_checks + custom_ap_texts + custom_line_texts + custom_rows + [custom_status]
            )
            
            custom_select_all_btn.click(
                fn=custom_select_all,
                inputs=[],
                outputs=custom_select_checks
            )
            
            custom_select_none_btn.click(
                fn=custom_select_none,
                inputs=[],
                outputs=custom_select_checks
            )
            
            # 自定义台词生成功能
            def gen_custom_selected(character_id: int, llm_config_id: int, language: str, *vals):
                """生成选中的自定义台词"""
                if not character_id or not llm_config_id or not language:
                    return [gr.update(value="请先选择角色、LLM配置和语言")] + [gr.update() for _ in custom_line_texts]
                
                n = len(custom_select_checks)
                selected = list(vals[:n])
                ap_values = list(vals[n:2*n])
                current_lines = list(vals[2*n:3*n])
                
                # 找到选中且有动作参数的项目
                selected_items = []
                for i, (is_selected, ap_val) in enumerate(zip(selected, ap_values)):
                    if is_selected and custom_rows[i].visible and ap_val.strip():
                        selected_items.append((i, ap_val.strip()))
                
                if not selected_items:
                    return [gr.update(value="请选择至少一个有动作参数的项目")] + [gr.update() for _ in custom_line_texts]
                
                # 初始化生成器
                generator = DialogueGenerator()
                
                # 获取角色信息
                character = db.get_character(character_id)
                if not character:
                    return [gr.update(value="角色信息获取失败")] + [gr.update() for _ in custom_line_texts]
                
                # 获取LLM配置
                llm_cfg = db.get_llm_config(llm_config_id)
                if not llm_cfg:
                    return [gr.update(value="LLM配置获取失败")] + [gr.update() for _ in custom_line_texts]
                
                # 开始生成
                yield [gr.update(value=f"开始生成 {len(selected_items)} 个自定义台词...")] + [gr.update() for _ in custom_line_texts]
                
                for idx, ap_val in selected_items:
                    if stop_requested_flag[0]:
                        break
                    # 构建提示词
                    prompt_template = generator.create_comprehensive_prompt_template(
                        character_name=character[1],  # character name
                        character_description=character[2] if len(character) > 2 and character[2] else "角色描述",  # character description
                        language=language,
                        action_params=[ap_val],  # action parameters list
                        event_category=None
                    )
                    
                    # 更新状态
                    yield [gr.update(value=f"正在生成: {ap_val}")] + [gr.update() for _ in custom_line_texts]
                    
                    def status_cb(msg: str):
                        pass  # 不显示状态日志
                    
                    try:
                        result_text = generator.call_llm_api_with_status(
                            llm_cfg, prompt_template, status_callback=status_cb, max_retries=2
                        )
                    except Exception as e:
                        result_text = f"生成失败: {str(e)}"
                    
                    # 解析结果
                    parsed = _parse_json_flex(result_text) if result_text else None
                    line = _extract_line_for_param(parsed, ap_val) if parsed is not None else ""
                    if not line and isinstance(parsed, dict) and ap_val in parsed:
                        v = parsed[ap_val]
                        line = "" if v is None else str(v)
                    if not line and isinstance(parsed, str):
                        line = parsed
                    if not line:
                        line = "生成失败，请重试"
                    
                    # 更新对应行的台词
                    current_lines[idx] = line
                    
                    # 实时更新界面
                    yield [gr.update(value=f"已生成: {ap_val}")] + [gr.update(value=current_lines[i]) for i in range(len(custom_line_texts))]
                
                # 生成完成
                final_status = "所有选中项目生成完成" if not stop_requested_flag[0] else "生成已停止"
                yield [gr.update(value=final_status)] + [gr.update(value=current_lines[i]) for i in range(len(custom_line_texts))]
            
            # 绑定自定义台词生成按钮
            custom_gen_inputs = [character_dropdown, llm_config_dropdown, language_dropdown] + custom_select_checks + custom_ap_texts + custom_line_texts
            custom_gen_outputs = [custom_status] + custom_line_texts
            
            generate_custom_btn.click(
                fn=gen_custom_selected,
                inputs=custom_gen_inputs,
                outputs=custom_gen_outputs
            )

        # 顶部选择变化时更新按键可用性
        def update_button_states(character_id: int, llm_config_id: int, language: str):
            valid = bool(character_id) and bool(llm_config_id) and bool(language)
            if is_generating_flag[0]:
                return gr.update(interactive=False), gr.update(interactive=True)
            return gr.update(interactive=valid), gr.update(interactive=False)

        # 下拉刷新函数
        def refresh_characters(current_value):
            chars = db.get_characters()
            choices = [(c[1], c[0]) for c in chars]
            # 保留当前选择（若仍存在）
            values = [c[0] for c in chars]
            value = current_value if (current_value in values) else None
            return gr.update(choices=choices, value=value)

        def refresh_llm_configs(current_value):
            cfgs = db.get_llm_configs()
            choices = [(c[1], c[0]) for c in cfgs]
            values = [c[0] for c in cfgs]
            value = current_value if (current_value in values) else None
            return gr.update(choices=choices, value=value)

        refresh_char_btn.click(refresh_characters, inputs=[character_dropdown], outputs=[character_dropdown])
        refresh_llm_btn.click(refresh_llm_configs, inputs=[llm_config_dropdown], outputs=[llm_config_dropdown])

        # 角色图文信息更新
        def update_character_visuals(character_id: int):
            if not character_id:
                return gr.update(value=None), gr.update(value="")
            char = db.get_character(character_id)
            name = char[1]
            img_path = file_manager.get_character_original_avatar_path(name)
            desc_text = file_manager.get_character_description(name)
            if not isinstance(desc_text, str) or not desc_text.strip():
                desc_text = char[2] or ""
            desc_text = desc_text.replace("{{char}}", name).replace("{{user}}", "用户")
            img_val = img_path if (isinstance(img_path, str) and os.path.exists(img_path)) else None
            return gr.update(value=img_val), gr.update(value=desc_text)

        character_dropdown.change(
            fn=update_button_states,
            inputs=[character_dropdown, llm_config_dropdown, language_dropdown],
            outputs=[start_btn, stop_btn]
        )
        character_dropdown.change(
            fn=update_character_visuals,
            inputs=[character_dropdown],
            outputs=[char_image, char_desc_box]
        )
        llm_config_dropdown.change(update_button_states, [character_dropdown, llm_config_dropdown, language_dropdown], [start_btn, stop_btn])
        language_dropdown.change(update_button_states, [character_dropdown, llm_config_dropdown, language_dropdown], [start_btn, stop_btn])

        # 加载时刷新下拉与按键初始状态，并初始化角色显示
        def get_initial_state():
            characters = db.get_characters()
            configs = db.get_llm_configs()
            
            # 设置默认选择第一个角色
            first_character_id = characters[0][0] if characters else None
            
            # 获取第一个角色的图片和描述
            char_image_val = None
            char_desc_val = ""
            if first_character_id:
                char = db.get_character(first_character_id)
                name = char[1]
                img_path = file_manager.get_character_original_avatar_path(name)
                desc_text = file_manager.get_character_description(name)
                if not isinstance(desc_text, str) or not desc_text.strip():
                    desc_text = char[2] or ""
                desc_text = desc_text.replace("{{char}}", name).replace("{{user}}", "用户")
                char_image_val = img_path if (isinstance(img_path, str) and os.path.exists(img_path)) else None
                char_desc_val = desc_text
            
            return (
                gr.update(choices=[(c[1], c[0]) for c in characters], value=first_character_id),
                gr.update(choices=[(c[1], c[0]) for c in configs]),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(value=char_image_val),
                gr.update(value=char_desc_val),
            )

        dialogue_generation_interface.load(get_initial_state, None, [character_dropdown, llm_config_dropdown, start_btn, stop_btn, char_image, char_desc_box])

    return dialogue_generation_interface


def _load_rows_from_template_all() -> List[List]:
    rows: List[List] = []
    ap_idx = None
    tx_idx = None
    try:
        with open(TEMPLATE_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header_detected = False
            for i, row in enumerate(reader):
                if not row:
                    continue
                if not header_detected and ("动作参数" in row or "台词" in row):
                    header_detected = True
                    try:
                        ap_idx = row.index("动作参数")
                    except ValueError:
                        ap_idx = 1 if len(row) > 1 else 0
                    try:
                        tx_idx = row.index("台词")
                    except ValueError:
                        tx_idx = 2 if len(row) > 2 else None
                    continue
                if not header_detected and i == 0:
                    ap_idx = 1 if len(row) > 1 else 0
                    tx_idx = 2 if len(row) > 2 else None
                    continue
                ap = row[ap_idx] if ap_idx is not None and ap_idx < len(row) else ""
                tx = row[tx_idx] if (tx_idx is not None and tx_idx < len(row)) else ""
                if not ap:
                    continue
                rows.append([False, ap, tx or ""])
    except Exception:
        from action_parameters import ALL_ACTION_PARAMS
        for p in ALL_ACTION_PARAMS:
            rows.append([False, p, ""])
    return rows


def _parse_json_flex(text: str):
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end+1]
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start:end+1]
            try:
                return json.loads(candidate)
            except Exception:
                return None
        return None


def _extract_line_for_param(parsed, param: str) -> str:
    if isinstance(parsed, dict):
        if param in parsed and isinstance(parsed[param], (str, int, float)):
            v = parsed[param]
            return "" if v is None else str(v)
        items = parsed.get("dialogues") or parsed.get("items") or parsed.get("data")
        if isinstance(items, list):
            for it in items:
                ap = it.get("动作参数") or it.get("action") or it.get("param")
                if ap == param:
                    return it.get("台词") or it.get("text") or it.get("line") or ""
    return ""