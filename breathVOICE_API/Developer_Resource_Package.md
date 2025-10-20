# BreathVOICE API 开发者资料包

## 📋 概述

本资料包为其他 AI 助手和开发者提供完整的 BreathVOICE API 集成资源，确保能够快速、准确地集成和使用 BreathVOICE 服务。

**API 基础信息**:
- **服务地址**: `https://tts.ioioioioio.com:1120`
- **API 前缀**: `/breathvoice`
- **协议**: HTTPS
- **认证**: 无需认证（当前版本）

## 📁 资料包内容

### 1. 核心文档
- `BreathVOICE_API_Documentation.md` - 完整 API 文档
- `API_Integration_Guide.md` - 集成指南和最佳实践
- `API_Usability_Testing.md` - 可用性测试指南
- `BreathVOICE_Implementation_Summary.md` - 实现总结
- `External_API_Test_Report.md` - 外部 API 测试报告
- `deploy_breathvoice_to_external.md` - 部署指南

### 2. 测试脚本
- `test_breathvoice_api.py` - API 测试脚本
- 内置性能测试和健康检查功能

### 3. 示例代码
- Python 集成示例
- JavaScript 集成示例
- cURL 命令示例

## 🚀 快速开始

### 第一步：验证 API 可用性

```python
import requests

# 基础连通性测试
def test_api_connectivity():
    base_url = "https://tts.ioioioioio.com:1120"
    
    try:
        # 测试根端点
        response = requests.get(f"{base_url}/")
        print(f"根端点状态: {response.status_code}")
        
        # 测试 BreathVOICE 端点
        response = requests.get(f"{base_url}/breathvoice/voice-groups")
        if response.status_code == 200:
            voice_groups = response.json()
            print(f"✅ API 可用，发现 {len(voice_groups.get('voice_groups', []))} 个角色组")
            return True
        else:
            print(f"❌ BreathVOICE 端点不可用: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

# 运行测试
if test_api_connectivity():
    print("🎉 可以开始集成 BreathVOICE API！")
```

### 第二步：获取可用角色组

```python
def get_available_voice_groups():
    """获取所有可用的角色组"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    try:
        response = requests.get(f"{base_url}/breathvoice/voice-groups")
        if response.status_code == 200:
            data = response.json()
            voice_groups = data.get("voice_groups", [])
            
            print("📋 可用角色组:")
            for group_id in voice_groups:
                print(f"  - {group_id}")
            
            return voice_groups
        else:
            print(f"获取角色组失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"请求失败: {e}")
        return []

# 获取角色组列表
voice_groups = get_available_voice_groups()
```

### 第三步：生成语音

#### 单条生成（推荐用于逐条工作流）

```python
def generate_single_speech(voice_group_id, text, filename):
    """
    生成单个TTS音频文件
    
    Args:
        voice_group_id (str): 角色组ID
        text (str): 要转换的文本
        filename (str): 输出文件名
    
    Returns:
        dict: 生成结果
    """
    base_url = "https://tts.ioioioioio.com:1120"
    
    request_data = {
        "text": text,
        "filename": filename,
        "voice_group_id": voice_group_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/breathvoice/single-tts",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 生成成功: {result['result']['filename']}")
            print(f"   输出路径: {result['result']['output_path']}")
            print(f"   处理时间: {result['result']['processing_time']}秒")
            return result['result']
        else:
            print(f"❌ 生成失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

# 使用示例
result = generate_single_speech(
    voice_group_id="ChineseWoman",
    text="你好，欢迎来到我们的世界！",
    filename="greeting_001.wav"
)
```

#### 逐条生成工作流

