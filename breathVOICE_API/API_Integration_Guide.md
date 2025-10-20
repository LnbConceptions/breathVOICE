# BreathVOICE API 集成指南

## 概述

本指南为其他 AI 助手和开发者提供详细的 BreathVOICE API 集成说明，包括完整的端点文档、示例代码和最佳实践。

**API 基础地址**: `https://tts.ioioioioio.com:1120`

## 快速开始

### 1. 基础连接测试

首先验证 API 服务是否可访问：

```python
import requests

BASE_URL = "https://tts.ioioioioio.com:1120"

# 测试基础连接
response = requests.get(f"{BASE_URL}/")
print(f"服务状态: {response.status_code}")

# 测试 BreathVOICE 扩展
response = requests.get(f"{BASE_URL}/breathvoice/voice-groups")
if response.status_code == 200:
    print("BreathVOICE API 可用")
    print(f"可用角色组: {response.json()}")
else:
    print(f"BreathVOICE API 不可用: {response.status_code}")
```

### 2. 获取 API 文档

```python
# 获取完整的 OpenAPI 规范
response = requests.get(f"{BASE_URL}/openapi.json")
api_spec = response.json()

# 查看所有可用端点
for path, methods in api_spec["paths"].items():
    print(f"{path}: {list(methods.keys())}")
```

## API 端点详细说明

### 1. 获取角色组列表

**端点**: `GET /breathvoice/voice-groups`

**描述**: 获取所有可用的角色组（VoiceGroupID）列表

**请求示例**:
```python
import requests

response = requests.get("https://tts.ioioioioio.com:1120/breathvoice/voice-groups")
data = response.json()
```

**响应格式**:
```json
{
  "voice_groups": ["ChineseWoman", "EnglishMan", "JapaneseGirl"],
  "count": 3
}
```

**字段说明**:
- `voice_groups`: 字符串数组，包含所有可用的角色组ID
- `count`: 整数，角色组总数

**错误处理**:
```python
if response.status_code == 200:
    voice_groups = response.json()["voice_groups"]
    print(f"找到 {len(voice_groups)} 个角色组")
else:
    print(f"获取失败: {response.status_code} - {response.text}")
```

### 2. 获取角色组详细信息

**端点**: `GET /breathvoice/voice-groups/{voice_group_id}`

**描述**: 获取指定角色组的详细配置信息

**路径参数**:
- `voice_group_id`: 角色组ID（如 "ChineseWoman"）

**请求示例**:
```python
voice_group_id = "ChineseWoman"
response = requests.get(f"https://tts.ioioioioio.com:1120/breathvoice/voice-groups/{voice_group_id}")
```

**响应格式**:
```json
{
  "voice_group_id": "ChineseWoman",
  "reference_files": {
    "greeting": "ChineseWoman_greeting.wav",
    "B1_B2": "ChineseWoman_B1_B2.wav",
    "B3_B4": "ChineseWoman_B3_B4.wav",
    "B5_orgasm": "ChineseWoman_B5_orgasm.wav"
  },
  "available_emotions": ["greeting", "B1_B2", "B3_B4", "B5_orgasm"],
  "file_count": 4,
  "status": "ready"
}
```

**字段说明**:
- `voice_group_id`: 角色组ID
- `reference_files`: 参考音频文件映射
- `available_emotions`: 可用的情绪类型
- `file_count`: 参考文件数量
- `status`: 角色组状态（"ready" 或 "incomplete"）

### 3. 单条 TTS 生成

**端点**: `POST /breathvoice/single-tts`

**描述**: 生成单个 TTS 音频文件，支持逐条生成工作流

**请求体格式**:
```json
{
  "text": "要转换的文本",
  "filename": "输出文件名.wav",
  "voice_group_id": "角色组ID"
}
```

**请求示例**:
```python
import requests

# 单条TTS生成
single_request = {
    "text": "你好，欢迎来到我们的世界！",
    "filename": "greeting_001.wav",
    "voice_group_id": "ChineseWoman"
}

response = requests.post(
    "https://tts.ioioioioio.com:1120/breathvoice/single-tts",
    json=single_request,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"生成成功: {result['result']['output_path']}")
    print(f"处理时间: {result['result']['processing_time']}秒")
else:
    print(f"生成失败: {response.status_code} - {response.text}")
```

