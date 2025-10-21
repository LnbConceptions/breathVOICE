# breathVOICE Nginx 反向代理部署指南

## 问题描述

在使用 Nginx 反向代理部署 breathVOICE 时，可能会遇到以下问题：
1. 角色图片无法加载
2. 选择台词集功能卡死
3. manifest.json 404 错误
4. 静态文件路径错误

## 解决方案

### 1. 修改 breathVOICE 配置

项目已经更新了以下配置以支持反向代理：

- **app.py**: 添加了 `root_path` 和 `file_directories` 参数
- **启动脚本**: 添加了 `GRADIO_ROOT_PATH` 环境变量
- **manifest.json**: 添加了 PWA 清单文件

### 2. 环境变量配置

在部署时，需要设置以下环境变量：

```bash
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT=7866
export GRADIO_ROOT_PATH=""  # 如果使用子路径，设置为对应路径，如 "/breathvoice"
```

### 3. Nginx 配置

使用提供的 `nginx.conf.example` 作为参考，关键配置包括：

#### 处理 Gradio API 路径
```nginx
location /gradio_api/ {
    proxy_pass http://127.0.0.1:7866/gradio_api/;
    # ... 其他代理设置
}
```

#### 处理文件上传下载
```nginx
location /file= {
    proxy_pass http://127.0.0.1:7866/file=;
    # ... 其他代理设置
}
```

#### 处理 manifest.json
```nginx
location /manifest.json {
    proxy_pass http://127.0.0.1:7866/manifest.json;
    add_header Content-Type application/json;
}
```

### 4. 部署步骤

1. **更新代码**：确保使用最新版本的 breathVOICE
2. **配置 Nginx**：使用 `nginx.conf.example` 作为模板
3. **设置环境变量**：根据你的部署环境设置正确的环境变量
4. **重启服务**：重启 breathVOICE 和 Nginx 服务
5. **测试功能**：验证角色选择、图片加载和台词集功能

### 5. 常见问题排查

#### 图片无法加载
- 检查 Nginx 是否正确代理 `/gradio_api/` 路径
- 确认 `file_directories` 参数包含了正确的路径
- 检查文件权限

#### 台词集功能卡死
- 检查 WebSocket 连接是否正常
- 确认 Nginx 配置中包含了 WebSocket 支持
- 检查代理超时设置

#### manifest.json 404
- 确认项目根目录包含 `manifest.json` 文件
- 检查 Nginx 配置中的 manifest.json 路径

### 6. 测试命令

```bash
# 测试主页访问
curl -I https://voice.ioioioioio.com:1120/

# 测试 manifest.json
curl -I https://voice.ioioioioio.com:1120/manifest.json

# 测试 API 路径
curl -I https://voice.ioioioioio.com:1120/gradio_api/
```

## 注意事项

1. 确保 SSL 证书配置正确
2. 调整 `client_max_body_size` 以支持大文件上传
3. 设置合适的代理超时时间
4. 定期检查日志文件排查问题