# BreathVOICE API 资料包

## 📋 概述

这是 BreathVOICE API 的完整开发者资料包，为其他 AI 助手和开发者提供集成 BreathVOICE 服务所需的所有资源。

**API 服务地址**: `https://tts.ioioioioio.com:1120`

## 📁 资料包结构

```
breathVOICE_API/
├── README.md                           # 本文件 - 资料包说明
├── Developer_Resource_Package.md       # 🌟 完整开发者资料包 (推荐首先阅读)
├── BreathVOICE_API_Documentation.md    # API 完整文档
├── API_Integration_Guide.md            # 集成指南和最佳实践
├── API_Usability_Testing.md           # 可用性测试指南
├── test_breathvoice_api.py            # API 测试脚本
├── BreathVOICE_Implementation_Summary.md # 实现总结
├── External_API_Test_Report.md        # 外部 API 测试报告
└── deploy_breathvoice_to_external.md  # 部署指南
```

## 🚀 快速开始

### 1. 首先阅读完整资料包
**推荐从这里开始**: [`Developer_Resource_Package.md`](./Developer_Resource_Package.md)

这个文档包含了：
- 完整的 API 使用指南
- 代码示例 (Python, JavaScript, cURL)
- 最佳实践和性能优化
- 错误处理和调试工具
- 安全考虑和监控方案

### 2. 运行连通性测试

```python
import requests

# 快速验证 API 可用性
def quick_test():
    base_url = "https://tts.ioioioioio.com:1120"
    
    try:
        # 测试基础连通性
        response = requests.get(f"{base_url}/")
        print(f"服务状态: {response.status_code}")
        
        # 测试 BreathVOICE 端点
        response = requests.get(f"{base_url}/breathvoice/voice-groups")
        if response.status_code == 200:
            voice_groups = response.json()
            print(f"✅ BreathVOICE API 可用，发现 {len(voice_groups.get('voice_groups', []))} 个角色组")
            return True
        else:
            print(f"❌ BreathVOICE 端点不可用: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

# 运行测试
if quick_test():
    print("🎉 可以开始集成 BreathVOICE API！")
else:
    print("⚠️ 请检查网络连接或联系技术支持")
```

### 3. 使用测试脚本

运行提供的测试脚本：

```bash
python test_breathvoice_api.py
```

## 📚 文档说明

### 核心文档

1. **[Developer_Resource_Package.md](./Developer_Resource_Package.md)** 🌟
   - **最重要的文档，建议首先阅读**
   - 包含完整的集成指南、代码示例、最佳实践
   - 涵盖错误处理、性能优化、安全考虑

2. **[BreathVOICE_API_Documentation.md](./BreathVOICE_API_Documentation.md)**
   - 详细的 API 端点文档
   - 请求/响应格式说明
   - 参数详细说明

3. **[API_Integration_Guide.md](./API_Integration_Guide.md)**
   - 集成步骤和最佳实践
   - 多语言代码示例
   - 性能优化建议

### 测试和验证

4. **[API_Usability_Testing.md](./API_Usability_Testing.md)**
   - 完整的测试计划
   - 自动化测试脚本
   - 性能基准测试

5. **[test_breathvoice_api.py](./test_breathvoice_api.py)**
   - 可执行的测试脚本
   - 包含所有端点的测试用例
   - 错误处理示例

### 技术参考

6. **[BreathVOICE_Implementation_Summary.md](./BreathVOICE_Implementation_Summary.md)**
   - 技术实现总结
   - 功能特性说明
   - 架构概览

7. **[External_API_Test_Report.md](./External_API_Test_Report.md)**
   - 外部 API 测试结果
   - 已知问题和解决方案
   - 部署状态说明

8. **[deploy_breathvoice_to_external.md](./deploy_breathvoice_to_external.md)**
   - 部署指南（供参考）
   - 故障排除步骤
   - 服务器配置说明

## 🎯 核心 API 端点

### 1. 获取角色组列表
```
GET /breathvoice/voice-groups
```

### 2. 获取角色组详情
```
GET /breathvoice/voice-groups/{voice_group_id}
```

### 3. 批量 TTS 生成
```
POST /breathvoice/batch-tts
```

### 4. 上传角色组
```
POST /breathvoice/upload-voice-group
```

## 🔧 智能特性

### 智能参考音频选择
BreathVOICE API 具有智能参考音频选择功能：

- **关键词匹配**: 根据文本内容自动选择合适的参考音频
- **情绪识别**: 识别 B1, B2, B3, B5 等情绪标识
- **内容类型**: 区分问候语、对话等不同场景

### 示例
```python
# 这些文本会自动选择不同的参考音频
texts = [
    "你好，欢迎使用我们的服务！",      # 选择 greeting 相关音频
    "这是一个温和的 B1 情绪测试。",    # 选择 B1 相关音频
    "这是最激烈的 B5 情绪表达！"       # 选择 B5 相关音频
]
```

## ⚡ 性能特征

| 操作 | 典型响应时间 | 建议并发数 |
|------|-------------|-----------|
| 获取角色组列表 | < 1 秒 | 不限 |
| 单个 TTS 请求 | 3-8 秒 | 3-5 个 |
| 批量 TTS (5个) | 10-25 秒 | 2-3 个 |

## 🛠️ 集成建议

### 对于 AI 助手开发者

1. **首先阅读** [`Developer_Resource_Package.md`](./Developer_Resource_Package.md)
2. **运行测试脚本** 验证 API 可用性
3. **参考代码示例** 实现基础功能
4. **添加错误处理** 确保稳定性
5. **实施性能优化** 提升用户体验

### 关键注意事项

- ✅ 使用智能参考音频选择功能
- ✅ 实现重试机制和错误处理
- ✅ 考虑批量处理优化性能
- ✅ 添加请求日志和监控
- ⚠️ 注意并发请求限制
- ⚠️ 验证输入文本安全性

## 🔍 故障排除

### 常见问题

1. **404 Not Found**: BreathVOICE 服务未部署
   - 检查 `/openapi.json` 中是否包含 breathvoice 端点

2. **请求超时**: 文本过长或服务器负载高
   - 减少文本长度或分批处理

3. **角色组不存在**: 指定的角色组 ID 无效
   - 先调用 `/breathvoice/voice-groups` 获取可用列表

### 调试工具

资料包中提供了完整的调试工具和监控脚本，详见 [`Developer_Resource_Package.md`](./Developer_Resource_Package.md)。

## 📞 技术支持

- **API 文档**: `https://tts.ioioioioio.com:1120/docs`
- **OpenAPI 规范**: `https://tts.ioioioioio.com:1120/openapi.json`

## 📋 集成检查清单

- [ ] 阅读完整开发者资料包
- [ ] 运行连通性测试
- [ ] 验证角色组可用性
- [ ] 实现基础 TTS 功能
- [ ] 添加错误处理
- [ ] 进行性能测试
- [ ] 实施监控和日志

---

**🎉 开始您的 BreathVOICE API 集成之旅！**

建议从 [`Developer_Resource_Package.md`](./Developer_Resource_Package.md) 开始，这个文档包含了成功集成所需的所有信息。