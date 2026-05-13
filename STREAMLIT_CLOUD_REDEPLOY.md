# Streamlit Cloud 重新部署指南

## 问题说明

如果你看到以下错误：
```
ImportError: This app has encountered an error...
File "/mount/src/patient-followup-system/ai_agent.py", line 485, in validate_environment
    raise ImportError(
```

这说明 Streamlit Cloud **还在使用旧版本的代码**。

---

## 解决方案

### 方法 1：手动触发重新部署（推荐）

1. **访问 Streamlit Cloud**
   - 打开你的应用管理页面
   - URL 格式：`https://share.streamlit.io/your-username/your-app`

2. **找到重新部署按钮**
   - 点击右上角的 **"⋮"** 菜单
   - 选择 **"Redeploy"** 或 **"Restart"**

3. **等待重新部署完成**
   - 通常需要 2-5 分钟
   - 可以在 "Logs" 标签页查看进度

4. **验证修复**
   - 刷新应用页面
   - 尝试使用 AI 功能
   - 应该看到友好提示而不是崩溃

---

### 方法 2：推送空提交强制重新部署

如果方法 1 不起作用，可以推送一个空提交来强制重新部署：

```bash
# 在项目根目录执行
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

这会触发 Streamlit Cloud 重新拉取代码并部署。

---

### 方法 3：删除并重新创建应用

如果以上方法都无效：

1. **删除现有应用**
   - 进入应用管理页面
   - 点击 **"⋮"** → **"Delete app"**

2. **重新创建应用**
   - 点击 **"New app"**
   - 选择仓库：`pathologysmile/patient-followup-system`
   - Branch: `main`
   - Main file: `app.py`

3. **配置 Secrets**
   ```toml
   DASHSCOPE_API_KEY = "sk-your-api-key"
   DASHSCOPE_MODEL = "qwen-turbo"
   DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
   ```

---

## 验证修复是否成功

### 场景 1：API Key 未配置

如果 API Key 没有配置，你应该看到：
- ✅ 应用正常启动，不崩溃
- ⚠️ AI 功能显示："AI 功能暂未启用（API Key 未配置）"
- ✅ 其他功能正常工作

### 场景 2：API Key 已配置

如果 API Key 已正确配置，你应该看到：
- ✅ 应用正常启动
- ✅ AI 功能正常工作
- ✅ 可以生成智能话术

---

## 常见问题

### Q1: 重新部署后还是报错？

**检查清单**：
1. ✅ 确认 Git 推送成功（查看 GitHub 上的最新 commit）
2. ✅ 确认 Streamlit Cloud 使用的是正确的分支（main）
3. ✅ 清除浏览器缓存（Ctrl + F5）
4. ✅ 查看 Streamlit Cloud Logs 确认使用了新代码

### Q2: 如何确认代码已更新？

在 Streamlit Cloud Logs 中查找：
```
✅ DASHSCOPE_API_KEY 已配置 (长度: XX)
```
或
```
⚠️  警告: DASHSCOPE_API_KEY 未设置！
```

如果看到这些日志，说明新代码已生效。

### Q3: 我想立即启用 AI 功能怎么办？

1. 获取 API Key：https://dashscope.console.aliyun.com/
2. 在 Streamlit Cloud Secrets 中添加：
   ```toml
   DASHSCOPE_API_KEY = "sk-your-api-key"
   ```
3. 保存后应用会自动重启
4. AI 功能立即启用

---

## 当前代码状态

✅ **已修复的内容**：
- 所有 AI 函数添加了 API Key 检查
- API Key 缺失时返回友好提示
- 应用不会因缺少 API Key 而崩溃
- 代码已推送到 GitHub（commit: 35decb2）

🔄 **需要做的**：
- 在 Streamlit Cloud 触发重新部署
- （可选）配置 API Key 以启用 AI 功能

---

## 联系支持

如果问题仍然存在：
1. 查看 Streamlit Cloud Logs 获取详细错误信息
2. 确认 GitHub 上的代码是最新版本
3. 在 GitHub Issues 中报告问题

---

**最后更新**：2026-05-13  
**文档版本**：1.0.0