```python
class SequentialTTSGenerator:
    """逐条TTS生成器，支持实时状态更新和停止控制"""
    
    def __init__(self, base_url="https://tts.ioioioioio.com:1120"):
        self.base_url = base_url
        self.stop_flag = False
        self.current_index = 0
        self.total_count = 0
        self.results = []
    
    def stop_generation(self):
        """停止生成（完成当前任务后停止）"""
        self.stop_flag = True
        print("🛑 收到停止信号，将在当前任务完成后停止")
    
    def generate_sequential(self, requests_list, progress_callback=None):
        """
        逐条生成TTS音频
        
        Args:
            requests_list (list): TTS请求列表
            progress_callback (callable): 进度回调函数
        
        Returns:
            list: 生成结果列表
        """
        self.total_count = len(requests_list)
        self.results = []
        self.stop_flag = False
        
        print(f"🎵 开始逐条生成 {self.total_count} 个音频文件")
        
        for i, request in enumerate(requests_list):
            if self.stop_flag:
                print(f"⏹️ 生成已停止，完成了 {i}/{self.total_count} 个文件")
                break
            
            self.current_index = i + 1
            
            # 更新进度
            if progress_callback:
                progress_callback(self.current_index, self.total_count, request['text'])
            
            print(f"[{self.current_index}/{self.total_count}] 正在生成: {request['text'][:30]}...")
            
            # 发送单条TTS请求
            try:
                response = requests.post(
                    f"{self.base_url}/breathvoice/single-tts",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()['result']
                    self.results.append(result)
                    print(f"✅ 生成成功: {result['filename']} ({result['processing_time']:.2f}s)")
                else:
                    error_result = {
                        "filename": request['filename'],
                        "text": request['text'],
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    }
                    self.results.append(error_result)
                    print(f"❌ 生成失败: {request['filename']}")
                    
            except Exception as e:
                error_result = {
                    "filename": request['filename'],
                    "text": request['text'],
                    "status": "failed",
                    "error": str(e)
                }
                self.results.append(error_result)
                print(f"❌ 请求异常: {request['filename']} - {e}")
        
        success_count = sum(1 for r in self.results if r.get('status') == 'success')
        print(f"🎉 生成完成: {success_count}/{len(self.results)} 成功")
        
        return self.results

# 使用示例
def progress_callback(current, total, text):
    """进度回调函数"""
    progress = (current / total) * 100
    print(f"📊 进度: {progress:.1f}% - {text[:20]}...")

# 创建生成器
generator = SequentialTTSGenerator()

# 准备请求列表
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
    },
    {
        "text": "哇，这种感觉真是难以置信！",
        "filename": "B3_reaction_002.wav",
        "voice_group_id": "ChineseWoman"
    }
]

# 开始逐条生成
results = generator.generate_sequential(requests_list, progress_callback)

# 如果需要停止生成，可以调用：
# generator.stop_generation()
```

#### 批量生成（原有功能）

```python
def generate_speech(voice_group_id, text, filename):
    """生成单个语音文件"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    payload = {
        "voice_group_id": voice_group_id,
        "requests": [
            {
                "text": text,
                "filename": filename
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/breathvoice/batch-tts",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 语音生成成功:")
            print(f"  成功: {result.get('successful_count', 0)}")
            print(f"  失败: {result.get('failed_count', 0)}")
            
            for item in result.get("results", []):
                if item["success"]:
                    print(f"  📁 {item['filename']}: {item['file_path']}")
                else:
                    print(f"  ❌ {item['filename']}: {item['error']}")
            
            return result
        else:
            print(f"生成失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None

# 示例使用
if voice_groups:
    result = generate_speech(
        voice_group_id=voice_groups[0],  # 使用第一个可用角色组
        text="你好，这是一个测试。",
        filename="test_greeting.wav"
    )
```

## 🔧 核心 API 端点

### 1. 获取角色组列表

**端点**: `GET /breathvoice/voice-groups`

**响应示例**:
```json
{
  "voice_groups": ["ChineseWoman", "EnglishMale", "JapaneseGirl"],
  "total_count": 3
}
```

**Python 示例**:
```python
response = requests.get("https://tts.ioioioioio.com:1120/breathvoice/voice-groups")
voice_groups = response.json()["voice_groups"]
```

**JavaScript 示例**:
```javascript
const response = await fetch('https://tts.ioioioioio.com:1120/breathvoice/voice-groups');
const data = await response.json();
const voiceGroups = data.voice_groups;
```

### 2. 获取角色组详情

**端点**: `GET /breathvoice/voice-groups/{voice_group_id}`

**响应示例**:
```json
{
  "voice_group_id": "ChineseWoman",
  "reference_files": [
    {
      "filename": "ChineseWoman_greeting.wav",
      "keywords": ["greeting", "hello", "你好", "欢迎"],
      "file_path": "/path/to/ChineseWoman_greeting.wav"
    },
    {
      "filename": "ChineseWoman_B1_B2.wav",
      "keywords": ["B1", "B2", "gentle", "soft"],
      "file_path": "/path/to/ChineseWoman_B1_B2.wav"
    }
  ],
  "total_files": 2
}
```

