"""
Supabase 配置助手
帮助你快速获取和配置 Supabase API Key
"""
import os
import webbrowser
from pathlib import Path


def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_step(step_num, title):
    """打印步骤"""
    print(f"\n{'─'*60}")
    print(f"  步骤 {step_num}: {title}")
    print(f"{'─'*60}")


def main():
    """主函数"""
    print_header("Supabase 配置助手")
    
    print("\n📋 本工具将引导你完成 Supabase 配置")
    print("\n⚠️  提示：你需要先有一个 Supabase 账号")
    print("   如果没有，请访问: https://supabase.com/")
    
    input("\n按 Enter 键继续...")
    
    # 步骤 1: 打开 Supabase 网站
    print_step(1, "访问 Supabase 并登录")
    print("\n我将为你打开 Supabase 网站...")
    print("\n操作指南:")
    print("  1. 如果已有账号，点击 'Sign in' 登录")
    print("  2. 如果没有账号，点击 'Start your project' 注册")
    print("  3. 登录后，创建新项目或选择现有项目")
    
    open_browser = input("\n是否现在打开浏览器？(yes/no): ")
    if open_browser.lower() == "yes":
        webbrowser.open("https://supabase.com/dashboard")
        print("✅ 已打开浏览器，请完成登录后返回继续...")
        input("完成后按 Enter 键继续...")
    
    # 步骤 2: 获取 API Key
    print_step(2, "获取 API Key")
    print("\n在 Supabase 控制台中:")
    print("  1. 选择你的项目")
    print("  2. 点击左侧菜单 'Settings' (齿轮图标)")
    print("  3. 点击 'API'")
    print("  4. 复制以下信息:")
    print("     - Project URL: https://xxx.supabase.co")
    print("     - anon public key: eyJhbG...")
    
    print("\n💡 提示:")
    print("  - 对于 Streamlit Cloud 部署，使用 'anon public' key")
    print("  - 对于数据迁移，可以使用 'service_role' key")
    
    project_url = input("\n请输入 Project URL: ").strip()
    api_key = input("请输入 API Key: ").strip()
    
    # 验证输入
    if not project_url or not api_key:
        print("\n❌ 错误: URL 和 Key 不能为空")
        return
    
    if not project_url.startswith("https://"):
        print("\n⚠️  警告: URL 应该以 https:// 开头")
        confirm = input("是否继续？(yes/no): ")
        if confirm.lower() != "yes":
            return
    
    # 步骤 3: 执行建表 SQL
    print_step(3, "执行建表 SQL")
    print("\n在 Supabase 控制台中:")
    print("  1. 点击左侧菜单 'SQL Editor'")
    print("  2. 点击 'New query'")
    print("  3. 打开项目中的 supabase_schema.sql 文件")
    print("  4. 复制全部内容并粘贴到 SQL Editor")
    print("  5. 点击 'Run' 按钮")
    
    sql_done = input("\n是否已完成建表？(yes/no): ")
    if sql_done.lower() != "yes":
        print("\n💡 提示:")
        print("  - SQL 文件位置: ./supabase_schema.sql")
        print("  - 你可以稍后再执行建表")
    
    # 步骤 4: 生成配置文件
    print_step(4, "生成配置文件")
    
    # 检查是否有 .env 文件
    env_file = Path(".env")
    
    if env_file.exists():
        print("\n⚠️  检测到已存在 .env 文件")
        backup = input("是否备份现有文件？(yes/no): ")
        if backup.lower() == "yes":
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f".env.backup_{timestamp}"
            shutil.copy2(".env", backup_file)
            print(f"✅ 已备份到: {backup_file}")
    
    # 生成配置内容
    config_content = f"""# ============================================
# Supabase 配置
# ============================================
# 自动生成于: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 启用 Supabase
USE_SUPABASE=true

# Supabase 连接信息
SUPABASE_URL={project_url}
SUPABASE_KEY={api_key}

# ============================================
# 其他配置（从 .env.example 复制）
# ============================================

# 通义千问 API 配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 服务器配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 数据库配置（SQLite，备用）
DATABASE_PATH=./patients.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
    
    # 写入文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"\n✅ 配置文件已生成: .env")
    print("\n📝 配置内容预览:")
    print(f"  USE_SUPABASE=true")
    print(f"  SUPABASE_URL={project_url[:30]}...")
    print(f"  SUPABASE_KEY={api_key[:20]}...")
    
    # 步骤 5: 测试连接
    print_step(5, "测试连接")
    print("\n我将尝试测试 Supabase 连接...")
    
    try:
        from supabase_adapter import get_supabase_adapter
        adapter = get_supabase_adapter()
        print("\n✅ Supabase 连接成功！")
        print("\n🎉 配置完成！你现在可以:")
        print("  1. 运行应用: streamlit run app.py")
        print("  2. 迁移数据: python migrate_to_supabase.py")
        
    except ImportError:
        print("\n⚠️  未安装 Supabase SDK")
        print("\n请先安装依赖:")
        print("  pip install supabase")
        print("\n然后再次测试连接:")
        print("  python -c \"from supabase_adapter import get_supabase_adapter; adapter = get_supabase_adapter(); print('✅ 连接成功')\"")
        
    except Exception as e:
        print(f"\n❌ 连接失败: {str(e)}")
        print("\n请检查:")
        print("  1. Project URL 是否正确")
        print("  2. API Key 是否正确")
        print("  3. 网络连接是否正常")
        print("  4. 是否已在 Supabase 中执行建表 SQL")
    
    # 完成
    print_header("配置完成")
    print("\n📚 相关文档:")
    print("  - SUPABASE_SETUP_GUIDE.md: 详细配置指南")
    print("  - STREAMLIT_CLOUD_SUPABASE.md: 云端集成方案")
    print("  - supabase_schema.sql: 建表 SQL")
    print("  - migrate_to_supabase.py: 数据迁移脚本")
    
    print("\n💡 下一步:")
    print("  1. 如果使用 Streamlit Cloud，请在 Secrets 中配置相同的信息")
    print("  2. 如有问题，查看文档或提交 Issue")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
