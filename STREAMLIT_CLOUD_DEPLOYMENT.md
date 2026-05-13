# Streamlit Community Cloud 部署指南

本文档详细说明如何将患者出院回访智能提醒系统部署到 Streamlit Community Cloud。

---

## 📋 前置要求

- ✅ GitHub 账号
- ✅ 代码已上传到 GitHub 公开仓库
- ✅ 通义千问 API 密钥（DashScope）

---

## 🚀 部署步骤

### 第一步：访问 Streamlit Cloud

1. 打开浏览器访问：https://share.streamlit.io/
2. 点击 **"New app"** 按钮
3. 使用 GitHub 账号登录授权

### 第二步：配置应用

在 "Deploy an app" 页面填写以下信息：

| 字段 | 值 |
|------|-----|
| **Repository** | `pathologysmile/patient-followup-system` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

### 第三步：添加 Secrets（重要！）

在部署之前，必须配置 API 密钥和其他敏感信息。

#### 3.1 找到 Secrets 设置

1. 部署应用后，进入应用管理页面
2. 点击右上角的 **"⋮"** 菜单
3. 选择 **"Settings"**
4. 找到 **"Secrets"** 标签页

#### 3.2 粘贴 Secrets 配置

将以下内容粘贴到 Secrets 编辑器中：

```toml
# ============================================
# Streamlit Community Cloud Secrets 配置
# ============================================

# 通义千问 API 配置（必需）
DASHSCOPE_API_KEY = "sk-your-actual-api-key-here"
DASHSCOPE_MODEL = "qwen-turbo"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 数据库配置
DATABASE_PATH = "./patients.db"

# 日志配置
LOG_LEVEL = "INFO"
```

⚠️ **重要提示**：
- 将 `sk-your-actual-api-key-here` 替换为你真实的通义千问 API 密钥
- 获取 API 密钥：https://dashscope.console.aliyun.com/
- Secrets 不会提交到 Git，安全存储

#### 3.3 保存并重启

1. 点击 **"Save"** 保存 Secrets
2. 应用会自动重启以加载新配置

### 第四步：等待部署完成

- 首次部署通常需要 **2-5 分钟**
- 可以在 "Logs" 标签页查看部署进度
- 部署成功后会显示应用 URL

### 第五步：测试应用

1. 访问生成的 URL（例如：`https://xxx-xxx.streamlit.app/`）
2. 测试以下功能：
   - ✅ Dashboard 是否正常加载
   - ✅ 患者登记功能
   - ✅ AI 话术生成
   - ✅ 数据导出功能

---

## ⚠️ 重要注意事项

### 1. 数据持久化问题

**问题**：Streamlit Community Cloud 使用临时文件系统，应用重启后数据会丢失。

**影响**：
- 患者数据会在应用重启后消失
- 每次重新部署都会清空数据

**解决方案**：

#### 方案 A：定期导出备份（简单）
1. 使用应用的"导出数据"功能
2. 定期下载 CSV/Excel 备份
3. 重新部署时手动导入数据

#### 方案 B：迁移到云端数据库（推荐）
- 使用 Supabase（PostgreSQL）
- 使用 Railway（PostgreSQL）
- 使用 MongoDB Atlas（NoSQL）

详见：[Supabase 云端数据库集成方案](./STREAMLIT_CLOUD_SUPABASE.md)

### 2. API 调用限制

**通义千问免费额度**：
- qwen-turbo：每月 100 万 tokens
- 超出后需要付费

**建议**：
- 监控 API 使用情况
- 合理使用 AI 生成功能
- 考虑缓存 AI 响应结果

### 3. 应用休眠

**问题**：如果 7 天没有访问，应用会进入休眠状态。

**解决**：
- 定期访问应用保持活跃
- 或使用外部服务定期 ping 应用

### 4. 文件大小限制

- 每个应用最多 **1 GB** 存储空间
- 单个文件不超过 **200 MB**
- 数据库文件应尽量小

---