### 3. 批量 TTS 生成

**端点**: `POST /breathvoice/batch-tts`

**请求格式**:
```json
{
  "voice_group_id": "ChineseWoman",
  "requests": [
    {
      "text": "要转换的文本",
      "filename": "output_filename.wav"
    }
  ]
}
```

**响应格式**:
```json
{
  "successful_count": 1,
  "failed_count": 0,
  "results": [
    {
      "filename": "output_filename.wav",
      "success": true,
      "file_path": "/path/to/generated/output_filename.wav",
      "reference_file": "ChineseWoman_greeting.wav",
      "processing_time": 2.34
    }
  ]
}
```

### 4. 上传角色组

**端点**: `POST /breathvoice/upload-voice-group`

**请求**: 多部分表单数据，包含 ZIP 文件

**响应示例**:
```json
{
  "success": true,
  "voice_group_id": "NewVoiceGroup",
  "extracted_files": ["file1.wav", "file2.wav"],
  "message": "角色组上传成功"
}
```

## 🎯 智能参考音频选择

BreathVOICE API 具有智能参考音频选择功能，会根据输入文本自动选择最合适的参考音频：

### 选择规则

1. **关键词匹配**: 优先匹配参考文件的关键词
2. **情绪识别**: 识别文本中的情绪标识（如 B1, B2, B3, B5）
3. **内容类型**: 识别问候语、对话等不同类型
4. **默认选择**: 如无匹配，使用第一个参考文件

### 示例

```python
# 这些文本会自动选择合适的参考音频
test_cases = [
    {
        "text": "你好，欢迎使用我们的服务！",  # 会选择 greeting 相关的参考音频
        "expected_reference": "ChineseWoman_greeting.wav"
    },
    {
        "text": "这是一个温和的 B1 情绪测试。",  # 会选择 B1 相关的参考音频
        "expected_reference": "ChineseWoman_B1_B2.wav"
    },
    {
        "text": "这是最激烈的 B5 情绪表达！",  # 会选择 B5 相关的参考音频
        "expected_reference": "ChineseWoman_B5_orgasm.wav"
    }
]

for case in test_cases:
    result = generate_speech("ChineseWoman", case["text"], "test.wav")
    print(f"文本: {case['text']}")
    print(f"选择的参考音频: {result['results'][0]['reference_file']}")
```

## 🛠️ 集成最佳实践

### 1. 错误处理

```python
def robust_tts_request(voice_group_id, text, filename, max_retries=3):
    """带重试机制的 TTS 请求"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    for attempt in range(max_retries):
        try:
            payload = {
                "voice_group_id": voice_group_id,
                "requests": [{"text": text, "filename": filename}]
            }
            
            response = requests.post(
                f"{base_url}/breathvoice/batch-tts",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                # 客户端错误，不重试
                print(f"请求错误: {response.text}")
                return None
            else:
                # 服务器错误，可以重试
                print(f"尝试 {attempt + 1} 失败: {response.status_code}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # 指数退避
                
        except requests.exceptions.Timeout:
            print(f"尝试 {attempt + 1} 超时")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)
            
        except Exception as e:
            print(f"尝试 {attempt + 1} 异常: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)
    
    return None
```

### 2. 批量处理优化

```python
def batch_tts_with_chunking(voice_group_id, text_list, chunk_size=5):
    """分块批量处理 TTS 请求"""
    base_url = "https://tts.ioioioioio.com:1120"
    all_results = []
    
    # 将文本列表分块
    for i in range(0, len(text_list), chunk_size):
        chunk = text_list[i:i + chunk_size]
        
        # 构建请求
        requests_data = []
        for j, text in enumerate(chunk):
            requests_data.append({
                "text": text,
                "filename": f"batch_{i + j + 1:03d}.wav"
            })
        
        payload = {
            "voice_group_id": voice_group_id,
            "requests": requests_data
        }
        
        try:
            response = requests.post(
                f"{base_url}/breathvoice/batch-tts",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                all_results.extend(result.get("results", []))
                print(f"✅ 处理块 {i//chunk_size + 1}: {result.get('successful_count', 0)} 成功")
            else:
                print(f"❌ 处理块 {i//chunk_size + 1} 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 处理块 {i//chunk_size + 1} 异常: {e}")
        
        # 避免过于频繁的请求
        time.sleep(1)
    
    return all_results
```

