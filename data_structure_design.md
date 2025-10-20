# breathVOICE 数据结构设计

## 工作流程输入输出分析

### Step 1: 角色管理
- **输入**: 角色名称、角色描述、头像图片、参考声音文件
- **输出**: 角色基础信息存储到数据库，文件存储到角色专属目录
- **存储结构**: 
  - 数据库: characters表 (id, name, description, avatar_path, created_at, updated_at)
  - 文件系统: Character/<角色名>/avatars/, reference_sound/, description/

### Step 2: LLM配置
- **输入**: 角色ID、LLM配置参数（模型、温度、提示词等）
- **输出**: LLM配置存储到数据库
- **存储结构**: 
  - 数据库: llm_configs表 (id, character_id, config_name, model, temperature, prompt_template, created_at)

### Step 3: 脚本生成
- **输入**: 角色ID、LLM配置ID、语言选择、台词模板
- **输出**: 生成的台词CSV文件
- **存储结构**: 
  - 文件系统: Character/<角色名>/script/<生成时间戳>.csv
  - 数据库: scripts表 (id, character_id, llm_config_id, file_path, language, created_at)

### Step 4: 语音生成
- **输入**: 角色脚本文件、语音生成参数
- **输出**: 分类别的音频文件
- **存储结构**: 
  - 文件系统: Character/<角色名>/<角色名>_Voices/greeting|impact|orgasm|reaction|tease|touch/

### Step 5: 语音包导出
- **输入**: 角色完整数据
- **输出**: 打包的语音包文件
- **存储结构**: voice_packs/目录

## 目录结构设计

```
Character/
├── <characterName>/
│   ├── avatars/           # 头像和50x50px缩略图
│   ├── reference_sound/   # 角色参考声音
│   ├── description/       # 角色描述文本文件
│   ├── script/           # Step3生成的所有CSV文件
│   └── <characterName>_Voices/  # Step4生成的音频文件
       ├── greeting/        # 角色开机问候音频文件
       ├── impact/          # 突然插入或换体位的音频文件
       ├── orgasm/         # 角色高潮音频文件
       ├── reaction/        # 角色兴奋音频文件
       ├── tease/           # 角色挑逗音频文件
       └── touch/           # 身体触碰音频文件
```

## 数据库重新设计

### characters表
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

### llm_configs表
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

### scripts表
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