**响应格式**:
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

**字段说明**:
- `success`: 布尔值，表示请求是否成功
- `message`: 字符串，操作结果消息
- `result`: 对象，包含生成结果详情
  - `filename`: 输出文件名
  - `text`: 原始文本
  - `reference_audio`: 使用的参考音频文件
  - `output_path`: 生成的音频文件路径
  - `status`: 生成状态（"success" 或 "failed"）
  - `processing_time`: 处理时间（秒）

**错误响应**:
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

**逐条生成工作流示例**:
```python
def sequential_tts_generation(requests_list):
    """
    逐条生成TTS音频，支持实时状态更新
    """
    results = []
    
    for i, request in enumerate(requests_list):
        print(f"正在生成第 {i+1}/{len(requests_list)} 条: {request['text'][:20]}...")
        
        response = requests.post(
            "https://tts.ioioioioio.com:1120/breathvoice/single-tts",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            results.append(result['result'])
            print(f"✓ 生成成功: {result['result']['filename']}")
        else:
            error_result = {
                "filename": request['filename'],
                "text": request['text'],
                "status": "failed",
                "error": f"HTTP {response.status_code}"
            }
            results.append(error_result)
            print(f"✗ 生成失败: {request['filename']}")
    
    return results

# 使用示例
requests_list = [
    {
        "text": "你好，欢迎来到我们的世界！",
        "filename": "greeting_001.wav",
        "voice_group_id": "ChineseWoman"
    },
    {
        "text": "这真是太令人兴奋了！",
        "filename": "B1_start_004.wav",
        "voice_group_id": "ChineseWoman"
    }
]

results = sequential_tts_generation(requests_list)
```

### 4. 批量 TTS 生成

**端点**: `POST /breathvoice/batch-tts`

**描述**: 批量生成 TTS 音频文件，支持智能参考音频选择

**请求体格式**:
```json
{
  "requests": [
    {
      "text": "你好，欢迎使用 BreathVOICE！",
      "filename": "greeting_demo.wav",
      "voice_group_id": "ChineseWoman"
    },
    {
      "text": "这是一个测试文本。",
      "filename": "B1_test.wav",
      "voice_group_id": "ChineseWoman"
    }
  ]
}
```

**请求参数说明**:
- `requests`: 必需，TTS 请求数组
  - `text`: 必需，要转换的文本
  - `filename`: 必需，输出文件名（用于智能选择参考音频）
  - `voice_group_id`: 必需，角色组ID

**智能参考音频选择规则**:
- 文件名包含 "greeting" → 使用 greeting 参考音频
- 文件名包含 "B1" 或 "B2" → 使用 B1_B2 参考音频
- 文件名包含 "B0", "B3", "B4", "impact" → 使用 B3_B4 参考音频
- 文件名包含 "B5" 或 "orgasm" → 使用 B5_orgasm 参考音频
- 默认 → 使用 greeting 参考音频

**完整请求示例**:
```python
import requests
import json

def batch_tts_generation(text_requests):
    """
    批量 TTS 生成函数
    
    Args:
        text_requests (list): TTS 请求列表，每个请求包含 text, filename, voice_group_id
    
    Returns:
        dict: 生成结果
    """
    url = "https://tts.ioioioioio.com:1120/breathvoice/batch-tts"
    
    payload = {
        "requests": text_requests
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "请求超时"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"请求异常: {str(e)}"
        }

# 使用示例
requests_data = [
    {
        "text": "你好，欢迎使用 BreathVOICE！",
        "filename": "greeting_welcome.wav",
        "voice_group_id": "ChineseWoman"
    },
    {
        "text": "这是 B1 情绪的测试文本。",
        "filename": "emotion_B1_test.wav",
        "voice_group_id": "ChineseWoman"
    },
    {
        "text": "这是高潮情绪的测试。",
        "filename": "emotion_B5_orgasm_test.wav",
        "voice_group_id": "ChineseWoman"
    }
]

result = batch_tts_generation(requests_data)

if result["success"]:
    data = result["data"]
    print(f"生成成功: {data['successful_count']} 个文件")
    print(f"失败: {data['failed_count']} 个文件")
    
    # 查看详细结果
    for item in data["results"]:
        if item["success"]:
            print(f"✅ {item['filename']}: {item['output_path']}")
        else:
            print(f"❌ {item['filename']}: {item['error']}")
else:
    print(f"批量生成失败: {result['error']}")
```