### 3. 异步处理

```python
import asyncio
import aiohttp

async def async_tts_request(session, voice_group_id, text, filename):
    """异步 TTS 请求"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    payload = {
        "voice_group_id": voice_group_id,
        "requests": [{"text": text, "filename": filename}]
    }
    
    try:
        async with session.post(
            f"{base_url}/breathvoice/batch-tts",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"HTTP {response.status}"}
                
    except Exception as e:
        return {"error": str(e)}

async def process_multiple_tts_requests(requests_list):
    """并发处理多个 TTS 请求"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for req in requests_list:
            task = async_tts_request(
                session,
                req["voice_group_id"],
                req["text"],
                req["filename"]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# 使用示例
requests_list = [
    {"voice_group_id": "ChineseWoman", "text": "文本1", "filename": "file1.wav"},
    {"voice_group_id": "ChineseWoman", "text": "文本2", "filename": "file2.wav"},
    {"voice_group_id": "ChineseWoman", "text": "文本3", "filename": "file3.wav"}
]

# results = asyncio.run(process_multiple_tts_requests(requests_list))
```

## 📊 性能特征

### 响应时间基准

| 操作 | 典型响应时间 | 最大响应时间 |
|------|-------------|-------------|
| 获取角色组列表 | < 1 秒 | 3 秒 |
| 获取角色组详情 | < 1 秒 | 3 秒 |
| 单个 TTS 请求 | 3-8 秒 | 15 秒 |
| 批量 TTS (5个) | 10-25 秒 | 45 秒 |

### 并发能力

- **推荐并发数**: 3-5 个请求
- **最大并发数**: 10 个请求
- **请求间隔**: 建议 1-2 秒

### 文件大小限制

- **单个文本长度**: 建议 < 500 字符
- **批量请求数量**: 建议 < 10 个
- **ZIP 文件大小**: < 100MB

## 🔍 调试和故障排除

### 常见问题

#### 1. 404 Not Found 错误

**问题**: 访问 BreathVOICE 端点返回 404

**解决方案**:
```python
# 检查服务是否正确部署
def check_breathvoice_deployment():
    base_url = "https://tts.ioioioioio.com:1120"
    
    # 检查 OpenAPI 文档
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            breathvoice_paths = [path for path in paths.keys() if "breathvoice" in path]
            
            if breathvoice_paths:
                print("✅ BreathVOICE 端点已部署:")
                for path in breathvoice_paths:
                    print(f"  - {path}")
            else:
                print("❌ BreathVOICE 端点未部署")
                print("请检查服务器上的 breathvoice_api.py 文件")
        
    except Exception as e:
        print(f"检查失败: {e}")

check_breathvoice_deployment()
```

#### 2. 超时错误

**问题**: 请求超时

**解决方案**:
```python
# 增加超时时间并添加重试机制
def tts_with_timeout_handling(voice_group_id, text, filename):
    base_url = "https://tts.ioioioioio.com:1120"
    
    payload = {
        "voice_group_id": voice_group_id,
        "requests": [{"text": text, "filename": filename}]
    }
    
    # 根据文本长度调整超时时间
    text_length = len(text)
    timeout = max(30, text_length * 0.1)  # 至少30秒，长文本增加时间
    
    try:
        response = requests.post(
            f"{base_url}/breathvoice/batch-tts",
            json=payload,
            timeout=timeout
        )
        return response.json()
        
    except requests.exceptions.Timeout:
        print(f"请求超时 (>{timeout}s)，请尝试:")
        print("1. 减少文本长度")
        print("2. 分批处理")
        print("3. 检查网络连接")
        return None
```

#### 3. 角色组不存在

**问题**: 指定的角色组不存在

