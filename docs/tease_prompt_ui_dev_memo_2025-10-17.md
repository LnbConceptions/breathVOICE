# Tease台词提示词测试开发备忘录（2025-10-17）

## 概述
记录本次针对测试页面与提示词生成逻辑的改动、验证方式与后续建议，便于追踪语言合规与UI可用性优化。

## 关键改动
- 下拉标签精简：测试页“选择LLM配置”仅显示配置名称，移除 URL 与 API Key，降低敏感信息曝光并提升可读性。
- 语言合规强化：
  - 系统消息与用户消息新增严格语言规则：输出必须为目标语言；禁止混用其他语言；日语禁止罗马字（romaji）。
  - 模板输出格式增加“禁止非目标语言字符/翻译”约束。
- Python 3.9 兼容修复：将 `dict | list` 等类型注解改为 `Union[dict, list]`，修复 `TypeError`，确保测试页面可启动。

## 受影响文件
- `test_tease_prompt_ui.py`
  - `_get_llm_configs` 标签简化：
    ```python
    # 旧：
    return [(f"{cfg[1]} | {cfg[2]} | {cfg[3]}", str(cfg[0])) for cfg in configs]
    # 新：
    return [(cfg[1], str(cfg[0])) for cfg in configs]
    ```
  - 类型注解兼容修复（示例）：
    ```python
    from typing import Union
    def _parse_json_flex(text: str) -> Optional[Union[dict, list]]:
        ...
    ```
- `dialogue_generator.py`
  - 系统与用户消息：新增“严格语言规则”（仅目标语言、禁止混用、禁止翻译/罗马字）。
  - 输出格式：补充“禁止非目标语言词/字符/翻译”的约束。

## 启动与预览
- 测试页地址：`http://127.0.0.1:7867/`
- 主应用地址（如已运行）：`http://127.0.0.1:7865/`
- 预览心跳偶发报错（`heartbeat`）不影响主功能；`urllib3` 的 `NotOpenSSLWarning` 为环境提示，可忽略。

## 日语输出验证要点
- 选择 `tease` 类动作参数（示例：`P0_B1_tease_1`）。
- 检查返回 JSON 值：
  - 仅包含日语（かな/漢字）；无英语、中文或罗马字。
  - 二人称统一使用“あなた”。
  - 返回仅为合法 JSON 对象，不夹带额外文本或代码块标记。

## 已知问题/注意事项
- 若仍出现语言混用，可进一步：
  - 增加字符集校验（仅允许日文字符集），失败则自动重试。
  - 在模板中明确脚本要求（如日语必须使用平假名/片假名及汉字）。

## 后续建议
- 主应用下拉也可统一为仅显示名称（可选显示 `name (model)`），继续避免 URL/API Key 暴露。
- 为提示词生成增加自动复核与重试策略，提升合规稳定性。

## 操作指引（测试页）
1. 终止占用端口：`lsof -ti:7867 | xargs kill -9 || true`
2. 启动测试页：`python /Users/Saga/breathVOICE/test_tease_prompt_ui.py`
3. 打开 `http://127.0.0.1:7867/`，进行日语输出验证（见上文要点）。

—— 完 ——