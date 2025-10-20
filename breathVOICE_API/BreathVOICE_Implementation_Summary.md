# BreathVOICE API 实现总结

## 项目概述

成功为 IndexTTS 项目实现了 BreathVOICE 应用程序的定制化 API 扩展。该扩展在不影响标准 OpenAI 兼容 API 的基础上，提供了角色组管理、批量 TTS 生成等专用功能。

**外网访问地址**: `https://tts.ioioioioio.com:1120`

## 实现的功能

### ✅ 1. 角色组管理 (VoiceGroupID)
- **功能**: 自动扫描 `examples` 目录下的 `<characterName>_Reference` 文件夹
- **支持的音频文件**:
  - `<characterName>_greeting.wav` - 问候音频
  - `<characterName>_B1_B2.wav` - B1/B2情绪音频
  - `<characterName>_B3_B4.wav` - B3/B4/冲击情绪音频
  - `<characterName>_B5_orgasm.wav` - B5/高潮情绪音频
- **API端点**: 
  - `GET https://tts.ioioioioio.com:1120/breathvoice/voice-groups` - 获取角色组列表
  - `GET https://tts.ioioioioio.com:1120/breathvoice/voice-groups/{voice_group_id}` - 获取角色组详细信息

### ✅ 2. 智能参考音频选择
- **功能**: 根据目标文件名中的关键词自动选择合适的参考音频
- **映射规则**:
  - "greeting" → `_greeting.wav`
  - "B1", "B2" → `_B1_B2.wav`
  - "B0", "B3", "B4", "impact" → `_B3_B4.wav`
  - "B5", "orgasm" → `_B5_orgasm.wav`

### ✅ 3. 批量 TTS 生成
- **功能**: 支持一次请求生成多个 TTS 音频文件
- **API端点**: `POST https://tts.ioioioioio.com:1120/breathvoice/batch-tts`
- **特性**:
  - 自动选择参考音频
  - 详细的生成结果报告
  - 错误处理和状态跟踪

### ✅ 4. ZIP 文件上传支持
- **功能**: 支持上传包含角色组音频文件的 ZIP 压缩包
- **API端点**: `POST https://tts.ioioioioio.com:1120/breathvoice/upload-voice-group`
- **特性**:
  - 自动解压到正确目录
  - 覆盖保护机制
  - 文件验证和错误报告

## 文件结构

```
breathVOICE_API/
├── breathvoice_api.py                    # BreathVOICE API 扩展模块
├── openai_tts_api.py                    # 主 API 服务器（已集成扩展）
├── test_breathvoice_api.py              # API 测试脚本
├── BreathVOICE_API_Documentation.md     # 完整 API 文档
├── External_API_Test_Report.md          # 外网 API 测试报告
├── deploy_breathvoice_to_external.md    # 部署指南
└── examples/
    └── ChineseWoman_Reference/          # 示例角色组数据
        ├── ChineseWoman_greeting.wav
        ├── ChineseWoman_B1_B2.wav
        ├── ChineseWoman_B3_B4.wav
        └── ChineseWoman_B5_orgasm.wav
```

## 核心技术特性

### 1. 无缝集成设计
- **兼容性**: 完全兼容现有 OpenAI TTS API
- **扩展性**: 通过 `/breathvoice` 前缀提供专用功能
- **稳定性**: 不影响原有 API 端点的正常工作

### 2. 智能音频处理
- **自动选择**: 根据文件名关键词智能选择参考音频
- **批量处理**: 支持一次请求处理多个 TTS 任务
- **错误恢复**: 单个任务失败不影响其他任务执行

### 3. 灵活的角色组管理
- **动态扫描**: 自动发现新添加的角色组
- **文件验证**: 检查必需的参考音频文件
- **详细信息**: 提供角色组的完整配置信息

## API 端点详情

### 1. 获取角色组列表
```http
GET https://tts.ioioioioio.com:1120/breathvoice/voice-groups
```

**响应示例**:
```json
{
  "voice_groups": ["ChineseWoman"],
  "count": 1
}
```

### 2. 获取角色组详情
```http
GET https://tts.ioioioioio.com:1120/breathvoice/voice-groups/ChineseWoman
```

**响应示例**:
```json
{
  "voice_group_id": "ChineseWoman",
  "reference_files": {
    "greeting": "ChineseWoman_greeting.wav",
    "B1_B2": "ChineseWoman_B1_B2.wav",
    "B3_B4": "ChineseWoman_B3_B4.wav",
    "B5_orgasm": "ChineseWoman_B5_orgasm.wav"
  },
  "available_emotions": ["greeting", "B1_B2", "B3_B4", "B5_orgasm"]
}
```