**响应格式**:
```json
{
  "successful_count": 2,
  "failed_count": 1,
  "total_count": 3,
  "results": [
    {
      "filename": "greeting_demo.wav",
      "success": true,
      "output_path": "/path/to/output/greeting_demo.wav",
      "reference_audio": "ChineseWoman_greeting.wav",
      "processing_time": 2.34
    },
    {
      "filename": "B1_test.wav",
      "success": true,
      "output_path": "/path/to/output/B1_test.wav",
      "reference_audio": "ChineseWoman_B1_B2.wav",
      "processing_time": 1.87
    },
    {
      "filename": "invalid_test.wav",
      "success": false,
      "error": "文本为空"
    }
  ]
}
```

### 4. 上传角色组

**端点**: `POST /breathvoice/upload-voice-group`

**描述**: 上传包含角色组音频文件的 ZIP 压缩包

**请求格式**: `multipart/form-data`

**表单字段**:
- `file`: 必需，ZIP 文件
- `voice_group_id`: 必需，角色组ID
- `overwrite`: 可选，是否覆盖现有文件（默认 false）

**请求示例**:
```python
import requests

def upload_voice_group(zip_file_path, voice_group_id, overwrite=False):
    """
    上传角色组 ZIP 文件
    
    Args:
        zip_file_path (str): ZIP 文件路径
        voice_group_id (str): 角色组ID
        overwrite (bool): 是否覆盖现有文件
    
    Returns:
        dict: 上传结果
    """
    url = "https://tts.ioioioioio.com:1120/breathvoice/upload-voice-group"
    
    with open(zip_file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'voice_group_id': voice_group_id,
            'overwrite': str(overwrite).lower()
        }
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}"
        }

# 使用示例
result = upload_voice_group("NewCharacter.zip", "NewCharacter", overwrite=False)

if result["success"]:
    print("上传成功!")
    print(f"解压的文件: {result['data']['extracted_files']}")
else:
    print(f"上传失败: {result['error']}")
```

**ZIP 文件结构要求**:
```
NewCharacter.zip
├── NewCharacter_greeting.wav
├── NewCharacter_B1_B2.wav
├── NewCharacter_B3_B4.wav
└── NewCharacter_B5_orgasm.wav
```

**响应格式**:
```json
{
  "message": "角色组上传成功",
  "voice_group_id": "NewCharacter",
  "extracted_files": [
    "NewCharacter_greeting.wav",
    "NewCharacter_B1_B2.wav",
    "NewCharacter_B3_B4.wav",
    "NewCharacter_B5_orgasm.wav"
  ],
  "target_directory": "/path/to/examples/NewCharacter_Reference"
}
```

## 完整集成示例

### Python 集成类