## 🔧 故障排查

### 问题 1：应用无法启动

**症状**：部署失败或应用崩溃

**检查清单**：
1. ✅ 确认 `requirements.txt` 包含所有依赖
2. ✅ 确认 Secrets 已正确配置
3. ✅ 查看 Logs 标签页的错误信息
4. ✅ 确认 `app.py` 路径正确

**常见错误**：
```
ModuleNotFoundError: No module named 'xxx'
```
**解决**：在 `requirements.txt` 中添加缺失的包

### 问题 2：API 密钥错误

**症状**：AI 话术生成失败

**检查**：
1. 确认 Secrets 中的 `DASHSCOPE_API_KEY` 正确
2. 确认 API 密钥未过期
3. 查看应用日志中的错误信息

**解决**：
```toml
# 重新配置 Secrets
DASHSCOPE_API_KEY = "sk-新的API密钥"
```

### 问题 3：数据丢失

**症状**：刷新页面后数据消失

**原因**：Cloud 环境的临时文件系统

**解决**：
- 立即实施云端数据库方案
- 或定期手动备份数据

### 问题 4：加载速度慢

**优化建议**：
1. ✅ 已启用数据缓存机制
2. 减少不必要的 AI 调用
3. 优化数据库查询
4. 使用分页加载大数据集

---

## 📊 性能优化建议

### 1. 缓存策略

当前已实现的缓存：
- 患者数据：5 分钟 TTL
- 今日待回访：1 分钟 TTL
- 逾期患者：1 分钟 TTL
- 提醒配置：10 分钟 TTL

**建议**：
- 根据数据更新频率调整 TTL
- 在数据修改后手动清除缓存

### 2. 数据库优化

**当前**：SQLite（适合小规模数据）

**优化**：
- 添加索引到常用查询字段
- 定期清理过期数据
- 迁移到云端数据库

### 3. AI 调用优化

**建议**：
- 缓存 AI 生成的话术
- 批量处理 AI 请求
- 设置超时和重试机制

---

## 🔄 更新应用

### 方法 1：自动更新（推荐）

1. 推送代码到 GitHub：
   ```bash
   git add .
   git commit -m "更新说明"
   git push origin main
   ```

2. Streamlit Cloud 会自动检测变化并重新部署
3. 等待 2-5 分钟完成更新

### 方法 2：手动重新部署

1. 进入应用管理页面
2. 点击 **"⋮"** → **"Redeploy"**
3. 等待重新部署完成

---

## 📝 最佳实践

### 1. 版本控制

- ✅ 使用语义化版本号
- ✅ 编写清晰的 commit 信息
- ✅ 使用分支进行功能开发

### 2. 安全管理

- ✅ 永远不要硬编码 API 密钥
- ✅ 使用 Streamlit Secrets 管理敏感信息
- ✅ 定期轮换 API 密钥
- ✅ 不在公共仓库暴露 `.env` 文件

### 3. 数据备份

- ✅ 每周导出一次数据备份
- ✅ 保留多个历史备份
- ✅ 测试备份文件的恢复流程

### 4. 监控和维护

- ✅ 定期检查应用日志
- ✅ 监控 API 使用量
- ✅ 测试关键功能是否正常
- ✅ 及时更新依赖包

---

## 🆘 获取帮助

### 官方资源

- Streamlit 文档：https://docs.streamlit.io/
- Streamlit Cloud 文档：https://docs.streamlit.io/streamlit-community-cloud
- 社区论坛：https://discuss.streamlit.io/

### 本项目资源

- GitHub 仓库：https://github.com/pathologysmile/patient-followup-system
- 问题反馈：在 GitHub Issues 中提交

---

## 📞 联系支持

如有问题，请：
1. 查看应用日志（Logs 标签页）
2. 检查 Secrets 配置是否正确
3. 在 GitHub Issues 中描述问题
4. 提供错误信息和截图

---

**最后更新**：2026-05-13  
**文档版本**：1.0.0
