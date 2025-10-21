# breathVOICE：个性化角色语音定制系统

<div align="center">

![breathVOICE Logo](https://img.shields.io/badge/breathVOICE-个性化语音定制-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Gradio](https://img.shields.io/badge/Gradio-WebUI-orange?style=for-the-badge&logo=gradio)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

**一个完整的个性化角色语音定制系统，支持角色创建、台词生成、语音合成和语音包导出**

</div>

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [安装步骤](#安装步骤)
  - [启动项目](#启动项目)
- [功能模块详解](#功能模块详解)
  - [步骤一：角色管理](#步骤一角色管理)
  - [步骤二：LLM配置](#步骤二llm配置)
  - [步骤三：台词生成](#步骤三台词生成)
  - [步骤四：语音生成](#步骤四语音生成)
  - [步骤五：导出语音包](#步骤五导出语音包)
- [API集成](#api集成)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🎯 项目简介

breathVOICE 是一个专为硅胶娃娃厂商和最终用户设计的个性化角色语音定制系统。该系统能够配合智能硅胶娃娃的感应组件，根据用户的互动动作（抽插、体位、触摸等）实现智能化的语音反馈。

### 🎭 应用场景

- **硅胶娃娃厂商**：为产品定制专属角色语音包
- **最终用户**：创建个性化的角色语音体验
- **内容创作者**：批量生成角色对话内容
- **语音合成研究**：测试和验证TTS模型效果

## ✨ 核心特性

### 🎪 完整的工作流程
- **步骤化操作**：五步完整流程，从角色创建到语音包导出
- **可视化界面**：基于Gradio的现代化Web界面
- **实时预览**：台词生成和语音合成过程实时显示

### 🎨 角色管理系统
- **多角色支持**：创建和管理多个虚拟角色
- **角色信息**：名称、描述、头像等完整信息
- **数据持久化**：SQLite数据库存储角色数据

### 🤖 智能台词生成
- **LLM集成**：支持OpenAI兼容的API接口
- **多语言支持**：中文、英文、日文台词生成
- **动态更新**：实时显示生成进度和结果
- **手动编辑**：支持台词的手动修改和重新生成

### 🎵 高质量语音合成
- **GPT-SoVITS集成**：支持高质量的语音合成
- **多音色选择**：预训练的VoiceID选择
- **参考音频**：可选的参考音频上传
- **批量处理**：自动化的批量语音生成

### 📦 语音包导出
- **标准格式**：48KHz, 16bit, 单声道WAV格式
- **分类整理**：按动作类型自动分类文件夹
- **一键打包**：自动压缩为ZIP文件供下载

## 🏗️ 技术架构

### 核心技术栈
- **前端界面**：Gradio WebUI
- **后端语言**：Python 3.8+
- **数据库**：SQLite
- **语音合成**：GPT-SoVITS 2 Pro
- **LLM集成**：OpenAI兼容API

### 主要依赖
```
gradio          # Web界面框架
openai          # LLM API客户端
pandas          # 数据处理
soundfile       # 音频文件处理
numpy           # 数值计算
tqdm            # 进度条显示
requests        # HTTP请求
Pillow          # 图像处理
```

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10+, macOS 10.15+, Linux
- **Python版本**：3.8 或更高版本
- **内存要求**：建议 8GB 以上
- **存储空间**：建议 10GB 以上可用空间
- **依赖库**：详见 requirements.txt

### 核心依赖

项目主要依赖以下Python库：
- **gradio** (>=5.0.0)：Web界面框架
- **openai**：LLM API客户端
- **pandas**：数据处理
- **soundfile**：音频文件处理
- **numpy**：数值计算
- **tqdm**：进度条显示
- **requests**：HTTP请求
- **Pillow**：图像处理

### 安装步骤

#### 方法一：自动安装（推荐）

**Windows用户**：
1. 下载项目到本地
2. 双击运行 `start_breathVOICE.bat`
3. 脚本会自动检查环境并安装依赖
4. 启动完成后访问 `http://localhost:7866`

**macOS/Linux用户**：
1. 下载项目到本地
2. 运行 `Start breathVOICE.command`（macOS）
3. 或手动执行以下命令：

```bash
# 克隆项目
git clone https://github.com/LnbConceptions/breathVOICE.git
cd breathVOICE

# 安装依赖
pip install -r requirements.txt

# 启动项目
python app.py
```

#### 方法二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/LnbConceptions/breathVOICE.git
cd breathVOICE

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动项目
python app.py
```

### 启动项目

项目启动后，在浏览器中访问：
```
http://localhost:7866
```

默认端口为 7866，可通过环境变量 `GRADIO_SERVER_PORT` 修改。

## 📚 功能模块详解

### 步骤一：角色管理

#### 功能概述
角色管理是整个系统的基础，用户可以创建和管理多个虚拟角色。

#### 操作步骤
1. **创建新角色**
   - 输入角色名称（必填）
   - 输入角色描述（必填）
   - 上传角色头像（可选）
   - 点击"创建角色"按钮

2. **管理现有角色**
   - 查看角色列表
   - 编辑角色信息
   - 删除不需要的角色
   - 选择角色进入下一步

#### 注意事项
- 角色名称必须唯一
- 角色描述将影响后续台词生成的风格
- 头像支持常见图片格式（JPG, PNG, GIF等）

### 步骤二：LLM配置

#### 功能概述
配置大语言模型API，用于后续的台词生成功能。

#### 操作步骤
1. **添加API配置**
   - 输入API URL（必须以"/v1"结尾）
   - 输入API Key
   - 系统自动获取可用模型列表
   - 选择要使用的模型

2. **测试配置**
   - 点击"测试连接"验证配置
   - 查看测试结果和响应时间

3. **管理配置**
   - 保存多个API配置
   - 切换不同的配置组合
   - 编辑或删除现有配置

#### 支持的API服务
- OpenAI官方API
- Azure OpenAI
- 其他OpenAI兼容的API服务
- 本地部署的LLM服务

### 步骤三：台词生成

#### 功能概述
基于选定的角色和LLM配置，自动生成符合角色特征的台词内容。

#### 操作步骤
1. **选择生成参数**
   - 选择目标角色
   - 选择LLM配置
   - 选择台词语言（中文/英文/日文）

2. **生成台词**
   - 点击"开始生成"
   - 实时查看生成进度
   - 观察LLM通讯状态

3. **编辑和管理**
   - 在表格中直接编辑台词
   - 选择特定台词重新生成
   - 保存为CSV文件
   - 导入外部CSV文件

#### 台词分类
系统预设了以下台词类别：
- **greeting**：问候语
- **reaction**：反应台词
- **tease**：调情台词
- **impact**：冲击反应
- **touch**：触摸反应
- **orgasm**：高潮台词

#### 文件管理
- 自动创建角色专属文件夹
- CSV文件按时间戳命名
- 支持多版本台词管理
- 可导入导出台词文件

### 步骤四：语音生成

#### 功能概述
将台词文本转换为高质量的语音文件，支持多种音色和参数调节。

#### 操作步骤
1. **选择语音参数**
   - 选择预训练的VoiceID
   - 上传参考音频（可选）
   - 调整语音生成参数

2. **批量生成**
   - 系统自动创建任务队列
   - 实时显示生成进度
   - 逐条生成语音文件

3. **预览和调整**
   - 点击播放预览生成的语音
   - 对不满意的结果重新生成
   - 调整参数优化效果

#### 技术特性
- **高质量输出**：基于GPT-SoVITS的先进TTS技术
- **多音色支持**：丰富的预训练音色库
- **参数可调**：语速、音调、情感等参数
- **批量处理**：自动化的批量生成流程

### 步骤五：导出语音包

#### 功能概述
将生成的语音文件整理打包，形成标准格式的语音包供下载使用。系统已优化导出流程，确保高效稳定的批量处理。

#### 操作步骤
1. **确认语音文件**
   - 检查所有必需的语音文件
   - 确认文件质量和完整性

2. **导出设置**
   - 选择导出格式（默认48KHz, 16bit, 单声道WAV）
   - 确认文件命名规则

3. **打包下载**
   - 系统自动整理文件结构
   - 创建分类文件夹
   - 实时显示导出进度
   - 压缩为ZIP文件
   - 自动开始下载

#### 技术改进
- **优化进度显示**：统一的三参数进度回调格式 `(current, total, message)`
- **错误处理**：完善的异常捕获和错误报告
- **依赖优化**：移除scipy依赖，使用numpy进行音频处理
- **兼容性增强**：支持多种音频格式和采样率

#### 输出结构
```
角色名称/
├── greeting/     # 问候语音文件
├── reaction/     # 反应语音文件
├── tease/        # 调情语音文件
├── impact/       # 冲击语音文件
├── touch/        # 触摸语音文件
└── orgasm/       # 高潮语音文件
```

## 🔌 API集成

### 外部API支持

项目支持集成多种外部API服务：

#### LLM API集成
- **OpenAI官方API**：支持GPT-3.5/GPT-4等模型
- **Azure OpenAI**：企业级OpenAI服务
- **兼容API**：支持其他OpenAI兼容的API服务
- **本地LLM**：支持本地部署的大语言模型

#### TTS API集成
- **GPT-SoVITS**：高质量语音合成服务
- **自定义TTS**：支持其他TTS服务接入

### API配置示例

```python
# LLM API配置示例
llm_config = {
    "api_url": "https://api.openai.com/v1",
    "api_key": "your-api-key",
    "model": "gpt-3.5-turbo"
}

# TTS API配置示例  
tts_config = {
    "api_url": "http://localhost:9880",
    "voice_id": "your-voice-id"
}
```

## 📁 项目结构

```
breathVOICE/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖列表
├── requirements_build.txt       # 构建依赖列表
├── requirements_compatible.txt  # 兼容性依赖列表
├── start_breathVOICE.bat       # Windows启动脚本
├── Start breathVOICE.command   # macOS启动脚本
├── start.sh                    # Linux启动脚本
├── build_windows_exe.bat       # Windows EXE打包脚本
├── build_exe.py                # EXE打包工具
├── app.py                      # 主应用程序
├── app_simple.py               # 简化版应用
├── app_standalone.py           # 独立版应用
├── app_csv_editor.py           # CSV编辑器应用
├── database.py                 # 数据库操作
├── file_manager.py             # 文件管理
├── dialogue_generator.py       # 台词生成器
├── voice_pack_exporter.py      # 语音包导出器
├── action_parameters.py        # 动作参数定义
├── csv_parameter_loader.py     # CSV参数加载器
├── fix_gradio_compatibility.py # Gradio兼容性修复
├── voice_outputs/              # 语音输出目录
├── avatars/                    # 角色头像目录
├── assets/                     # 静态资源
│   ├── character_card.css      # 角色卡片样式
│   └── character_grid.js       # 角色网格脚本
├── static/                     # 静态文件
├── docs/                       # 开发文档
├── snapshots/                  # 项目快照
├── 存档/                       # 历史存档
├── Windows_EXE_打包指南.md      # Windows打包指南
├── deployment_guide.md         # 部署指南
├── data_structure_design.md    # 数据结构设计
└── voice_pack.db               # 语音包数据库
```

## 🛠️ 开发指南

### 本地开发环境搭建

1. **Fork项目**
```bash
git clone https://github.com/your-username/breathVOICE.git
cd breathVOICE
```

2. **创建开发分支**
```bash
git checkout -b feature/your-feature-name
```

3. **安装开发依赖**
```bash
pip install -r requirements.txt
```

4. **启动开发服务器**
```bash
python app.py
```

### 代码规范

- 使用Python PEP 8编码规范
- 函数和类需要添加详细的文档字符串
- 重要功能需要添加单元测试
- 提交前请运行代码格式化工具

### 调试技巧

1. **启用调试模式**
```python
# 在app.py中设置
debug = True
```

2. **查看日志**
```bash
# 查看应用日志
tail -f debug/app.log
```

3. **数据库调试**
```python
# 使用SQLite浏览器查看数据库
sqlite3 voice_pack.db
```

## ❓ 常见问题

### 安装问题

**Q: pip安装依赖失败怎么办？**
A: 尝试使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**Q: Windows下启动脚本无法运行？**
A: 确保Python已正确安装并添加到PATH环境变量中。

### 使用问题

**Q: LLM API连接失败？**
A: 检查以下几点：
- API URL格式是否正确（必须以"/v1"结尾）
- API Key是否有效
- 网络连接是否正常
- API服务是否可用

**Q: 语音生成失败？**
A: 可能的原因：
- GPT-SoVITS服务未启动
- 音频文件格式不支持
- 系统资源不足

**Q: 导出的语音包无法使用？**
A: 检查：
- 文件格式是否为48KHz, 16bit, 单声道WAV
- 文件命名是否符合规范
- ZIP文件是否完整

### 性能优化

**Q: 系统运行缓慢怎么办？**
A: 优化建议：
- 增加系统内存
- 使用SSD存储
- 关闭不必要的后台程序
- 调整批量处理的并发数

## 📝 更新日志

### v1.2.0 (2024-12-XX)
- 🔧 **导出功能优化**：修复语音包导出中的进度回调参数不匹配问题
- 📦 **依赖优化**：移除scipy依赖，使用numpy进行音频处理
- 🎯 **进度显示改进**：统一进度回调格式为 `(current, total, message)`
- 🖥️ **Windows支持**：新增Windows EXE打包支持和相关脚本
- 🧪 **测试增强**：添加多个测试脚本和调试工具
- 📊 **CSV处理**：改进CSV参数加载器和编辑功能
- 🔄 **兼容性修复**：修复Gradio版本兼容性问题
- 📱 **多版本支持**：新增独立应用版本和简化版本

### v1.1.0 (2024-11-XX)
- 🎨 **UI优化**：改进用户界面和交互体验
- 🔧 **文件管理**：优化文件管理和对话生成功能
- 📝 **文档完善**：添加部署指南和数据结构设计文档
- 🐛 **Bug修复**：修复多个已知问题和稳定性改进

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🎯 完整的五步工作流程
- 🎨 现代化的Web界面
- 🤖 LLM集成和台词生成
- 🎵 GPT-SoVITS语音合成
- 📦 语音包导出功能

### 计划中的功能
- 🌐 多语言界面支持
- 🎛️ 更多语音参数调节
- 📊 使用统计和分析
- 🔄 自动更新机制
- 🎨 主题和界面定制

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **报告问题**
   - 在GitHub Issues中报告bug
   - 提供详细的复现步骤
   - 附上相关的日志信息

2. **提出建议**
   - 在Issues中提出功能建议
   - 详细描述期望的功能
   - 说明使用场景和价值

3. **代码贡献**
   - Fork项目到你的账户
   - 创建功能分支
   - 提交Pull Request
   - 等待代码审查

### 贡献者

感谢所有为项目做出贡献的开发者！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目主页**：https://github.com/LnbConceptions/breathVOICE
- **问题反馈**：https://github.com/LnbConceptions/breathVOICE/issues
- **API服务**：https://tts.ioioioioio.com:1120

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个星标！**

Made with ❤️ by L&B Conceptions

</div>