```python
import requests
import json
from typing import List, Dict, Optional, Union

class BreathVOICEClient:
    """BreathVOICE API 客户端"""
    
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120"):
        """
        初始化客户端
        
        Args:
            base_url (str): API 基础地址
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    def get_voice_groups(self) -> Dict[str, Union[List[str], int]]:
        """
        获取所有角色组
        
        Returns:
            dict: 角色组信息
        """
        response = self.session.get(f"{self.base_url}/breathvoice/voice-groups")
        response.raise_for_status()
        return response.json()
    
    def get_voice_group_details(self, voice_group_id: str) -> Dict:
        """
        获取角色组详细信息
        
        Args:
            voice_group_id (str): 角色组ID
            
        Returns:
            dict: 角色组详细信息
        """
        response = self.session.get(f"{self.base_url}/breathvoice/voice-groups/{voice_group_id}")
        response.raise_for_status()
        return response.json()
    
    def batch_tts(self, requests: List[Dict[str, str]]) -> Dict:
        """
        批量 TTS 生成
        
        Args:
            requests (list): TTS 请求列表，每个请求包含 text, filename, voice_group_id
            
        Returns:
            dict: 生成结果
        """
        payload = {
            "requests": requests
        }
        
        response = self.session.post(
            f"{self.base_url}/breathvoice/batch-tts",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def upload_voice_group(self, zip_file_path: str, voice_group_id: str, overwrite: bool = False) -> Dict:
        """
        上传角色组
        
        Args:
            zip_file_path (str): ZIP 文件路径
            voice_group_id (str): 角色组ID
            overwrite (bool): 是否覆盖现有文件
            
        Returns:
            dict: 上传结果
        """
        with open(zip_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'voice_group_id': voice_group_id,
                'overwrite': str(overwrite).lower()
            }
            
            response = self.session.post(
                f"{self.base_url}/breathvoice/upload-voice-group",
                files=files,
                data=data
            )
        
        response.raise_for_status()
        return response.json()

# 使用示例
def main():
    # 初始化客户端
    client = BreathVOICEClient()
    
    # 测试连接
    if not client.test_connection():
        print("无法连接到 BreathVOICE API")
        return
    
    print("✅ API 连接成功")
    
    # 获取角色组列表
    voice_groups = client.get_voice_groups()
    print(f"📋 可用角色组: {voice_groups['voice_groups']}")
    
    if voice_groups['voice_groups']:
        # 获取第一个角色组的详细信息
        first_group = voice_groups['voice_groups'][0]
        details = client.get_voice_group_details(first_group)
        print(f"📝 {first_group} 详细信息: {details}")
        
        # 批量 TTS 生成
        tts_requests = [
            {
                "text": "你好，这是一个测试。",
                "filename": "greeting_test.wav",
                "voice_group_id": first_group
            },
            {
                "text": "这是 B1 情绪测试。",
                "filename": "B1_emotion_test.wav",
                "voice_group_id": first_group
            }
        ]
        
        try:
            results = client.batch_tts(tts_requests)
            print(f"🎵 TTS 生成结果: 成功 {results['successful_count']} 个，失败 {results['failed_count']} 个")
            
            for result in results['results']:
                if result['success']:
                    print(f"  ✅ {result['filename']}: {result['output_path']}")
                else:
                    print(f"  ❌ {result['filename']}: {result['error']}")
        
        except Exception as e:
            print(f"❌ TTS 生成失败: {e}")

if __name__ == "__main__":
    main()
```

### JavaScript 集成示例

