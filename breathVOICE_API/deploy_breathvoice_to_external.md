# breathVOICE 扩展外网部署指南

## 概述

本指南详细说明如何将 breathVOICE API 扩展部署到外网服务器 `https://tts.ioioioioio.com:1120`。

### 当前问题

外网服务器运行的是**不包含 breathVOICE 扩展的旧版本代码**，需要进行代码同步和部署。

## 需要部署的文件

### 核心文件（必需）

```
breathvoice_api.py                    # breathVOICE 核心模块
openai_tts_api.py                    # 已集成 breathVOICE 的主API服务器
```

### 示例数据（推荐）

```
examples/ChineseWoman_Reference/     # 示例角色组数据
├── ChineseWoman_greeting.wav
├── ChineseWoman_B1_B2.wav
├── ChineseWoman_B3_B4.wav
└── ChineseWoman_B5_orgasm.wav
```

### 文档文件（可选）

```
BreathVOICE_API_Documentation.md     # API 文档
BreathVOICE_Implementation_Summary.md # 实现总结
test_breathvoice_api.py              # 测试脚本
```

## 部署步骤

### 步骤 1: 准备部署文件

在本地准备所有需要上传的文件：

```bash
# 创建部署目录
mkdir breathvoice_deployment
cd breathvoice_deployment

# 复制核心文件
cp ../breathvoice_api.py .
cp ../openai_tts_api.py .

# 复制示例数据
cp -r ../examples/ChineseWoman_Reference .

# 复制文档（可选）
cp ../BreathVOICE_API_Documentation.md .
cp ../test_breathvoice_api.py .

# 验证文件
ls -la breathvoice_api.py
ls -la openai_tts_api.py
ls -la ChineseWoman_Reference/
```

### 步骤 2: 上传文件到服务器

#### 方法 A: 使用 SCP

```bash
# 上传核心文件
scp breathvoice_api.py user@server:/path/to/indextts/
scp openai_tts_api.py user@server:/path/to/indextts/

# 上传示例数据
scp -r ChineseWoman_Reference user@server:/path/to/indextts/examples/
```

#### 方法 B: 使用 SFTP

```bash
sftp user@server
put breathvoice_api.py /path/to/indextts/
put openai_tts_api.py /path/to/indextts/
put -r ChineseWoman_Reference /path/to/indextts/examples/
quit
```

### 步骤 3: 服务器端配置

登录到外网服务器并执行以下操作：

```bash
# 1. 进入项目目录
cd /path/to/indextts/

# 2. 验证文件上传成功
ls -la breathvoice_api.py
ls -la openai_tts_api.py
ls -la examples/ChineseWoman_Reference/

# 3. 设置文件权限
chmod 644 breathvoice_api.py
chmod 644 openai_tts_api.py
chmod -R 644 examples/ChineseWoman_Reference/

# 4. 检查Python依赖
python -c "import requests, zipfile, os, json"
```

### 步骤 4: 重启服务

根据服务器的具体配置，重启 TTS API 服务：

#### 方法 A: 使用 systemd

```bash
sudo systemctl restart indextts-api
sudo systemctl status indextts-api
```

#### 方法 B: 使用 PM2

```bash
pm2 restart indextts-api
pm2 status
```

#### 方法 C: 手动重启

```bash
# 停止现有进程
pkill -f "openai_tts_api.py"

# 启动新进程
nohup python openai_tts_api.py --port 1120 > tts_api.log 2>&1 &
```

### 步骤 5: 验证部署

#### 5.1 基础连通性测试

```bash
# 测试服务器是否响应
curl -X GET "https://tts.ioioioioio.com:1120/"

# 测试 OpenAI API
curl -X GET "https://tts.ioioioioio.com:1120/v1/models"
```

#### 5.2 breathVOICE 端点测试

```bash
# 测试 breathVOICE 端点
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups"

# 测试角色组详情
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups/ChineseWoman"
```

#### 5.3 OpenAPI 规范检查

```bash
# 检查是否包含 breathVOICE 端点
curl -X GET "https://tts.ioioioioio.com:1120/openapi.json" | grep -i breathvoice
```

## 功能测试

### 使用测试脚本

```bash
# 上传测试脚本
scp test_breathvoice_api.py user@server:/path/to/indextts/

# 在服务器上运行测试
python test_breathvoice_api.py
```

### 手动功能测试

```bash
# 1. 测试角色组列表
curl -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups"

# 2. 测试批量TTS
curl -X POST "https://tts.ioioioioio.com:1120/breathvoice/batch-tts" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_group_id": "ChineseWoman",
    "requests": [
      {
        "text": "测试文本",
        "filename": "test_output.wav"
      }
    ]
  }'
```

## 故障排除

### 常见问题

#### 问题 1: ModuleNotFoundError

```bash
# 错误: ModuleNotFoundError: No module named 'breathvoice_api'
# 解决: 确保 breathvoice_api.py 在正确路径
ls -la breathvoice_api.py
```

#### 问题 2: 权限错误

```bash
# 错误: Permission denied
# 解决: 检查文件权限
chmod 644 breathvoice_api.py
chmod 644 openai_tts_api.py
```

#### 问题 3: 端口占用

```bash
# 错误: Address already in use
# 解决: 停止现有进程
lsof -i :1120
kill -9 <PID>
```

#### 问题 4: 依赖缺失

```bash
# 错误: ImportError
# 解决: 安装缺失的依赖
pip install requests zipfile-deflate64
```

## 部署验证清单

### 部署前检查

- [ ] 本地 breathVOICE 功能正常工作
- [ ] 所有必需文件已准备
- [ ] 服务器访问权限确认
- [ ] 备份现有配置

### 部署后验证

- [ ] 文件上传成功
- [ ] 文件权限正确
- [ ] 服务重启成功
- [ ] breathVOICE 端点返回 200 状态码
- [ ] 角色组列表正常返回
- [ ] 批量TTS功能正常
- [ ] OpenAPI 规范包含新端点

## 回滚计划

如果部署出现问题，可以快速回滚：

```bash
# 1. 停止服务
sudo systemctl stop indextts-api

# 2. 移除新文件
rm breathvoice_api.py

# 3. 恢复原始文件
cp openai_tts_api.py.backup openai_tts_api.py

# 4. 重启服务
sudo systemctl start indextts-api
```

## 监控和维护

### 健康检查

```bash
# 定期检查 breathVOICE API 健康状态
curl -f -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups" || exit 1
echo "breathVOICE API is healthy"
```

### 日志监控

```bash
# 监控API日志
tail -f /var/log/indextts/api.log | grep -i breathvoice
```

### 性能监控

```bash
# 监控API响应时间
curl -w "@curl-format.txt" -X GET "https://tts.ioioioioio.com:1120/breathvoice/voice-groups"
```

## 安全考虑

1. **文件权限**: 确保敏感文件权限设置正确
2. **网络安全**: 考虑添加防火墙规则
3. **API认证**: 为生产环境添加认证机制
4. **输入验证**: 确保所有输入都经过验证

## 总结

完成以上步骤后，breathVOICE API 扩展将在外网服务器 `https://tts.ioioioioio.com:1120` 上正常工作。

**关键成功因素**:
1. 确保所有文件正确上传
2. 服务器重启成功
3. 依赖包完整安装
4. 权限配置正确

**验证标准**:
- 所有 breathVOICE 端点返回 200 状态码
- 功能测试全部通过
- OpenAPI 规范包含新端点

---

**注意**: 部署完成后请运行完整的功能测试以确保所有功能正常工作。