# BreathVOICE API 文档

## 概述

BreathVOICE API 是 IndexTTS 项目的定制化扩展，专为 breathVOICE 应用程序设计。该API在不影响标准OpenAI兼容API的基础上，提供了角色组管理、批量TTS生成等专用功能。

## 基础信息

- **API基础URL**: `https://tts.ioioioioio.com:1120`
- **API前缀**: `/breathvoice`
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 核心概念

### VoiceGroupID (角色组ID)
- 角色组是一组相关的参考音频文件的集合
- 每个角色组包含4个特定的音频文件，用于不同情绪场景
- VoiceGroupID 是角色组的唯一标识符（角色名称）

### 参考音频文件结构
每个角色组必须包含以下4个音频文件：
- `<characterName>_greeting.wav` - 问候音频
- `<characterName>_B1_B2.wav` - B1/B2情绪音频  
- `<characterName>_B3_B4.wav` - B3/B4/冲击情绪音频
- `<characterName>_B5_orgasm.wav` - B5/高潮情绪音频

### 文件名映射规则
根据目标文件名中的关键词自动选择参考音频：
- 包含 "greeting" → 使用 `_greeting.wav`
- 包含 "B1" 或 "B2" → 使用 `_B1_B2.wav`
- 包含 "B0", "B3", "B4", "impact" → 使用 `_B3_B4.wav`
- 包含 "B5" 或 "orgasm" → 使用 `_B5_orgasm.wav`

## API 端点

### 1. 健康检查

检查 BreathVOICE API 服务状态。

**请求**
```http
GET /breathvoice/health
```

**响应**
```json
{
  "status": "healthy",
  "service": "breathvoice",
  "version": "1.0.0",
  "available_voice_groups": 1
}
```

**字段说明**
- `status` (string): 服务状态，"healthy" 表示正常
- `service` (string): 服务名称
- `version` (string): API版本号
- `available_voice_groups` (integer): 可用角色组数量

### 2. 获取角色组列表

获取所有可用的角色组列表。

**请求**
```http
GET /breathvoice/voice-groups
```

**响应**
```json
{
  "success": true,
  "voice_groups": ["ChineseWoman", "EnglishGirl", "JapaneseMan"],
  "count": 3
}
```

**错误响应**
```json
{
  "success": false,
  "error": "Failed to scan voice groups directory"
}
```

### 4. 获取角色组详细信息

获取特定角色组的详细信息，包括所有音频文件列表。

**请求**
```http
GET /breathvoice/voice-groups/{voice_group_id}
```

**参数**
- `voice_group_id` (string): 角色组ID（角色名称）

**响应**
```json
{
  "success": true,
  "voice_group_info": {
    "voice_group_id": "ChineseWoman",
    "reference_dir": "C:\\Users\\cnbjs\\IndexTTS\\index-tts\\examples\\ChineseWoman_Reference",
    "audio_files": {
      "greeting": {
        "filename": "ChineseWoman_greeting.wav",
        "path": "C:\\Users\\cnbjs\\IndexTTS\\index-tts\\examples\\ChineseWoman_Reference\\ChineseWoman_greeting.wav",
        "exists": true,
        "size": 560956
      },
      "B1_B2": {
        "filename": "ChineseWoman_B1_B2.wav",
        "path": "C:\\Users\\cnbjs\\IndexTTS\\index-tts\\examples\\ChineseWoman_Reference\\ChineseWoman_B1_B2.wav",
        "exists": true,
        "size": 584954
      },
      "B3_B4": {
        "filename": "ChineseWoman_B3_B4.wav",
        "path": "C:\\Users\\cnbjs\\IndexTTS\\index-tts\\examples\\ChineseWoman_Reference\\ChineseWoman_B3_B4.wav",
        "exists": true,
        "size": 488954
      },
      "B5_orgasm": {
        "filename": "ChineseWoman_B5_orgasm.wav",
        "path": "C:\\Users\\cnbjs\\IndexTTS\\index-tts\\examples\\ChineseWoman_Reference\\ChineseWoman_B5_orgasm.wav",
        "exists": true,
        "size": 440954
      }
    }
  }
}
```

**错误响应**
```json
{
  "success": false,
  "error": "Voice group 'InvalidName' not found"
}
```

### 4. 上传角色组

上传ZIP文件创建新的角色组。

**请求**
```http
POST /breathvoice/upload-voice-group
Content-Type: multipart/form-data
```

**参数**
- `file` (file): ZIP文件，包含角色组音频文件
- `overwrite` (boolean, 可选): 是否覆盖已存在的角色组，默认false

