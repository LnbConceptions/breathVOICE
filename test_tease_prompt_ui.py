import gradio as gr
import json
import csv
from typing import List, Tuple, Optional, Union

from database import CharacterDatabase
from dialogue_generator import DialogueGenerator
from action_parameters import ALL_ACTION_PARAMS

TEMPLATE_CSV_PATH = "/Users/Saga/breathVOICE/台词模版.csv"


def _get_characters(db: CharacterDatabase) -> List[Tuple[str, str]]:
    characters = db.get_characters()
    if not characters:
        return []
    return [(c[1], str(c[0])) for c in characters]


def _get_llm_configs(db: CharacterDatabase) -> List[Tuple[str, str]]:
    configs = db.get_llm_configs()
    if not configs:
        return []
    return [(cfg[1], str(cfg[0])) for cfg in configs]


def _parse_json_flex(text: str) -> Optional[Union[dict, list]]:
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


def _load_tease_rows_from_template() -> List[List]:
    rows: List[List] = []
    ap_idx = None
    tx_idx = None
    # Robust CSV parsing for format like: FALSE,动作参数,台词 + many lines
    try:
        with open(TEMPLATE_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header_detected = False
            for i, row in enumerate(reader):
                if not row:
                    continue
                # Detect header
                if not header_detected and ("动作参数" in row or "台词" in row):
                    header_detected = True
                    # Try to locate indices
                    try:
                        ap_idx = row.index("动作参数")
                    except ValueError:
                        ap_idx = 1 if len(row) > 1 else 0
                    try:
                        tx_idx = row.index("台词")
                    except ValueError:
                        tx_idx = 2 if len(row) > 2 else None
                    continue
                # If header not detected, assume template has first row like FALSE,动作参数,台词
                if not header_detected and i == 0:
                    # Attempt to infer positions
                    ap_idx = 1 if len(row) > 1 else 0
                    tx_idx = 2 if len(row) > 2 else None
                    # Skip this inferred header row
                    continue
                # Extract columns
                ap = row[ap_idx] if ap_idx is not None and ap_idx < len(row) else ""
                tx = row[tx_idx] if (tx_idx is not None and tx_idx < len(row)) else ""
                if not ap:
                    continue
                # Filter to tease only
                if "tease" not in ap:
                    continue
                # Initialize: 选择=False, 动作参数=ap(只读), 台词="" (或保留原值)
                rows.append([False, ap, tx or ""])
    except Exception:
        # Fallback to ALL_ACTION_PARAMS tease subset if CSV missing
        for p in [p for p in ALL_ACTION_PARAMS if "tease" in p]:
            rows.append([False, p, ""])
    return rows


def build_ui():
    db = CharacterDatabase()
    db.initialize_database()
    generator = DialogueGenerator()

    default_language = "中文"

    with gr.Blocks(title="Tease台词提示词测试", theme=gr.themes.Default()) as demo:
        gr.Markdown("## Tease台词提示词测试\n- 只读的‘动作参数’与可编辑‘台词’，左侧复选框用于选择需要重生成的条目。\n- 支持逐条生成并实时更新表格，提示词预览显示当前生成条目的最终JSON提示词。")

        character_dd = gr.Dropdown(label="选择角色", choices=[c[0] for c in _get_characters(db)], value=None)
        llm_dd = gr.Dropdown(label="选择LLM配置", choices=[c[0] for c in _get_llm_configs(db)], value=None)
        language_dd = gr.Dropdown(label="语言", choices=["中文", "English", "日本語"], value=default_language)

        with gr.Row():
            load_btn = gr.Button("加载tease模版", variant="primary", visible=False)
            select_all_btn = gr.Button("全选", visible=False)
            select_none_btn = gr.Button("全不选", visible=False)
        with gr.Row():
            build_btn = gr.Button("构建综合提示词（预览）", visible=False)
            gen_selected_btn = gr.Button("生成选中台词（逐条实时报更）", variant="secondary", visible=False)

        prompt_state = gr.State(None)
        base_rows_state = gr.State([])  # 保留只读动作参数基线

        prompt_preview = gr.Textbox(label="提示词预览（最终注入LLM的JSON）", lines=16)
        status_box = gr.Textbox(label="LLM状态日志", lines=12)

        # 辅助函数：根据下拉菜单标签解析ID（角色/LLM配置）
        def _resolve_character_id(label: str) -> Optional[int]:
            if not label:
                return None
            for name, cid in _get_characters(db):
                if name == label or str(cid) == label:
                    return int(cid)
            return None

        def _resolve_llm_config_id(label: str) -> Optional[int]:
            if not label:
                return None
            for name, lid in _get_llm_configs(db):
                if name == label or str(lid) == label:
                    return int(lid)
            return None

        # 兼容旧表：统一将 DataFrame 或其它结构转换为 list-of-lists
        def _to_rows(table):
            if table is None:
                return []
            if hasattr(table, "values"):
                try:
                    return table.values.tolist()
                except Exception:
                    pass
            if isinstance(table, list):
                return table
            return []

        # 选择 + 只读动作参数 + 可编辑台词（旧：Dataframe，不再推荐使用）
        result_table = gr.Dataframe(
            headers=["选择", "动作参数", "台词"],
            datatype=["bool", "str", "str"],
            interactive=True,
            type="array",
            row_count=10,
            col_count=3,
            visible=False,
        )

        # 新版交互式编辑UI（每行：复选框 + 只读动作参数 + 可编辑台词）
        with gr.Tab("编辑版"):
            gr.Markdown("### 编辑表\n- 每行包含：选择复选框 + 只读动作参数 + 可编辑台词\n- 支持全选/全不选、综合提示词预览、逐条调用LLM并实时更新对应行台词")
            rows_init = _load_tease_rows_from_template()
            select_checks2: List[gr.Checkbox] = []
            ap_texts2: List[gr.Textbox] = []
            line_texts2: List[gr.Textbox] = []
            with gr.Column():
                for sel, ap, tx in rows_init:
                    with gr.Row():
                        chk = gr.Checkbox(label="", value=False, scale=0, min_width=32, show_label=False)
                        ap_tb = gr.Textbox(label="", value=ap, interactive=False, scale=3, show_label=False)
                        line_tb = gr.Textbox(label="", value=tx or "", interactive=True, scale=9, show_label=False)
                    select_checks2.append(chk)
                    ap_texts2.append(ap_tb)
                    line_texts2.append(line_tb)

            with gr.Row():
                select_all_btn2 = gr.Button("全选")
                select_none_btn2 = gr.Button("全不选")
                build_btn2 = gr.Button("构建综合提示词（预览）")
                gen_selected_btn2 = gr.Button("生成选中台词（逐条实时报更）", variant="secondary")

            def select_all_v2():
                return [True] * len(select_checks2)

            def select_none_v2():
                return [False] * len(select_checks2)

            select_all_btn2.click(fn=select_all_v2, inputs=[], outputs=select_checks2)
            select_none_btn2.click(fn=select_none_v2, inputs=[], outputs=select_checks2)

            def on_build_prompt_v2(character_label: str, llm_label: str, language: str, *aps):
                char_id = _resolve_character_id(character_label)
                llm_id = _resolve_llm_config_id(llm_label)
                if not char_id or not llm_id:
                    return gr.update(value="请先选择有效的角色与LLM配置"), None
                char = db.get_character(char_id)
                if not char:
                    return gr.update(value="角色读取失败"), None
                character_name = char[1]
                character_description = char[2] or ""
                action_params = [a for a in aps if isinstance(a, str) and a]
                if not action_params:
                    action_params = [p for p in ALL_ACTION_PARAMS if p.startswith("tease")]
                prompt = generator.create_comprehensive_prompt_template(
                    character_name=character_name,
                    character_description=character_description,
                    language=language,
                    action_params=action_params,
                    event_category="tease",
                )
                prompt_text = json.dumps(prompt, ensure_ascii=False, indent=2)
                return prompt_text, prompt

            build_inputs = [character_dd, llm_dd, language_dd] + ap_texts2
            build_btn2.click(
                fn=on_build_prompt_v2,
                inputs=build_inputs,
                outputs=[prompt_preview, prompt_state],
            )

            def gen_selected_v2(character_label: str, llm_label: str, language: str, *vals):
                n = len(select_checks2)
                sel_vals = list(vals[:n])
                aps = list(vals[n:2*n])
                lines_in = list(vals[2*n:3*n])
                char_id = _resolve_character_id(character_label)
                llm_id = _resolve_llm_config_id(llm_label)
                if not char_id or not llm_id:
                    yield "请先选择有效的角色与LLM配置", gr.update(value=""), *lines_in
                    return
                char = db.get_character(char_id)
                character_name = char[1]
                character_description = char[2] or ""
                llm_cfg = db.get_llm_config(llm_id)
                indices = [i for i in range(n) if bool(sel_vals[i])]
                if not indices:
                    indices = list(range(n))
                current_lines = [l if isinstance(l, str) else "" for l in lines_in]

                for idx in indices:
                    param = aps[idx]
                    if not isinstance(param, str) or not param:
                        continue
                    prompt = generator.create_comprehensive_prompt_template(
                        character_name=character_name,
                        character_description=character_description,
                        language=language,
                        action_params=[param],
                        event_category="tease",
                    )
                    prompt_text = json.dumps(prompt, ensure_ascii=False, indent=2)
                    status_lines: List[str] = []
                    def status_cb(msg: str):
                        status_lines.append(msg)
                    try:
                        result_text = generator.call_llm_api_with_status(
                            llm_cfg, prompt, status_callback=status_cb, max_retries=2
                        )
                    except Exception as e:
                        result_text = ""
                        status_lines.append(f"异常: {e}")
                    status_text = "\n".join(status_lines)
                    parsed = _parse_json_flex(result_text) if result_text else None
                    line = _extract_line_for_param(parsed, param) if parsed is not None else ""
                    if not line and isinstance(parsed, dict) and param in parsed:
                        v = parsed[param]
                        line = "" if v is None else str(v)
                    if not line and isinstance(parsed, str):
                        line = parsed
                    current_lines[idx] = line
                    yield status_text, gr.update(value=prompt_text), *current_lines

            gen_inputs = [character_dd, llm_dd, language_dd] + select_checks2 + ap_texts2 + line_texts2
            gen_outputs = [status_box, prompt_preview] + line_texts2
            gen_selected_btn2.click(
                fn=gen_selected_v2,
                inputs=gen_inputs,
                outputs=gen_outputs,
            )

        def _extract_line_for_param(parsed: Union[dict, list], param: str) -> str:
            if isinstance(parsed, dict):
                # direct mapping
                if param in parsed and isinstance(parsed[param], (str, int, float)):
                    v = parsed[param]
                    return "" if v is None else str(v)
                # dialogues list
                items = parsed.get("dialogues") or parsed.get("items") or parsed.get("data")
                if isinstance(items, list):
                    for it in items:
                        ap = it.get("动作参数") or it.get("action") or it.get("param")
                        if ap == param:
                            return it.get("台词") or it.get("text") or it.get("line") or ""
            return ""

        def gen_selected(character_label: str, llm_label: str, language: str, table: List[List]):
            char_id = _resolve_character_id(character_label)
            llm_id = _resolve_llm_config_id(llm_label)
            if not char_id or not llm_id:
                yield "请先选择有效的角色与LLM配置", gr.update(value=""), gr.update(value=_to_rows(table))
                return
            char = db.get_character(char_id)
            character_name = char[1]
            character_description = char[2] or ""
            llm_cfg = db.get_llm_config(llm_id)

            rows = _to_rows(table)
            working_table = [r[:] if isinstance(r, list) else [False, "", ""] for r in rows]
            indices = [i for i, r in enumerate(working_table) if isinstance(r, list) and len(r) >= 1 and bool(r[0])]
            if not indices:
                indices = list(range(len(working_table)))

            for idx in indices:
                param = working_table[idx][1] if len(working_table[idx]) >= 2 else ""
                if not param:
                    continue
                prompt = generator.create_comprehensive_prompt_template(
                    character_name=character_name,
                    character_description=character_description,
                    language=language,
                    action_params=[param],
                    event_category="tease",
                )
                prompt_text = json.dumps(prompt, ensure_ascii=False, indent=2)

                status_lines: List[str] = []
                def status_cb(msg: str):
                    status_lines.append(msg)
                try:
                    result_text = generator.call_llm_api_with_status(llm_cfg, prompt, status_callback=status_cb, max_retries=2)
                except Exception as e:
                    result_text = ""
                    status_lines.append(f"异常: {e}")
                status_text = "\n".join(status_lines)

                parsed = _parse_json_flex(result_text) if result_text else None
                line = _extract_line_for_param(parsed, param) if parsed is not None else ""
                if not line and isinstance(parsed, dict) and param in parsed:
                    v = parsed[param]
                    line = "" if v is None else str(v)
                if not line and isinstance(parsed, str):
                    line = parsed

                while len(working_table[idx]) < 3:
                    working_table[idx].append("")
                working_table[idx][2] = line

                yield status_text, gr.update(value=prompt_text), gr.update(value=working_table)

        gen_selected_btn.click(
            fn=gen_selected,
            inputs=[character_dd, llm_dd, language_dd, result_table],
            outputs=[status_box, prompt_preview, result_table],
        )

        demo.launch(server_name="127.0.0.1", server_port=7867, share=False, max_threads=10)

    return demo


if __name__ == "__main__":
    build_ui()