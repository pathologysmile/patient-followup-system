# 🏥 患者出院回访智能提醒系统

> 基于 Streamlit + LangChain + 通义千问的智能患者回访管理系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 功能特性

### 🎯 核心功能
- **智能提醒看板** - 自动识别今日/明日回访任务，紧急任务红色警告
- **AI话术生成** - 基于通义千问自动生成个性化回访话术
- **患者数据管理** - 完整的患者信息录入、查询、状态管理
- **智能体对话** - 与AI助手对话，获取专业建议

### 📊 数据管理
- 患者基本信息（姓名、性别、诊断）
- 联系方式（联系人、电话）
- 时间节点（出院日期、回访日期）
- 回访状态跟踪（待回访/已完成）

### 🤖 AI能力
- 智能话术生成
- 多轮对话支持
- 医疗知识问答
- 回访技巧指导

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Windows 操作系统
- 通义千问API密钥

### 一键部署

```bash
# 克隆或下载项目到本地
cd D:\remindercode

# 运行部署脚本
deploy.bat
```

### 配置API密钥

编辑 `.env` 文件：
```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo
```

获取API密钥：https://dashscope.aliyun.com/

### 启动系统

```bash
# 生产模式启动
start_production.bat

# 访问系统
浏览器打开: http://localhost:8501
```

详细部署指南请查看：[DEPLOYMENT.md](DEPLOYMENT.md)

## 📱 界面预览

### 智能提醒看板
- 🔴 今日紧急任务醒目提示
- 🟡 明日待办事项列表
- ✨ 一键生成AI话术

### 患者数据查看
- 📋 完整数据表格展示
- 🔍 状态筛选功能
- 📊 统计数据面板
- ✅ 快捷状态更新

### 智能体对话
- 💬 实时对话界面
- 📜 对话历史保存
- 🎓 专业知识问答

## 📂 项目结构

```
remindercode/
├── app.py                  # 主应用（Streamlit界面）
├── db_manager.py           # 数据库管理模块
├── ai_agent.py             # AI智能体模块
├── patients.db             # SQLite数据库
├── .env                    # 环境配置
├── requirements.txt        # Python依赖
├── deploy.bat              # 部署脚本
├── start_production.bat    # 启动脚本
├── backup.bat              # 备份脚本
├── auto_start.bat          # 开机自启脚本
├── .streamlit/
│   └── config.toml         # Streamlit配置
├── logs/                   # 日志目录
└── backups/                # 备份目录
```

## 🔧 技术栈

- **前端框架**: Streamlit 1.57.0
- **AI框架**: LangChain 1.2.18
- **大语言模型**: 通义千问 (Qwen-Turbo)
- **数据库**: SQLite3
- **数据处理**: Pandas 2.3.3
- **环境管理**: Python-dotenv

## 📖 文档

- [快速开始指南](QUICKSTART.md) - 5分钟上手
- [完整部署文档](DEPLOYMENT.md) - 详细部署说明
- [开机自启动说明](开机自启动说明.md) - 自动化配置

## 🛠️ 常用命令

```bash
# 部署项目
deploy.bat

# 启动服务
start_production.bat

# 数据备份
backup.bat

# 设置开机自启
install_autostart.bat

# 取消开机自启
uninstall_autostart.bat
```

## 🔒 安全提示

1. **保护API密钥**
   - 不要将 `.env` 文件上传到公开仓库
   - 定期更换API密钥
   - 限制API调用配额

2. **数据备份**
   - 定期备份数据库文件
   - 使用 `backup.bat` 自动备份

3. **网络安全**
   - 仅在可信网络中部署
   - 配置防火墙规则
   - 限制访问IP范围

## 📊 系统要求

- **操作系统**: Windows 10/11
- **Python版本**: 3.8 或更高
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 500MB
- **网络**: 需要访问通义千问API

## 🐛 故障排查

常见问题及解决方案请参考：[DEPLOYMENT.md](DEPLOYMENT.md#-故障排查)

## 📝 更新日志

### v1.0.0 (2026-05-09)
- ✨ 初始版本发布
- 🎯 智能提醒看板
- 📋 患者数据管理
- 💬 AI智能体对话
- 🔄 开机自启动功能
- 💾 自动备份功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目仅供内部使用。

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**Made with ❤️ using Streamlit & LangChain**
