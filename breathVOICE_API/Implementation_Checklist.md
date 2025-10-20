# BreathVOICE 逐条TTS生成功能实现清单

## 📋 实现概述
本文档为BreathVOICE TTS API开发者提供了实现逐条TTS生成功能的详细清单。

## 🎯 核心需求
基于WebUI的需求，需要将现有的批量TTS生成改为逐条生成模式，支持：
- 逐条发送TTS请求并生成音频
- 实时状态更新和播放控件显示
- 停止生成功能（完成当前任务后停止）

## ✅ 已完成的文档更新

### 1. API文档更新
- ✅ **BreathVOICE_API_Documentation.md**: 添加了 `/breathvoice/single-tts` 接口规范
- ✅ **API_Integration_Guide.md**: 添加了单条TTS生成的集成指南和工作流示例
- ✅ **Developer_Resource_Package.md**: 添加了单条TTS和逐条生成的Python示例代码
- ✅ **Sequential_TTS_Requirements.md**: 创建了详细的需求规范文档
- ✅ **test_breathvoice_api.py**: 添加了单条TTS和逐条生成的测试函数

## 🔧 需要实现的API功能

### 1. 新增API端点
```
POST /breathvoice/single-tts
```

**功能要求：**
- 接收单个TTS请求
- 支持与批量TTS相同的参数格式
- 返回单个音频文件的base64编码
- 保持与现有批量接口的兼容性

### 2. 请求体格式
```json
{
    "voice_group_id": "string",
    "text": "string", 
    "filename": "string",
    "reference_audio": "string (可选)"
}
```

### 3. 响应格式
```json
{
    "success": true,
    "audio_data": "base64编码的WAV文件",
    "filename": "生成的文件名",
    "voice_group_id": "使用的角色组ID",
    "reference_audio": "实际使用的参考音频",
    "processing_time": 1.23
}
```

## 🚀 实现优先级

### 高优先级 (P0)
1. **实现 `/breathvoice/single-tts` 接口**
   - 复用现有的TTS生成逻辑
   - 将单个请求包装成批量请求格式
   - 返回单个结果

2. **参考音频智能选择**
   - 复用批量TTS的智能选择逻辑
   - 确保单条生成的参考音频选择一致性

3. **错误处理**
   - 统一的错误响应格式
   - 详细的错误信息返回

### 中优先级 (P1)
1. **性能优化**
   - 单条请求的响应时间控制在3秒内
   - 内存使用优化

2. **日志记录**
   - 单条TTS请求的详细日志
   - 便于调试和监控

### 低优先级 (P2)
1. **扩展功能**
   - 支持更多音频格式输出
   - 批量和单条接口的统一管理

## 🧪 测试要求

### 1. 功能测试
- ✅ 单条TTS生成测试函数已准备
- ✅ 逐条生成工作流测试函数已准备
- ✅ 集成到主测试流程

### 2. 性能测试
- 单条请求响应时间测试
- 并发请求处理能力测试
- 内存使用情况监控

### 3. 兼容性测试
- 与现有批量TTS接口的兼容性
- 不同参数组合的测试
- 错误场景的处理测试

## 📁 相关文件

### 核心文档
- `BreathVOICE_API_Documentation.md` - API接口文档
- `Sequential_TTS_Requirements.md` - 详细需求规范
- `API_Integration_Guide.md` - 集成指南

### 开发资源
- `Developer_Resource_Package.md` - 开发者资源包
- `test_breathvoice_api.py` - 测试脚本

### 实现指南
- `Implementation_Checklist.md` - 本文档

## 🎯 预期效果

实现后，WebUI将能够：
1. 逐条发送TTS请求到 `/breathvoice/single-tts`
2. 收到每个音频文件后立即显示播放控件
3. 支持用户随时停止生成流程
4. 提供实时的生成状态反馈

## 📞 技术支持

如有实现过程中的问题，请参考：
1. `Sequential_TTS_Requirements.md` - 详细需求说明
2. `test_breathvoice_api.py` - 测试用例和示例
3. `API_Integration_Guide.md` - 集成指南和最佳实践

---
**文档版本**: 1.0  
**创建日期**: 2024年  
**最后更新**: 2024年