**解决方案**:
```python
def validate_voice_group(voice_group_id):
    """验证角色组是否存在"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    try:
        # 获取所有可用角色组
        response = requests.get(f"{base_url}/breathvoice/voice-groups")
        if response.status_code == 200:
            available_groups = response.json().get("voice_groups", [])
            
            if voice_group_id in available_groups:
                print(f"✅ 角色组 '{voice_group_id}' 存在")
                return True
            else:
                print(f"❌ 角色组 '{voice_group_id}' 不存在")
                print(f"可用角色组: {available_groups}")
                return False
        else:
            print(f"无法获取角色组列表: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"验证失败: {e}")
        return False

# 使用前验证
if validate_voice_group("ChineseWoman"):
    # 继续处理
    pass
```

### 调试工具

```python
def debug_api_request(endpoint, method="GET", payload=None):
    """调试 API 请求"""
    base_url = "https://tts.ioioioioio.com:1120"
    
    print(f"🔍 调试请求: {method} {base_url}{endpoint}")
    
    if payload:
        print(f"📤 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{base_url}{endpoint}", json=payload)
        
        end_time = time.time()
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"⏱️ 响应时间: {end_time - start_time:.3f}s")
        print(f"📥 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"📄 响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"📄 响应文本: {response.text[:500]}...")
        else:
            print(f"❌ 错误响应: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

# 调试示例
debug_api_request("/breathvoice/voice-groups")
debug_api_request("/breathvoice/batch-tts", "POST", {
    "voice_group_id": "ChineseWoman",
    "requests": [{"text": "测试", "filename": "test.wav"}]
})
```

## 📈 监控和日志

### 请求日志记录

```python
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('breathvoice_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def logged_tts_request(voice_group_id, text, filename):
    """带日志记录的 TTS 请求"""
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    logger.info(f"[{request_id}] 开始 TTS 请求")
    logger.info(f"[{request_id}] 角色组: {voice_group_id}")
    logger.info(f"[{request_id}] 文本长度: {len(text)} 字符")
    logger.info(f"[{request_id}] 输出文件: {filename}")
    
    start_time = time.time()
    
    try:
        result = generate_speech(voice_group_id, text, filename)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result and result.get("successful_count", 0) > 0:
            logger.info(f"[{request_id}] ✅ 请求成功，耗时: {processing_time:.2f}s")
        else:
            logger.error(f"[{request_id}] ❌ 请求失败，耗时: {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.error(f"[{request_id}] ❌ 请求异常: {e}，耗时: {processing_time:.2f}s")
        return None
```

### 性能监控

```python
class APIPerformanceMonitor:
    """API 性能监控"""
    
    def __init__(self):
        self.request_times = []
        self.success_count = 0
        self.failure_count = 0
    
    def record_request(self, success: bool, response_time: float):
        """记录请求结果"""
        self.request_times.append(response_time)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_statistics(self):
        """获取统计信息"""
        if not self.request_times:
            return {"error": "没有请求记录"}
        
        return {
            "total_requests": len(self.request_times),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_count / len(self.request_times) * 100,
            "avg_response_time": statistics.mean(self.request_times),
            "min_response_time": min(self.request_times),
            "max_response_time": max(self.request_times),
            "median_response_time": statistics.median(self.request_times)
        }
    
    def print_report(self):
        """打印性能报告"""
        stats = self.get_statistics()
        
        if "error" in stats:
            print(stats["error"])
            return
        
        print("\n📊 API 性能报告")
        print("=" * 30)
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['success_count']}")
        print(f"失败请求: {stats['failure_count']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"最快响应时间: {stats['min_response_time']:.3f}s")
        print(f"最慢响应时间: {stats['max_response_time']:.3f}s")
        print(f"中位响应时间: {stats['median_response_time']:.3f}s")

# 使用示例
monitor = APIPerformanceMonitor()

# 在每次请求后记录
def monitored_tts_request(voice_group_id, text, filename):
    start_time = time.time()
    
    try:
        result = generate_speech(voice_group_id, text, filename)
        end_time = time.time()
        
        success = result and result.get("successful_count", 0) > 0
        monitor.record_request(success, end_time - start_time)
        
        return result
        
    except Exception as e:
        end_time = time.time()
        monitor.record_request(False, end_time - start_time)
        raise e

# 定期打印报告
# monitor.print_report()
```

## 🔐 安全考虑

### 输入验证