**ZIP文件要求**
- 必须包含4个音频文件
- 文件命名格式：`<characterName>_<category>.wav`
- 支持的category：`greeting`, `B1_B2`, `B3_B4`, `B5_orgasm`

**响应**
```json
{
  "success": true,
  "message": "Voice group 'NewCharacter' uploaded successfully",
  "voice_group_id": "NewCharacter",
  "files_extracted": 4,
  "reference_dir": "examples/NewCharacter_Reference"
}
```

**错误响应**
```json
{
  "success": false,
  "error": "Voice group 'ExistingName' already exists. Use overwrite=true to replace."
}
```

### 5. 单条TTS生成

生成单个TTS音频文件，支持逐条生成工作流。

**请求**
```http
POST /breathvoice/single-tts
Content-Type: application/json
```

**请求体**
```json
{
  "text": "你好，欢迎来到我们的世界！",
  "filename": "greeting_001.wav",
  "voice_group_id": "ChineseWoman"
}
```

**参数说明**
- `text` (string): 要转换的文本
- `filename` (string): 输出音频文件名
- `voice_group_id` (string): 要使用的角色组ID

**响应**
```json
{
  "success": true,
  "message": "Single TTS completed successfully",
  "result": {
    "filename": "greeting_001.wav",
    "text": "你好，欢迎来到我们的世界！",
    "reference_audio": "ChineseWoman_greeting.wav",
    "output_path": "examples/greeting_001.wav",
    "status": "success",
    "processing_time": 2.34
  }
}
```

**错误响应**
```json
{
  "success": false,
  "error": "Voice group 'InvalidName' not found",
  "result": {
    "filename": "greeting_001.wav",
    "text": "你好，欢迎来到我们的世界！",
    "status": "failed",
    "error": "Voice group not found"
  }
}
```

### 6. 批量TTS生成

批量生成多个TTS音频文件。

**请求**
```http
POST /breathvoice/batch-tts
Content-Type: application/json
```

**请求体**
```json
{
  "requests": [
    {
      "text": "你好，欢迎来到我们的世界！",
      "filename": "greeting_001.wav",
      "voice_group_id": "ChineseWoman"
    },
    {
      "text": "这真是太令人兴奋了！",
      "filename": "B1_start_004.wav",
      "voice_group_id": "ChineseWoman"
    },
    {
      "text": "哇，这种感觉真是难以置信！",
      "filename": "B3_reaction_002.wav",
      "voice_group_id": "ChineseWoman"
    },
    {
      "text": "啊...这就是最高的境界！",
      "filename": "B5_climax_003.wav",
      "voice_group_id": "ChineseWoman"
    }
  ]
}
```

**参数说明**
- `requests` (array): TTS请求列表
  - `text` (string): 要转换的文本
  - `filename` (string): 输出音频文件名
  - `voice_group_id` (string): 要使用的角色组ID

**响应**
```json
{
  "success": true,
  "message": "Batch TTS completed successfully",
  "results": [
    {
      "filename": "greeting_001.wav",
      "text": "你好，欢迎来到我们的世界！",
      "reference_audio": "ChineseWoman_greeting.wav",
      "output_path": "examples/greeting_001.wav",
      "status": "success",
      "processing_time": 2.34
    },
    {
      "filename": "B1_start_004.wav", 
      "text": "这真是太令人兴奋了！",
      "reference_audio": "ChineseWoman_B1_B2.wav",
      "output_path": "examples/B1_start_004.wav",
      "status": "success",
      "processing_time": 1.89
    },
    {
      "filename": "B3_reaction_002.wav",
      "text": "哇，这种感觉真是难以置信！", 
      "reference_audio": "ChineseWoman_B3_B4.wav",
      "output_path": "examples/B3_reaction_002.wav",
      "status": "success",
      "processing_time": 2.12
    },
    {
      "filename": "B5_climax_003.wav",
      "text": "啊...这就是最高的境界！",
      "reference_audio": "ChineseWoman_B5_orgasm.wav", 
      "output_path": "examples/B5_climax_003.wav",
      "status": "success",
      "processing_time": 2.67
    }
  ],
  "total_requests": 4,
  "successful": 4,
  "failed": 0,
  "total_processing_time": 9.02
}
```

**错误响应**
```json
{
  "success": false,
  "error": "Voice group 'InvalidGroup' not found"
}
```

## 使用示例

### Python 示例