```javascript
class BreathVOICEClient {
    constructor(baseUrl = "https://tts.ioioioioio.com:1120") {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async testConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/`);
            return response.ok;
        } catch {
            return false;
        }
    }
    
    async getVoiceGroups() {
        const response = await fetch(`${this.baseUrl}/breathvoice/voice-groups`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        return await response.json();
    }
    
    async getVoiceGroupDetails(voiceGroupId) {
        const response = await fetch(`${this.baseUrl}/breathvoice/voice-groups/${voiceGroupId}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        return await response.json();
    }
    
    async batchTTS(requests) {
        const response = await fetch(`${this.baseUrl}/breathvoice/batch-tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requests: requests
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }
    
    async uploadVoiceGroup(zipFile, voiceGroupId, overwrite = false) {
        const formData = new FormData();
        formData.append('file', zipFile);
        formData.append('voice_group_id', voiceGroupId);
        formData.append('overwrite', overwrite.toString());
        
        const response = await fetch(`${this.baseUrl}/breathvoice/upload-voice-group`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }
}

// 使用示例
async function main() {
    const client = new BreathVOICEClient();
    
    // 测试连接
    if (!(await client.testConnection())) {
        console.log("无法连接到 BreathVOICE API");
        return;
    }
    
    console.log("✅ API 连接成功");
    
    try {
        // 获取角色组列表
        const voiceGroups = await client.getVoiceGroups();
        console.log(`📋 可用角色组: ${voiceGroups.voice_groups}`);
        
        if (voiceGroups.voice_groups.length > 0) {
            const firstGroup = voiceGroups.voice_groups[0];
            
            // 获取详细信息
            const details = await client.getVoiceGroupDetails(firstGroup);
            console.log(`📝 ${firstGroup} 详细信息:`, details);
            
            // 批量 TTS
            const ttsRequests = [
                {
                    text: "你好，这是一个测试。",
                    filename: "greeting_test.wav",
                    voice_group_id: firstGroup
                }
            ];
            
            const results = await client.batchTTS(ttsRequests);
            console.log(`🎵 TTS 生成结果: 成功 ${results.successful_count} 个`);
        }
    } catch (error) {
        console.error("❌ 操作失败:", error.message);
    }
}
```

## 错误处理最佳实践

### 1. HTTP 状态码处理

```python
def handle_api_response(response):
    """处理 API 响应"""
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    elif response.status_code == 400:
        return {"success": False, "error": "请求参数错误", "details": response.text}
    elif response.status_code == 404:
        return {"success": False, "error": "资源不存在", "details": response.text}
    elif response.status_code == 500:
        return {"success": False, "error": "服务器内部错误", "details": response.text}
    else:
        return {"success": False, "error": f"未知错误 {response.status_code}", "details": response.text}
```

### 2. 网络异常处理

```python
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

def safe_api_call(func, *args, **kwargs):
    """安全的 API 调用包装器"""
    try:
        return func(*args, **kwargs)
    except Timeout:
        return {"success": False, "error": "请求超时"}
    except ConnectionError:
        return {"success": False, "error": "网络连接错误"}
    except RequestException as e:
        return {"success": False, "error": f"请求异常: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"未知异常: {str(e)}"}
```

### 3. 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result.get("success", False):
                        return result
                    
                    if attempt < max_retries - 1:
                        print(f"尝试 {attempt + 1} 失败，{delay} 秒后重试...")
                        time.sleep(delay)
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"尝试 {attempt + 1} 异常: {e}，{delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        return {"success": False, "error": f"重试 {max_retries} 次后仍然失败: {e}"}
            
            return {"success": False, "error": f"重试 {max_retries} 次后仍然失败"}
        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, delay=2)
def reliable_batch_tts(voice_group_id, requests):
    client = BreathVOICEClient()
    return {"success": True, "data": client.batch_tts(voice_group_id, requests)}
```

## 性能优化建议

### 1. 连接池使用

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedBreathVOICEClient:
    def __init__(self, base_url="https://tts.ioioioioio.com:1120"):
        self.base_url = base_url.rstrip('/')
        
        # 配置会话和连接池
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认超时
        self.session.timeout = 30
```

### 2. 批量请求优化

```python
def optimize_batch_requests(requests, max_batch_size=10):
    """
    优化批量请求，分批处理大量请求
    
    Args:
        requests (list): 原始请求列表
        max_batch_size (int): 每批最大请求数
        
    Returns:
        list: 分批后的请求列表
    """
    batches = []
    for i in range(0, len(requests), max_batch_size):
        batch = requests[i:i + max_batch_size]
        batches.append(batch)
    return batches

def process_large_batch(client, voice_group_id, all_requests):
    """处理大批量请求"""
    batches = optimize_batch_requests(all_requests, max_batch_size=10)
    all_results = []
    
    for i, batch in enumerate(batches):
        print(f"处理批次 {i + 1}/{len(batches)}...")
        
        try:
            result = client.batch_tts(voice_group_id, batch)
            all_results.extend(result["results"])
            
            # 批次间添加延迟，避免服务器过载
            if i < len(batches) - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"批次 {i + 1} 处理失败: {e}")
            # 为失败的批次添加错误结果
            for req in batch:
                all_results.append({
                    "filename": req["filename"],
                    "success": False,
                    "error": f"批次处理失败: {e}"
                })
    
    return all_results
```

## 监控和日志

### 1. API 调用监控

```python
import logging
import time
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BreathVOICE')

def monitor_api_call(func):
    """API 调用监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        logger.info(f"开始调用 {func_name}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if result.get("success", False):
                logger.info(f"{func_name} 调用成功，耗时 {duration:.2f} 秒")
            else:
                logger.warning(f"{func_name} 调用失败: {result.get('error', '未知错误')}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func_name} 调用异常，耗时 {duration:.2f} 秒: {e}")
            raise
    
    return wrapper

# 使用示例
class MonitoredBreathVOICEClient(BreathVOICEClient):
    @monitor_api_call
    def batch_tts(self, voice_group_id, requests):
        return super().batch_tts(voice_group_id, requests)
    
    @monitor_api_call
    def get_voice_groups(self):
        return super().get_voice_groups()
```

### 2. 性能统计

```python
class PerformanceTracker:
    def __init__(self):
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_duration": 0,
            "average_duration": 0
        }
    
    def record_call(self, success, duration):
        self.stats["total_calls"] += 1
        self.stats["total_duration"] += duration
        
        if success:
            self.stats["successful_calls"] += 1
        else:
            self.stats["failed_calls"] += 1
        
        self.stats["average_duration"] = self.stats["total_duration"] / self.stats["total_calls"]
    
    def get_stats(self):
        return self.stats.copy()
    
    def print_stats(self):
        stats = self.get_stats()
        print("=== API 调用统计 ===")
        print(f"总调用次数: {stats['total_calls']}")
        print(f"成功次数: {stats['successful_calls']}")
        print(f"失败次数: {stats['failed_calls']}")
        print(f"成功率: {stats['successful_calls'] / stats['total_calls'] * 100:.1f}%")
        print(f"平均响应时间: {stats['average_duration']:.2f} 秒")

# 全局性能跟踪器
performance_tracker = PerformanceTracker()
```

## 安全最佳实践

### 1. API 密钥管理（如果需要）

```python
import os
from typing import Optional

class SecureBreathVOICEClient(BreathVOICEClient):
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120", api_key: Optional[str] = None):
        super().__init__(base_url)
        
        # 从环境变量获取 API 密钥
        self.api_key = api_key or os.getenv('BREATHVOICE_API_KEY')
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
```

### 2. 输入验证

```python
def validate_tts_request(request):
    """验证 TTS 请求"""
    if not isinstance(request, dict):
        return False, "请求必须是字典格式"
    
    if "text" not in request:
        return False, "缺少 text 字段"
    
    if "filename" not in request:
        return False, "缺少 filename 字段"
    
    if not isinstance(request["text"], str) or not request["text"].strip():
        return False, "text 字段不能为空"
    
    if not isinstance(request["filename"], str) or not request["filename"].strip():
        return False, "filename 字段不能为空"
    
    # 检查文件名安全性
    if any(char in request["filename"] for char in ['..', '/', '\\']):
        return False, "filename 包含不安全字符"
    
    return True, "验证通过"

def safe_batch_tts(client, voice_group_id, requests):
    """安全的批量 TTS 调用"""
    # 验证角色组ID
    if not voice_group_id or not isinstance(voice_group_id, str):
        return {"success": False, "error": "无效的 voice_group_id"}
    
    # 验证请求列表
    if not isinstance(requests, list) or not requests:
        return {"success": False, "error": "requests 必须是非空列表"}
    
    # 验证每个请求
    for i, request in enumerate(requests):
        valid, message = validate_tts_request(request)
        if not valid:
            return {"success": False, "error": f"请求 {i + 1} 验证失败: {message}"}
    
    # 执行 API 调用
    return client.batch_tts(voice_group_id, requests)
```

## 总结

本集成指南提供了完整的 BreathVOICE API 集成方案，包括：

1. **完整的 API 端点文档**
2. **详细的请求/响应格式说明**
3. **多语言集成示例**（Python、JavaScript）
4. **错误处理和重试机制**
5. **性能优化建议**
6. **监控和日志记录**
7. **安全最佳实践**

使用本指南，其他 AI 助手和开发者可以快速、安全、高效地集成 BreathVOICE API 功能。

---

**重要提醒**:
- 确保 API 服务器 `https://tts.ioioioioio.com:1120` 已正确部署 BreathVOICE 扩展
- 在生产环境中使用时，请添加适当的认证和限流机制
- 定期监控 API 性能和可用性
- 遵循最佳实践进行错误处理和重试