```python
def validate_tts_input(text: str, filename: str) -> tuple[bool, str]:
    """验证 TTS 输入"""
    
    # 文本验证
    if not text or not text.strip():
        return False, "文本不能为空"
    
    if len(text) > 1000:
        return False, "文本长度不能超过 1000 字符"
    
    # 检查可能的恶意内容
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "文本包含不安全内容"
    
    # 文件名验证
    if not filename or not filename.strip():
        return False, "文件名不能为空"
    
    if not filename.endswith('.wav'):
        return False, "文件名必须以 .wav 结尾"
    
    # 检查文件名安全性
    if re.search(r'[<>:"/\\|?*]', filename):
        return False, "文件名包含非法字符"
    
    if len(filename) > 100:
        return False, "文件名长度不能超过 100 字符"
    
    return True, "验证通过"

def safe_tts_request(voice_group_id, text, filename):
    """安全的 TTS 请求"""
    
    # 输入验证
    is_valid, message = validate_tts_input(text, filename)
    if not is_valid:
        return {"error": f"输入验证失败: {message}"}
    
    # 角色组验证
    if not validate_voice_group(voice_group_id):
        return {"error": f"无效的角色组: {voice_group_id}"}
    
    # 执行请求
    return generate_speech(voice_group_id, text, filename)
```

### 速率限制

```python
import time
from collections import defaultdict

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, max_requests_per_minute=10):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id="default"):
        """检查是否允许请求"""
        now = time.time()
        minute_ago = now - 60
        
        # 清理过期记录
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[client_id].append(now)
        return True
    
    def get_wait_time(self, client_id="default"):
        """获取需要等待的时间"""
        if not self.requests[client_id]:
            return 0
        
        oldest_request = min(self.requests[client_id])
        wait_time = 60 - (time.time() - oldest_request)
        return max(0, wait_time)

# 使用示例
rate_limiter = RateLimiter(max_requests_per_minute=5)

def rate_limited_tts_request(voice_group_id, text, filename, client_id="default"):
    """带速率限制的 TTS 请求"""
    
    if not rate_limiter.is_allowed(client_id):
        wait_time = rate_limiter.get_wait_time(client_id)
        return {
            "error": f"请求过于频繁，请等待 {wait_time:.1f} 秒后重试"
        }
    
    return generate_speech(voice_group_id, text, filename)
```

## 📚 完整示例项目

### 简单的 TTS 客户端

```python
#!/usr/bin/env python3
"""
BreathVOICE API 客户端示例
"""

import requests
import json
import time
import argparse
from typing import List, Dict, Optional

class BreathVOICEClient:
    """BreathVOICE API 客户端"""
    
    def __init__(self, base_url: str = "https://tts.ioioioioio.com:1120"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    def get_voice_groups(self) -> List[str]:
        """获取可用角色组"""
        try:
            response = self.session.get(f"{self.base_url}/breathvoice/voice-groups")
            if response.status_code == 200:
                return response.json().get("voice_groups", [])
            else:
                print(f"获取角色组失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"请求失败: {e}")
            return []
    
    def get_voice_group_details(self, voice_group_id: str) -> Optional[Dict]:
        """获取角色组详情"""
        try:
            response = self.session.get(f"{self.base_url}/breathvoice/voice-groups/{voice_group_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取角色组详情失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def generate_speech(self, voice_group_id: str, text: str, filename: str) -> Optional[Dict]:
        """生成语音"""
        payload = {
            "voice_group_id": voice_group_id,
            "requests": [{"text": text, "filename": filename}]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/breathvoice/batch-tts",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"生成语音失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def batch_generate_speech(self, voice_group_id: str, text_list: List[str]) -> Optional[Dict]:
        """批量生成语音"""
        requests_data = []
        for i, text in enumerate(text_list):
            requests_data.append({
                "text": text,
                "filename": f"batch_{i+1:03d}.wav"
            })
        
        payload = {
            "voice_group_id": voice_group_id,
            "requests": requests_data
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/breathvoice/batch-tts",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"批量生成失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"请求失败: {e}")
            return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="BreathVOICE API 客户端")
    parser.add_argument("--list-groups", action="store_true", help="列出所有角色组")
    parser.add_argument("--group-details", type=str, help="获取指定角色组的详情")
    parser.add_argument("--generate", nargs=3, metavar=("GROUP", "TEXT", "FILENAME"), 
                       help="生成语音: 角色组 文本 文件名")
    parser.add_argument("--batch-file", type=str, help="从文件批量生成语音")
    parser.add_argument("--voice-group", type=str, default="ChineseWoman", 
                       help="批量生成时使用的角色组")
    
    args = parser.parse_args()
    
    client = BreathVOICEClient()
    
    if args.list_groups:
        print("📋 获取角色组列表...")
        voice_groups = client.get_voice_groups()
        if voice_groups:
            print("可用角色组:")
            for group in voice_groups:
                print(f"  - {group}")
        else:
            print("未找到可用角色组")
    
    elif args.group_details:
        print(f"🔍 获取角色组 '{args.group_details}' 的详情...")
        details = client.get_voice_group_details(args.group_details)
        if details:
            print(json.dumps(details, ensure_ascii=False, indent=2))
        else:
            print("获取详情失败")
    
    elif args.generate:
        voice_group, text, filename = args.generate
        print(f"🎵 生成语音: {voice_group} -> {filename}")
        result = client.generate_speech(voice_group, text, filename)
        if result:
            print("生成结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("生成失败")
    
    elif args.batch_file:
        print(f"📁 从文件批量生成语音: {args.batch_file}")
        try:
            with open(args.batch_file, 'r', encoding='utf-8') as f:
                text_list = [line.strip() for line in f if line.strip()]
            
            if text_list:
                result = client.batch_generate_speech(args.voice_group, text_list)
                if result:
                    print("批量生成结果:")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print("批量生成失败")
            else:
                print("文件为空或无有效文本")
                
        except FileNotFoundError:
            print(f"文件不存在: {args.batch_file}")
        except Exception as e:
            print(f"读取文件失败: {e}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

### 使用示例

```bash
# 列出所有角色组
python breathvoice_client.py --list-groups

