# breathVOICE 工作流程备忘录

## 角色文件夹结构

```
Character/
├── <characterName>/                    # 角色根目录
│   ├── avatars/                       # 头像文件夹
│   │   ├── original.*                 # 原始头像文件
│   │   └── thumbnail_50x50.*          # 50x50px缩略图
│   ├── reference_sound/               # 参考声音文件夹
│   │   └── reference.*                # 角色参考声音文件
│   ├── description/                   # 角色描述文件夹
│   │   └── character_info.txt         # 角色描述文本文件
│   ├── script/                        # 脚本文件夹
│   │   └── dialogue_<timestamp>.csv   # 生成的台词CSV文件
│   └── <characterName>_Voices/        # 语音文件夹
│       ├── greeting/                  # 开机问候音频文件
│       ├── impact/                    # 突然插入或换体位音频文件
│       ├── orgasm/                    # 高潮音频文件
│       ├── reaction/                  # 兴奋反应音频文件
│       ├── tease/                     # 挑逗音频文件
│       └── touch/                     # 身体触碰音频文件
```

## 工作流程详细说明

### Step 1: 角色管理 (Character Management)

**功能描述**: 创建和管理角色基础信息

**输入 (Input)**:
- 角色名称 (Character Name) - 文本输入
- 角色描述 (Character Description) - 文本输入
- 头像图片 (Avatar Image) - 图片文件上传
- 参考声音 (Reference Sound) - 音频文件上传 (可选)

**处理过程**:
1. 创建角色目录结构
2. 保存原始头像并生成50x50px缩略图
3. 保存角色描述到文本文件
4. 保存参考声音文件 (如果提供)
5. 在数据库中创建角色记录

**输出 (Output)**:
- 角色目录: `Character/<characterName>/`
- 头像文件: `avatars/original.*` 和 `avatars/thumbnail_50x50.*`
- 描述文件: `description/character_info.txt`
- 参考声音: `reference_sound/reference.*` (如果提供)
- 数据库记录: characters表中的角色信息

**存储位置**:
- 文件系统: `Character/<characterName>/`
- 数据库: `characters` 表

---

### Step 2: LLM配置 (LLM Configuration)

**功能描述**: 为角色配置大语言模型参数

**输入 (Input)**:
- 选择已创建的角色 (Character Selection)
- 配置名称 (Config Name) - 文本输入
- 模型选择 (Model Selection) - 下拉选择
- 温度参数 (Temperature) - 数值输入 (0.0-2.0)
- 最大令牌数 (Max Tokens) - 数值输入
- 提示词模板 (Prompt Template) - 文本输入

**处理过程**:
1. 验证角色存在性
2. 保存LLM配置参数到数据库
3. 关联配置到指定角色

**输出 (Output)**:
- 数据库记录: llm_configs表中的配置信息
- 配置与角色的关联关系

**存储位置**:
- 数据库: `llm_configs` 表

---

### Step 3: 脚本生成 (Script Generation)

**功能描述**: 使用LLM生成角色台词脚本

**输入 (Input)**:
- 选择角色 (Character Selection)
- 选择LLM配置 (LLM Config Selection)
- 语言选择 (Language Selection) - 中文/英文等
- 台词模板 (Script Template) - CSV模板文件
- 动作参数 (Action Parameters) - 从action_parameters.py

**处理过程**:
1. 读取角色描述和LLM配置
2. 根据台词模板和动作参数生成提示词
3. 调用LLM API生成台词内容
4. 将生成的台词保存为CSV文件
5. 按台词类型分类保存

**输出 (Output)**:
- 台词CSV文件: `script/dialogue_<language>_<date>_<time>.csv`（示例：`dialogue_zh_20251018_025600.csv`）
- 语言编码: 中文→`zh`，English→`en`，日本語→`ja`
- 目前不按类型拆分导出，统一保存为一份脚本CSV
- 数据库记录: `scripts` 表（包含 `language` 字段，默认 `zh`）

**存储位置**:
- 文件系统: `Character/<characterName>/script/`
- 数据库: `scripts` 表

---

### Step 4: 语音生成 (Voice Generation)

**功能描述**: 将台词文本转换为语音文件

**输入 (Input)**:
- 选择角色 (Character Selection)
- 选择台词脚本文件 (Script File Selection)
- 语音生成参数 (Voice Parameters):
  - 语音模型选择
  - 语速设置
  - 音调设置
  - 情感参数
- 参考声音文件 (Reference Sound) - 可选

**处理过程**:
1. 读取台词CSV文件
2. 按台词类型分组处理
3. 调用语音合成API生成音频
4. 按类型保存到对应文件夹
5. 生成音频文件元数据

**输出 (Output)**:
- 语音文件按类型分类保存:
  - `<characterName>_Voices/greeting/*.wav`
  - `<characterName>_Voices/impact/*.wav`
  - `<characterName>_Voices/orgasm/*.wav`
  - `<characterName>_Voices/reaction/*.wav`
  - `<characterName>_Voices/tease/*.wav`
  - `<characterName>_Voices/touch/*.wav`

**存储位置**:
- 文件系统: `Character/<characterName>/<characterName>_Voices/`

---

### Step 5: 语音包导出 (Voice Pack Export)

**功能描述**: 将角色的所有文件打包导出

**输入 (Input)**:
- 选择角色 (Character Selection)
- 导出选项 (Export Options):
  - 包含头像
  - 包含描述
  - 包含脚本
  - 包含语音文件
  - 包含参考声音

**处理过程**:
1. 收集角色的所有相关文件
2. 创建导出清单
3. 压缩打包所有文件
4. 生成语音包元数据文件

**输出 (Output)**:
- 语音包文件: `voice_packs/<characterName>_voice_pack_<timestamp>.zip`
- 包含内容:
  - 角色信息文件
  - 头像文件
  - 台词脚本文件
  - 语音音频文件
  - 参考声音文件 (如果有)
  - 元数据文件

**存储位置**:
- 文件系统: `voice_packs/`

## 数据库表结构

### characters 表
```sql
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    avatar_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### llm_configs 表
```sql
CREATE TABLE llm_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER,
    config_name TEXT NOT NULL,
    model TEXT NOT NULL,
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    prompt_template TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
);
```

### scripts 表
```sql
CREATE TABLE scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER,
    llm_config_id INTEGER,
    file_path TEXT NOT NULL,
    language TEXT DEFAULT 'zh',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
    FOREIGN KEY (llm_config_id) REFERENCES llm_configs (id) ON DELETE CASCADE
);
```

## 文件命名规范

### 头像文件
- 原始文件: `original.{ext}` (保持原始扩展名)
- 缩略图: `thumbnail_50x50.{ext}`

### 脚本文件
- 主脚本: `dialogue_<language>_<date>_<time>.csv`
  - 示例：`dialogue_zh_20251018_025600.csv`
  - 语言编码：中文→`zh`，English→`en`，日本語→`ja`
- 分类脚本: 暂未按类型拆分导出
- 日期格式: `YYYYMMDD`；时间格式: `HHMMSS`

### 语音文件
- 格式: `{action_type}_{index}.wav`
- 编码: WAV格式，16bit，44.1kHz

### 参考声音文件
- 格式: `reference.{ext}` (保持原始扩展名)

## 注意事项

1. **文件夹权限**: 确保Character目录有读写权限
2. **文件大小限制**: 
   - 头像文件建议不超过10MB
   - 参考声音文件建议不超过50MB
3. **字符编码**: 所有文本文件使用UTF-8编码
4. **备份策略**: 重要操作前自动创建备份
5. **错误处理**: 每个步骤都有相应的错误处理和回滚机制