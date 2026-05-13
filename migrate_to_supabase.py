"""
从 SQLite 迁移数据到 Supabase

使用方法：
1. 确保已安装 supabase: pip install supabase
2. 配置 Supabase 连接信息（在脚本中修改或使用环境变量）
3. 运行脚本: python migrate_to_supabase.py
"""
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# SQLite 配置
SQLITE_DB = "patients.db"

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-service-role-key")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        from supabase import create_client, Client
        print("✅ Supabase SDK 已安装")
        return True
    except ImportError:
        print("❌ 未安装 Supabase SDK")
        print("请运行: pip install supabase")
        return False


def migrate_data():
    """迁移数据从 SQLite 到 Supabase"""
    print("="*60)
    print("  患者回访系统 - 数据迁移工具")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 导入 Supabase
    from supabase import create_client, Client
    
    # 验证配置
    if SUPABASE_URL == "https://your-project.supabase.co":
        print("\n❌ 错误: 请先配置 Supabase URL 和 Key")
        print("\n请在 .env 文件中添加:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_KEY=your-service-role-key")
        return
    
    print(f"\n📡 连接到 Supabase: {SUPABASE_URL}")
    
    try:
        # 创建 Supabase 客户端
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 测试连接
        response = supabase.table("patients").select("count").limit(1).execute()
        print("✅ Supabase 连接成功\n")
        
    except Exception as e:
        print(f"❌ Supabase 连接失败: {str(e)}")
        print("\n请检查:")
        print("1. SUPABASE_URL 是否正确")
        print("2. SUPABASE_KEY 是否正确")
        print("3. 网络连接是否正常")
        return
    
    # 检查 SQLite 数据库是否存在
    if not os.path.exists(SQLITE_DB):
        print(f"❌ SQLite 数据库文件不存在: {SQLITE_DB}")
        return
    
    print(f"📁 读取 SQLite 数据库: {SQLITE_DB}\n")
    
    # 连接 SQLite
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    migration_stats = {
        "patients": 0,
        "visit_plans": 0,
        "visit_records": 0,
        "errors": []
    }
    
    try:
        # ========================================
        # 1. 迁移患者数据
        # ========================================
        print("📋 步骤 1: 迁移患者数据...")
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        
        print(f"   找到 {len(patients)} 个患者")
        
        for i, patient in enumerate(patients, 1):
            try:
                patient_data = {
                    "id": patient[0],
                    "name": patient[1],
                    "gender": patient[2] if len(patient) > 2 else None,
                    "discharge_date": patient[3] if len(patient) > 3 else None,
                    "diagnosis": patient[4] if len(patient) > 4 else None,
                    "contact_person": patient[5] if len(patient) > 5 else None,
                    "contact_phone": patient[6] if len(patient) > 6 else None,
                    "hospital_number": patient[7] if len(patient) > 7 else None
                }
                
                # 插入到 Supabase（使用 upsert 避免重复）
                supabase.table("patients").upsert(patient_data).execute()
                migration_stats["patients"] += 1
                
                if i % 10 == 0 or i == len(patients):
                    print(f"   ✓ 已迁移 {i}/{len(patients)} 个患者")
                
            except Exception as e:
                error_msg = f"患者 {patient[1]} (ID: {patient[0]}): {str(e)}"
                migration_stats["errors"].append(error_msg)
                print(f"   ⚠️  跳过: {error_msg}")
        
        print(f"   ✅ 患者数据迁移完成: {migration_stats['patients']} 条\n")
        
        # ========================================
        # 2. 迁移回访计划
        # ========================================
        print("📋 步骤 2: 迁移回访计划...")
        cursor.execute("SELECT * FROM visit_plans")
        plans = cursor.fetchall()
        
        print(f"   找到 {len(plans)} 个回访计划")
        
        for i, plan in enumerate(plans, 1):
            try:
                plan_data = {
                    "id": plan[0],
                    "patient_id": plan[1],
                    "visit_date": plan[2],
                    "status": plan[3] if len(plan) > 3 else "pending"
                }
                
                # 插入到 Supabase
                supabase.table("visit_plans").upsert(plan_data).execute()
                migration_stats["visit_plans"] += 1
                
                if i % 20 == 0 or i == len(plans):
                    print(f"   ✓ 已迁移 {i}/{len(plans)} 个回访计划")
                
            except Exception as e:
                error_msg = f"回访计划 ID {plan[0]}: {str(e)}"
                migration_stats["errors"].append(error_msg)
                print(f"   ⚠️  跳过: {error_msg}")
        
        print(f"   ✅ 回访计划迁移完成: {migration_stats['visit_plans']} 条\n")
        
        # ========================================
        # 3. 迁移回访记录
        # ========================================
        print("📋 步骤 3: 迁移回访记录...")
        cursor.execute("SELECT * FROM visit_records")
        records = cursor.fetchall()
        
        if records:
            print(f"   找到 {len(records)} 个回访记录")
            
            for i, record in enumerate(records, 1):
                try:
                    record_data = {
                        "id": record[0],
                        "plan_id": record[1],
                        "patient_id": record[2],
                        "visit_date": record[3] if len(record) > 3 else None,
                        "content": record[4] if len(record) > 4 else None,
                        "feedback": record[5] if len(record) > 5 else None,
                        "next_visit_date": record[6] if len(record) > 6 else None
                    }
                    
                    # 插入到 Supabase
                    supabase.table("visit_records").upsert(record_data).execute()
                    migration_stats["visit_records"] += 1
                    
                    if i % 20 == 0 or i == len(records):
                        print(f"   ✓ 已迁移 {i}/{len(records)} 个回访记录")
                    
                except Exception as e:
                    error_msg = f"回访记录 ID {record[0]}: {str(e)}"
                    migration_stats["errors"].append(error_msg)
                    print(f"   ⚠️  跳过: {error_msg}")
            
            print(f"   ✅ 回访记录迁移完成: {migration_stats['visit_records']} 条\n")
        else:
            print("   ℹ️  没有回访记录需要迁移\n")
        
        # ========================================
        # 4. 迁移提醒配置
        # ========================================
        print("📋 步骤 4: 迁移提醒配置...")
        try:
            cursor.execute("SELECT * FROM reminder_settings")
            settings = cursor.fetchall()
            
            if settings:
                for setting in settings:
                    setting_data = {
                        "id": setting[0],
                        "days_before": setting[1],
                        "enabled": setting[2]
                    }
                    supabase.table("reminder_settings").upsert(setting_data).execute()
                
                print(f"   ✅ 提醒配置迁移完成: {len(settings)} 条\n")
            else:
                print("   ℹ️  使用默认提醒配置\n")
        except Exception as e:
            print(f"   ⚠️  提醒配置迁移跳过: {str(e)}\n")
        
        # ========================================
        # 迁移完成总结
        # ========================================
        print("="*60)
        print("  ✅ 数据迁移完成！")
        print("="*60)
        print(f"\n📊 迁移统计:")
        print(f"   - 患者数据: {migration_stats['patients']} 条")
        print(f"   - 回访计划: {migration_stats['visit_plans']} 条")
        print(f"   - 回访记录: {migration_stats['visit_records']} 条")
        
        if migration_stats["errors"]:
            print(f"\n⚠️  错误数量: {len(migration_stats['errors'])}")
            print("\n错误详情:")
            for error in migration_stats["errors"][:10]:  # 只显示前10个错误
                print(f"   - {error}")
            if len(migration_stats["errors"]) > 10:
                print(f"   ... 还有 {len(migration_stats['errors']) - 10} 个错误")
        else:
            print(f"\n✅ 无错误")
        
        print(f"\n💡 下一步:")
        print(f"   1. 在 Streamlit Cloud Secrets 中配置:")
        print(f"      USE_SUPABASE = \"true\"")
        print(f"      SUPABASE_URL = \"{SUPABASE_URL}\"")
        print(f"      SUPABASE_KEY = \"your-anon-key\"")
        print(f"   2. 重新部署应用")
        print(f"   3. 验证数据是否正确")
        
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n" + "="*60)


if __name__ == "__main__":
    print("\n⚠️  警告: 此操作将迁移数据到 Supabase")
    print("建议先备份 SQLite 数据库文件\n")
    
    confirm = input("确认继续？(yes/no): ")
    
    if confirm.lower() == "yes":
        migrate_data()
    else:
        print("❌ 操作已取消")