```python
import requests
import json

BASE_URL = "https://tts.ioioioioio.com:1120"

# 1. 获取角色组列表
response = requests.get(f"{BASE_URL}/breathvoice/voice-groups")
print("角色组列表:", response.json())

# 2. 检查服务健康状态
response = requests.get(f"{BASE_URL}/breathvoice/health")
print("服务状态:", response.json())

# 3. 获取特定角色组信息
voice_group_id = "ChineseWoman"
response = requests.get(f"{BASE_URL}/breathvoice/voice-groups/{voice_group_id}")
print("角色组详情:", response.json())

# 5. 上传新角色组
with open("new_character.zip", "rb") as f:
    files = {"file": f}
    data = {"overwrite": "false"}
    response = requests.post(
        f"{BASE_URL}/breathvoice/upload-voice-group",
        files=files,
        data=data
    )
print("上传结果:", response.json())

# 5. 批量TTS生成
batch_data = {
    "requests": [
        {
            "text": "你好世界",
            "filename": "greeting_001.wav",
            "voice_group_id": "ChineseWoman"
        },
        {
            "text": "太棒了！",
            "filename": "B1_excitement_002.wav",
            "voice_group_id": "ChineseWoman"
        }
    ]
}

response = requests.post(
    f"{BASE_URL}/breathvoice/batch-tts",
    json=batch_data,
    headers={"Content-Type": "application/json"}
)
print("批量TTS结果:", response.json())
```

### JavaScript 示例

```javascript
const BASE_URL = 'https://tts.ioioioioio.com:1120';

// 1. 获取角色组列表
async function getVoiceGroups() {
    const response = await fetch(`${BASE_URL}/breathvoice/voice-groups`);
    const data = await response.json();
    console.log('角色组列表:', data);
    return data;
}

// 2. 批量TTS生成
async function batchTTS(requests) {
    const response = await fetch(`${BASE_URL}/breathvoice/batch-tts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            requests: requests
        })
    });
    
    const result = await response.json();
    console.log('批量TTS结果:', result);
    return result;
}

// 使用示例
getVoiceGroups().then(groups => {
    if (groups.success && groups.voice_groups.length > 0) {
        const voiceGroupId = groups.voice_groups[0];
        const requests = [
            { 
                text: "欢迎使用BreathVOICE", 
                filename: "greeting_welcome.wav",
                voice_group_id: voiceGroupId
            },
            { 
                text: "这真是太棒了！", 
                filename: "B1_amazing.wav",
                voice_group_id: voiceGroupId
            }
        ];
        
        batchTTS(requests);
    }
});
```

### cURL 示例

```bash
# 1. 获取角色组列表
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups"

# 2. 检查服务健康状态
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/health"

# 3. 获取角色组详情
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups/ChineseWoman"

# 4. 批量TTS生成
curl -X POST "https://tts.ioioioioio.com:1120/breathvoice/batch-tts" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "text": "你好，这是测试文本",
        "filename": "test_greeting.wav",
        "voice_group_id": "ChineseWoman"
      },
      {
        "text": "太令人兴奋了！",
        "filename": "test_B1_excitement.wav",
        "voice_group_id": "ChineseWoman"
      }
    ]
  }'

# 5. 上传角色组ZIP文件
curl -X POST "https://tts.ioioioioio.com:1120/breathvoice/upload-voice-group" \
  -F "file=@character_audio.zip" \
  -F "overwrite=false"
```

## 错误处理

### 常见错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误或格式不正确 |
| 404 | Not Found | 请求的角色组不存在 |
| 409 | Conflict | 角色组已存在（上传时未设置覆盖） |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应格式

```json
{
  "success": false,
  "error": "详细错误信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## 最佳实践

### 1. 角色组管理
- 在批量TTS前先检查角色组是否存在
- 定期备份重要的角色组数据
- 使用有意义的角色组名称

### 2. 批量TTS优化
- 合理控制单次批量请求的数量（建议不超过50个）
- 为文件名使用清晰的命名规范
- 监控处理时间，避免超时

### 3. 错误处理
- 始终检查API响应的success字段
- 实现适当的重试机制
- 记录错误日志便于调试

### 4. 性能考虑
- 避免频繁的小批量请求
- 复用已建立的HTTP连接
- 考虑异步处理大批量任务

## 技术规格

- **支持的音频格式**: WAV (16-bit, 22050Hz)
- **最大文本长度**: 1000字符
- **最大批量请求数**: 100个/次
- **最大ZIP文件大小**: 100MB
- **API速率限制**: 100请求/分钟

## 更新日志

### v1.0.0 (2024-01-20)
- 初始版本发布
- 支持角色组管理
- 支持批量TTS生成
- 支持ZIP文件上传
- 智能参考音频选择

---

**注意**: 本API专为breathVOICE应用程序设计，与标准OpenAI TTS API完全兼容并可同时使用。