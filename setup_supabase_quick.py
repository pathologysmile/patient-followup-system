#!/usr/bin/env python3
"""
Supabase 快速配置助手
帮助你快速配置云端数据库，解决数据丢失问题
"""

import os
import sys
import webbrowser
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🚀 Supabase 快速配置助手")
    print("=" * 70)
    print()
    print("💡 为什么需要 Supabase？")
    print("   Streamlit Cloud 每次重新部署都会清空本地数据库")
    print("   Supabase 是云端数据库，数据永久保存，不会丢失！")
    print()

def step1_create_project():
    print("📋 步骤 1: 创建 Supabase 项目")
    print("-" * 70)
    print()
    print("请在浏览器中完成以下操作：")
    print()
    print("1️⃣  访问: https://supabase.com/")
    print("2️⃣  点击 'Start your project' 并登录（推荐 GitHub 登录）")
    print("3️⃣  点击 'New project'")
    print("4️⃣  填写项目信息：")
    print("    - Organization: 选择或创建组织")
    print("    - Name: patient-followup-db")
    print("    - Database Password: 设置强密码（务必保存！）")
    print("    - Region: Singapore (亚太区最快)")
    print("5️⃣  点击 'Create new project'")
    print("6️⃣  等待 2-3 分钟项目创建完成")
    print()
    
    input("✅ 完成后按 Enter 继续...")
    print()

def step2_get_api_key():
    print("📋 步骤 2: 获取 API Key")
    print("-" * 70)
    print()
    print("项目创建完成后：")
    print()
    print("1️⃣  在左侧菜单点击 'Settings' (齿轮图标)")
    print("2️⃣  点击 'API'")
    print("3️⃣  复制以下两个信息：")
    print()
    print("    📌 Project URL:")
    print("       https://xxxxxxxxxxxxx.supabase.co")
    print()
    print("    📌 anon public key:")
    print("       eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX...")
    print()
    print("⚠️  注意：使用 'anon public' key，不要使用 'service_role'")
    print()
    
    project_url = input("请输入 Project URL: ").strip()
    api_key = input("请输入 anon public key: ").strip()
    
    if not project_url or not api_key:
        print("❌ 错误：URL 和 Key 不能为空！")
        sys.exit(1)
    
    print()
    return project_url, api_key

def step3_execute_sql(project_url):
    print("📋 步骤 3: 执行建表 SQL")
    print("-" * 70)
    print()
    print("有两种方式：")
    print()
    print("方式 A（推荐）：在线执行")
    print("1️⃣  在 Supabase 左侧菜单点击 'SQL Editor'")
    print("2️⃣  点击 'New query'")
    print("3️⃣  打开项目中的 supabase_schema.sql 文件")
    print("4️⃣  复制全部内容并粘贴到 SQL Editor")
    print("5️⃣  点击 'Run' 按钮")
    print()
    print("方式 B：使用我提供的链接")
    print(f"   访问你的项目: {project_url}")
    print("   然后按照方式 A 的步骤操作")
    print()
    
    input("✅ SQL 执行完成后按 Enter 继续...")
    print()

def step4_generate_env(project_url, api_key):
    print("📋 步骤 4: 生成配置文件")
    print("-" * 70)
    print()
    
    # 生成 .env 文件内容
    env_content = f"""# ============================================
# Supabase 数据库配置
# ============================================

# 启用 Supabase
USE_SUPABASE=true

# Supabase 连接信息
SUPABASE_URL={project_url}
SUPABASE_KEY={api_key}

# ============================================
# 通义千问 API 配置（可选）
# ============================================
DASHSCOPE_API_KEY=sk-your-api-key-here
DASHSCOPE_MODEL=qwen-turbo
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ============================================
# 日志配置
# ============================================
LOG_LEVEL=INFO
"""
    
    # 写入 .env 文件
    env_path = Path(".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ 已生成 .env 文件: {env_path.absolute()}")
    print()
    
    # 生成 Streamlit Cloud Secrets 内容
    secrets_content = f"""# ============================================
# Streamlit Cloud Secrets 配置
# 复制到 Settings -> Secrets 中
# ============================================

# 启用 Supabase
USE_SUPABASE = "true"

# Supabase 配置
SUPABASE_URL = "{project_url}"
SUPABASE_KEY = "{api_key}"

# 通义千问 API 配置
DASHSCOPE_API_KEY = "sk-your-api-key-here"
DASHSCOPE_MODEL = "qwen-turbo"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 日志配置
LOG_LEVEL = "INFO"
"""
    
    secrets_path = Path("streamlit_cloud_secrets.toml")
    with open(secrets_path, "w", encoding="utf-8") as f:
        f.write(secrets_content)
    
    print(f"✅ 已生成 Streamlit Cloud Secrets 文件: {secrets_path.absolute()}")
    print()
    print("📝 下一步操作：")
    print("   1. 本地测试：直接运行 streamlit run app.py")
    print("   2. 云端部署：复制上面的内容到 Streamlit Cloud Secrets")
    print()

def step5_test_connection():
    print("📋 步骤 5: 测试连接")
    print("-" * 70)
    print()
    print("正在测试 Supabase 连接...")
    print()
    
    try:
        from supabase_adapter import get_supabase_adapter
        adapter = get_supabase_adapter()
        
        # 尝试查询患者数量
        patients = adapter.get_all_patients()
        count = len(patients) if patients else 0
        
        print(f"✅ Supabase 连接成功！")
        print(f"   当前患者数量: {count}")
        print()
        print("🎉 配置完成！你现在可以：")
        print("   1. 运行应用: streamlit run app.py")
        print("   2. 添加患者数据（会保存到云端）")
        print("   3. 重新部署到 Streamlit Cloud（数据不会丢失）")
        print()
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print()
        print("可能的原因：")
        print("   1. 未安装 supabase 包: pip install supabase")
        print("   2. SQL 表未创建: 请在 SQL Editor 中执行 supabase_schema.sql")
        print("   3. API Key 不正确: 请检查是否正确复制")
        print()
        print("需要帮助吗？查看 SUPABASE_SETUP_GUIDE.md")
        print()

def main():
    print_header()
    
    # 询问是否打开浏览器
    open_browser = input("🌐 是否打开 Supabase 网站？(y/n): ").strip().lower()
    if open_browser == 'y':
        webbrowser.open("https://supabase.com/dashboard")
        print("✅ 已打开浏览器，请按照提示操作")
        print()
    
    # 执行配置步骤
    step1_create_project()
    project_url, api_key = step2_get_api_key()
    step3_execute_sql(project_url)
    step4_generate_env(project_url, api_key)
    step5_test_connection()
    
    print("=" * 70)
    print("🎊 恭喜！Supabase 配置完成！")
    print("=" * 70)
    print()
    print("📚 相关文档：")
    print("   - SUPABASE_SETUP_GUIDE.md: 详细配置指南")
    print("   - STREAMLIT_CLOUD_SUPABASE.md: 云端集成方案")
    print()
    print("💡 提示：")
    print("   现在你的数据会永久保存在云端，不再担心丢失！")
    print()

if __name__ == "__main__":
    main()