# 获取角色组详情
python breathvoice_client.py --group-details ChineseWoman

# 生成单个语音
python breathvoice_client.py --generate ChineseWoman "你好，这是一个测试。" test.wav

# 从文件批量生成
echo -e "第一个测试文本\n第二个测试文本\n第三个测试文本" > texts.txt
python breathvoice_client.py --batch-file texts.txt --voice-group ChineseWoman
```

## 📞 技术支持

### 联系方式

- **API 文档**: `https://tts.ioioioioio.com:1120/docs`
- **OpenAPI 规范**: `https://tts.ioioioioio.com:1120/openapi.json`

### 常见问题 FAQ

**Q: API 是否需要认证？**
A: 当前版本不需要认证，可以直接访问。

**Q: 支持哪些音频格式？**
A: 目前只支持 WAV 格式输出。

**Q: 单次请求的文本长度限制是多少？**
A: 建议单个文本不超过 500 字符，以确保最佳性能。

**Q: 是否支持自定义角色组？**
A: 支持，可以通过 `/breathvoice/upload-voice-group` 端点上传 ZIP 格式的角色组。

**Q: 如何选择合适的参考音频？**
A: API 具有智能选择功能，会根据文本内容自动选择最合适的参考音频。

## 📋 检查清单

在开始集成之前，请确认以下事项：

### 环境准备
- [ ] Python 3.7+ 或 Node.js 14+
- [ ] 安装 requests 库 (Python) 或 fetch API (JavaScript)
- [ ] 网络可以访问 `https://tts.ioioioioio.com:1120`

### API 验证
- [ ] 能够访问 `/` 端点
- [ ] 能够访问 `/breathvoice/voice-groups` 端点
- [ ] 能够获取角色组列表
- [ ] 能够成功生成测试语音

### 集成准备
- [ ] 了解智能参考音频选择机制
- [ ] 实现错误处理和重试逻辑
- [ ] 考虑批量处理和性能优化
- [ ] 添加日志记录和监控

### 测试验证
- [ ] 运行基础连通性测试
- [ ] 验证各种文本类型的处理
- [ ] 测试错误情况的处理
- [ ] 进行性能基准测试

---

**🎉 恭喜！您现在拥有了完整的 BreathVOICE API 集成资源包。**

这个资料包包含了成功集成 BreathVOICE API 所需的所有信息、工具和最佳实践。如果在集成过程中遇到任何问题，请参考调试部分或使用提供的测试工具进行诊断。