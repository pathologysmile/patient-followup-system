# 患者回访系统 - 部署指南

## 📋 目录结构

```
D:\remindercode\
├── app.py                      # 主应用文件
├── db_manager.py               # 数据库管理
├── ai_agent.py                 # AI智能体
├── patients.db                 # SQLite数据库
├── .env                        # 环境配置（需自行创建）
├── .env.example                # 配置模板
├── requirements.txt            # Python依赖
├── deploy.bat                  # Windows部署脚本
├── deploy.ps1                  # PowerShell部署脚本
├── start_production.bat        # 生产环境启动
├── backup.bat                  # 数据备份脚本
├── auto_start.bat              # 开机自启动脚本
├── install_autostart.bat       # 安装开机自启
├── uninstall_autostart.bat     # 卸载开机自启
├── .streamlit/
│   └── config.toml            # Streamlit配置
├── logs/                       # 日志目录（自动创建）
└── backups/                    # 备份目录（自动创建）
```

## 🚀 快速部署

### 方法一：使用批处理脚本（推荐）

```bash
# 双击运行或在命令行执行
deploy.bat
```

### 方法二：使用PowerShell脚本

```powershell
# 右键以管理员身份运行
.\deploy.ps1
```

### 方法三：手动部署

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入API密钥

# 5. 启动应用
streamlit run app.py
```

## ⚙️ 配置说明

### 1. 环境变量配置 (.env)

```env
# 通义千问 API 配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 服务器配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

**获取API密钥：**
1. 访问 https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 创建API Key

### 2. Streamlit配置 (.streamlit/config.toml)

已预配置生产环境参数：
- 监听所有网络接口 (0.0.0.0)
- 端口 8501
- 无头模式（不自动打开浏览器）
- 自定义主题颜色

## 🔧 常用操作

### 启动服务

```bash
# 生产模式启动
start_production.bat

# 或直接运行
streamlit run app.py --server.headless true
```

### 停止服务

在运行Streamlit的窗口按 `Ctrl+C`

或强制停止：
```bash
taskkill /F /IM streamlit.exe
```

### 数据备份

```bash
# 手动备份
backup.bat

# 自动备份（添加到任务计划）
# 每天凌晨2点自动备份
schtasks /create /tn "患者数据每日备份" /tr "D:\remindercode\backup.bat" /sc daily /st 02:00
```

### 查看日志

```bash
# Streamlit日志在控制台输出
# 应用日志目录
logs/
```

### 更新依赖

```bash
.venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

## 🌐 网络访问配置

### 允许局域网访问

1. 确保防火墙允许8501端口
2. 查看本机IP地址：
   ```bash
   ipconfig
   ```
3. 其他设备访问：`http://YOUR_IP:8501`

### 防火墙设置

```bash
# 添加防火墙规则（管理员权限）
netsh advfirewall firewall add rule name="患者回访系统" dir=in action=allow protocol=TCP localport=8501
```

## 🔒 安全建议

1. **保护API密钥**
   - 不要将 `.env` 文件上传到Git
   - 定期更换API密钥
   - 限制API调用配额

2. **数据库安全**
   - 定期备份数据
   - 设置数据库访问权限
   - 加密敏感信息

3. **网络安全**
   - 仅在可信网络中部署
   - 使用HTTPS（需要反向代理）
   - 限制访问IP范围

## 📊 监控与维护

### 检查服务状态

```bash
# 查看进程
tasklist | findstr streamlit

# 查看端口占用
netstat -ano | findstr 8501
```

### 性能优化

1. **数据库优化**
   ```sql
   -- 定期清理已完成的数据
   DELETE FROM patients WHERE status='completed' AND created_at < datetime('now', '-90 days');
   ```

2. **内存管理**
   - 定期重启服务
   - 监控内存使用

3. **日志轮转**
   - 定期清理旧日志
   - 设置日志文件大小限制

## 🔄 版本更新

```bash
# 1. 备份当前版本
backup.bat

# 2. 拉取最新代码
git pull

# 3. 更新依赖
.venv\Scripts\activate
pip install -r requirements.txt

# 4. 重启服务
taskkill /F /IM streamlit.exe
start_production.bat
```

## 🐛 故障排查

### 问题1：端口被占用

```bash
# 查找占用端口的进程
netstat -ano | findstr 8501

# 结束进程
taskkill /F /PID <PID>
```

### 问题2：依赖冲突

```bash
# 删除虚拟环境重新创建
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 问题3：API调用失败

- 检查网络连接
- 验证API密钥是否正确
- 查看API配额是否用完
- 检查 `.env` 文件格式

### 问题4：数据库锁定

```bash
# 关闭所有访问数据库的程序
# 删除临时文件
del patients.db-journal
```

## 📞 技术支持

如遇问题，请检查：
1. Python版本 >= 3.8
2. 所有依赖已正确安装
3. API密钥配置正确
4. 防火墙/杀毒软件未阻止
5. 端口8501未被占用

## 📝 许可证

本项目仅供内部使用，请勿用于商业用途。

---
**版本**: 1.0  
**更新日期**: 2026-05-09  
**维护者**: 开发团队