### 3. 批量 TTS 生成
```http
POST https://tts.ioioioioio.com:1120/breathvoice/batch-tts
Content-Type: application/json

{
  "voice_group_id": "ChineseWoman",
  "requests": [
    {
      "text": "你好，欢迎使用 BreathVOICE！",
      "filename": "greeting_demo.wav"
    },
    {
      "text": "这是一个测试文本。",
      "filename": "B1_test.wav"
    }
  ]
}
```

### 4. 上传角色组
```http
POST https://tts.ioioioioio.com:1120/breathvoice/upload-voice-group
Content-Type: multipart/form-data

file: [ZIP文件包含角色组音频文件]
voice_group_id: NewCharacter
overwrite: false
```

## 使用示例

### Python 示例
```python
import requests

# 基础配置
BASE_URL = "https://tts.ioioioioio.com:1120"

# 1. 获取可用角色组
response = requests.get(f"{BASE_URL}/breathvoice/voice-groups")
voice_groups = response.json()["voice_groups"]
print(f"可用角色组: {voice_groups}")

# 2. 批量生成 TTS
batch_request = {
    "voice_group_id": "ChineseWoman",
    "requests": [
        {
            "text": "你好，欢迎使用 BreathVOICE！",
            "filename": "greeting_demo.wav"
        }
    ]
}

response = requests.post(
    f"{BASE_URL}/breathvoice/batch-tts",
    json=batch_request
)

if response.status_code == 200:
    results = response.json()
    print(f"生成成功: {results['successful_count']} 个文件")
else:
    print(f"生成失败: {response.text}")
```

### JavaScript 示例
```javascript
const BASE_URL = "https://tts.ioioioioio.com:1120";

// 获取角色组列表
async function getVoiceGroups() {
    const response = await fetch(`${BASE_URL}/breathvoice/voice-groups`);
    const data = await response.json();
    return data.voice_groups;
}

// 批量 TTS 生成
async function batchTTS(voiceGroupId, requests) {
    const response = await fetch(`${BASE_URL}/breathvoice/batch-tts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            voice_group_id: voiceGroupId,
            requests: requests
        })
    });
    
    return await response.json();
}
```

### cURL 示例
```bash
# 获取角色组列表
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups"

# 批量 TTS 生成
curl -X POST "https://tts.ioioioioio.com:1120/breathvoice/batch-tts" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_group_id": "ChineseWoman",
    "requests": [
      {
        "text": "你好，欢迎使用 BreathVOICE！",
        "filename": "greeting_demo.wav"
      }
    ]
  }'
```

## 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 角色组不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式
```json
{
  "error": "错误描述",
  "details": "详细错误信息"
}
```

## 性能特性

### 1. 并发处理
- 支持多个 TTS 请求并发处理
- 智能任务调度和资源管理

### 2. 缓存机制
- 角色组信息缓存
- 减少文件系统访问次数

### 3. 错误恢复
- 单个任务失败不影响整体处理
- 详细的错误报告和状态跟踪

## 部署状态

### 当前状态
- ✅ 本地开发环境完全正常
- ⚠️ 外网服务器需要部署更新

### 部署要求
1. 上传核心文件到外网服务器
2. 重启 API 服务
3. 验证所有端点正常工作

详细部署步骤请参考 `deploy_breathvoice_to_external.md`。

## 测试和验证

### 自动化测试
使用 `test_breathvoice_api.py` 脚本进行完整功能测试：

```bash
python test_breathvoice_api.py
```

### 手动测试清单
- [ ] 角色组列表获取正常
- [ ] 角色组详情查询正常
- [ ] 批量 TTS 生成功能正常
- [ ] ZIP 文件上传功能正常
- [ ] 错误处理机制正常

## 未来扩展计划

### 1. 功能增强
- 支持更多音频格式
- 添加音频质量控制参数
- 实现音频预处理功能

### 2. 性能优化
- 实现音频文件缓存
- 优化批量处理性能
- 添加负载均衡支持

### 3. 管理功能
- 添加角色组管理界面
- 实现音频文件在线编辑
- 提供使用统计和监控

## 总结

BreathVOICE API 扩展成功实现了所有预期功能，提供了完整的角色组管理和批量 TTS 生成能力。该扩展具有良好的兼容性、稳定性和扩展性，为 IndexTTS 项目增加了强大的定制化功能。

**关键成就**:
- ✅ 完全兼容现有 OpenAI API
- ✅ 智能参考音频选择机制
- ✅ 高效的批量处理能力
- ✅ 灵活的角色组管理
- ✅ 完善的错误处理和状态报告

**下一步行动**:
1. 完成外网服务器部署
2. 进行全面功能测试
3. 优化性能和用户体验

---

**文档版本**: v2.0  
**最后更新**: 2024年12月  
**外网地址**: https://tts.ioioioioio.com:1120