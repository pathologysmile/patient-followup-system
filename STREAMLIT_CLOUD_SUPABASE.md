# Supabase 云端数据库集成方案

本文档详细说明如何将患者回访系统从 SQLite 迁移到 Supabase（PostgreSQL），实现数据持久化存储。

---

## 📋 为什么需要云端数据库？

### 当前问题

Streamlit Community Cloud 使用**临时文件系统**：
- ❌ 应用重启后数据丢失
- ❌ 重新部署后数据清空
- ❌ 无法多实例共享数据
- ❌ 数据安全性低

### Supabase 优势

- ✅ **数据持久化**：永久存储，不会丢失
- ✅ **免费额度充足**：500 MB 数据库空间
- ✅ **PostgreSQL**：功能强大，支持复杂查询
- ✅ **实时同步**：支持实时更新
- ✅ **安全可靠**：自动备份，高可用
- ✅ **易于集成**：提供 Python SDK

---

## 🚀 快速开始

### 第一步：创建 Supabase 项目

1. 访问：https://supabase.com/
2. 点击 **"Start your project"**
3. 使用 GitHub 账号登录
4. 点击 **"New project"**
5. 填写项目信息：
   - **Name**: `patient-followup-db`
   - **Database Password**: 设置一个强密码（保存好！）
   - **Region**: 选择离你最近的区域（如 Singapore）
6. 点击 **"Create new project"**
7. 等待 2-3 分钟项目创建完成

### 第二步：获取连接信息

项目创建完成后：

1. 进入项目控制台
2. 点击左侧 **"Settings"** → **"API"**
3. 记录以下信息：
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJhbG...`
   - **Service Role Key**: `eyJhbG...`（用于服务器端操作）

⚠️ **重要**：妥善保管这些密钥，不要泄露！

### 第三步：创建数据库表

#### 方法 A：使用 SQL Editor（推荐）

1. 在 Supabase 控制台点击左侧 **"SQL Editor"**
2. 点击 **"New query"**
3. 粘贴以下 SQL 代码：

```sql
-- ============================================
-- 患者回访系统数据库表结构
-- ============================================

-- 1. 患者表
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    discharge_date DATE,
    diagnosis TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    hospital_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 回访计划表
CREATE TABLE visit_plans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    visit_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, overdue
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. 回访记录表
CREATE TABLE visit_records (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES visit_plans(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    visit_date DATE,
    content TEXT,
    feedback TEXT,
    next_visit_date DATE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 提醒配置表
CREATE TABLE reminder_settings (
    id SERIAL PRIMARY KEY,
    days_before INTEGER DEFAULT 1,
    enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入默认提醒配置
INSERT INTO reminder_settings (days_before, enabled) VALUES (1, TRUE);

-- 5. 创建索引（优化查询性能）
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_patients_hospital_number ON patients(hospital_number);
CREATE INDEX idx_visit_plans_patient_id ON visit_plans(patient_id);
CREATE INDEX idx_visit_plans_visit_date ON visit_plans(visit_date);
CREATE INDEX idx_visit_plans_status ON visit_plans(status);
CREATE INDEX idx_visit_records_patient_id ON visit_records(patient_id);
CREATE INDEX idx_visit_records_plan_id ON visit_records(plan_id);
```

4. 点击 **"Run"** 执行 SQL
5. 确认所有表创建成功

#### 方法 B：使用 Table Editor

1. 点击左侧 **"Table Editor"**
2. 手动创建每个表
3. 添加字段和约束

### 第四步：安装 Supabase Python SDK

在项目根目录执行：

```bash
pip install supabase
```

更新 `requirements.txt`：

```txt
streamlit==1.57.0
langchain==1.2.18
langchain-community==0.4.1
langchain-core>=1.3.3
python-dotenv==1.2.2
pandas==2.3.3
pydantic==2.13.4
requests==2.33.1
openpyxl==3.1.5
supabase==2.3.4  # 新增
```

### 第五步：配置 Secrets

在 Streamlit Cloud 的 Secrets 中添加：

```toml
# Supabase 配置
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# 通义千问 API 配置
DASHSCOPE_API_KEY = "sk-your-api-key"
DASHSCOPE_MODEL = "qwen-turbo"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 日志配置
LOG_LEVEL = "INFO"
```

---

## 🔧 代码修改

### 修改 db_manager.py

创建新的数据库管理器以支持 Supabase：

```python
"""
数据库管理器 - 支持 Supabase
"""
import os
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# 导入日志配置
try:
    from logging_config import logger, log_database_operation
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('PatientReminderSystem')
    def log_database_operation(*args, **kwargs):
        pass

# 检测是否使用 Supabase
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

if USE_SUPABASE:
    from supabase import create_client, Client
    
    # 从 Streamlit Secrets 或环境变量获取配置
    if hasattr(st, 'secrets'):
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
    else:
        SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # 创建 Supabase 客户端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ 已连接到 Supabase 数据库")
else:
    # 使用 SQLite（本地开发）
    import sqlite3
    DB_NAME = "patients.db"
    logger.info("📁 使用 SQLite 数据库")


def init_db():
    """初始化数据库"""
    if USE_SUPABASE:
        logger.info("Supabase 数据库已就绪")
        log_database_operation('INIT', 'supabase', success=True)
    else:
        # SQLite 初始化逻辑（原有代码）
        logger.info("数据库初始化开始")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            # ... 原有 SQLite 初始化代码
            conn.commit()
            logger.info("数据库初始化成功")
            log_database_operation('INIT', 'sqlite', success=True)
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
            log_database_operation('INIT', 'sqlite', success=False, error_msg=str(e))
            raise
        finally:
            conn.close()


def add_patient(name, gender, discharge_date, visit_dates, diagnosis, 
                contact_person, contact_phone, hospital_number=None):
    """添加新患者"""
    logger.info(f"添加患者 | 姓名: {name} | 住院号: {hospital_number or '无'}")
    
    if USE_SUPABASE:
        return _add_patient_supabase(name, gender, discharge_date, visit_dates, 
                                     diagnosis, contact_person, contact_phone, 
                                     hospital_number)
    else:
        return _add_patient_sqlite(name, gender, discharge_date, visit_dates, 
                                   diagnosis, contact_person, contact_phone, 
                                   hospital_number)


def _add_patient_supabase(name, gender, discharge_date, visit_dates, diagnosis, 
                          contact_person, contact_phone, hospital_number=None):
    """使用 Supabase 添加患者"""
    try:
        # 1. 插入患者数据
        patient_data = {
            "name": name,
            "gender": gender,
            "discharge_date": discharge_date,
            "diagnosis": diagnosis,
            "contact_person": contact_person,
            "contact_phone": contact_phone,
            "hospital_number": hospital_number
        }
        
        response = supabase.table("patients").insert(patient_data).execute()
        patient_id = response.data[0]["id"]
        
        # 2. 插入回访计划
        plans_data = []
        for visit_date in visit_dates:
            plans_data.append({
                "patient_id": patient_id,
                "visit_date": visit_date,
                "status": "pending"
            })
        
        if plans_data:
            supabase.table("visit_plans").insert(plans_data).execute()
        
        logger.info(f"患者添加成功 | ID: {patient_id} | 回访计划数: {len(visit_dates)}")
        log_database_operation('INSERT', 'patients + visit_plans (Supabase)', success=True)
        
        return patient_id
        
    except Exception as e:
        logger.error(f"患者添加失败 | 姓名: {name} | 错误: {str(e)}", exc_info=True)
        log_database_operation('INSERT', 'patients + visit_plans (Supabase)', 
                              success=False, error_msg=str(e))
        raise


def _add_patient_sqlite(name, gender, discharge_date, visit_dates, diagnosis, 
                        contact_person, contact_phone, hospital_number=None):
    """使用 SQLite 添加患者（原有代码）"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # ... 原有 SQLite 代码
        pass
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_patients():
    """获取所有患者"""
    if USE_SUPABASE:
        return _get_all_patients_supabase()
    else:
        return _get_all_patients_sqlite()


def _get_all_patients_supabase():
    """使用 Supabase 获取所有患者"""
    try:
        # 查询患者数据
        response = supabase.table("patients").select("*").execute()
        patients = response.data
        
        # 为每个患者关联回访计划
        result = []
        for patient in patients:
            patient_id = patient["id"]
            
            # 查询该患者的回访计划
            plans_response = supabase.table("visit_plans").select("*").eq("patient_id", patient_id).execute()
            plans = plans_response.data
            
            # 格式化数据（与 SQLite 返回格式一致）
            patient_tuple = (
                patient["id"],
                patient["name"],
                patient["gender"],
                patient["discharge_date"],
                patient["diagnosis"],
                patient["contact_person"],
                patient["contact_phone"],
                patient["hospital_number"],
                patient["created_at"],
                plans  # 回访计划列表
            )
            result.append(patient_tuple)
        
        logger.info(f"获取所有患者 | 数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取患者失败 | 错误: {str(e)}", exc_info=True)
        raise


def _get_all_patients_sqlite():
    """使用 SQLite 获取所有患者（原有代码）"""
    # ... 原有代码
    pass


def get_due_patients():
    """获取今日待回访患者"""
    if USE_SUPABASE:
        return _get_due_patients_supabase()
    else:
        return _get_due_patients_sqlite()


def _get_due_patients_supabase():
    """使用 Supabase 获取今日待回访患者"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 查询今日的回访计划
        response = supabase.table("visit_plans").select("*").eq("visit_date", today).eq("status", "pending").execute()
        plans = response.data
        
        # 获取关联的患者信息
        result = []
        for plan in plans:
            patient_id = plan["patient_id"]
            patient_response = supabase.table("patients").select("*").eq("id", patient_id).execute()
            
            if patient_response.data:
                patient = patient_response.data[0]
                result.append({
                    "plan_id": plan["id"],
                    "patient_id": patient_id,
                    "name": patient["name"],
                    "visit_date": plan["visit_date"],
                    "diagnosis": patient["diagnosis"],
                    "contact_phone": patient["contact_phone"]
                })
        
        logger.info(f"获取今日待回访患者 | 数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取待回访患者失败 | 错误: {str(e)}", exc_info=True)
        raise


def get_overdue_patients():
    """获取逾期患者"""
    if USE_SUPABASE:
        return _get_overdue_patients_supabase()
    else:
        return _get_overdue_patients_sqlite()


def _get_overdue_patients_supabase():
    """使用 Supabase 获取逾期患者"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 查询逾期的回访计划
        response = supabase.table("visit_plans").select("*").lt("visit_date", today).eq("status", "pending").execute()
        plans = response.data
        
        # 获取关联的患者信息
        result = []
        for plan in plans:
            patient_id = plan["patient_id"]
            patient_response = supabase.table("patients").select("*").eq("id", patient_id).execute()
            
            if patient_response.data:
                patient = patient_response.data[0]
                result.append({
                    "plan_id": plan["id"],
                    "patient_id": patient_id,
                    "name": patient["name"],
                    "visit_date": plan["visit_date"],
                    "diagnosis": patient["diagnosis"],
                    "contact_phone": patient["contact_phone"],
                    "days_overdue": (datetime.now() - datetime.strptime(plan["visit_date"], "%Y-%m-%d")).days
                })
        
        logger.info(f"获取逾期患者 | 数量: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取逾期患者失败 | 错误: {str(e)}", exc_info=True)
        raise


def complete_visit(plan_id, content, feedback, next_visit_date=None):
    """完成回访"""
    if USE_SUPABASE:
        return _complete_visit_supabase(plan_id, content, feedback, next_visit_date)
    else:
        return _complete_visit_sqlite(plan_id, content, feedback, next_visit_date)


def _complete_visit_supabase(plan_id, content, feedback, next_visit_date=None):
    """使用 Supabase 完成回访"""
    try:
        # 1. 更新回访计划状态
        supabase.table("visit_plans").update({"status": "completed"}).eq("id", plan_id).execute()
        
        # 2. 获取计划信息
        plan_response = supabase.table("visit_plans").select("*").eq("id", plan_id).execute()
        plan = plan_response.data[0]
        patient_id = plan["patient_id"]
        
        # 3. 创建回访记录
        record_data = {
            "plan_id": plan_id,
            "patient_id": patient_id,
            "visit_date": datetime.now().strftime("%Y-%m-%d"),
            "content": content,
            "feedback": feedback,
            "next_visit_date": next_visit_date
        }
        
        supabase.table("visit_records").insert(record_data).execute()
        
        logger.info(f"回访完成 | Plan ID: {plan_id}")
        log_database_operation('UPDATE', 'visit_plans + visit_records (Supabase)', success=True)
        
    except Exception as e:
        logger.error(f"完成回访失败 | Plan ID: {plan_id} | 错误: {str(e)}", exc_info=True)
        log_database_operation('UPDATE', 'visit_plans + visit_records (Supabase)', 
                              success=False, error_msg=str(e))
        raise


# ... 其他函数类似修改
```

### 修改 app.py

在文件开头添加环境检测：

```python
import os
import streamlit as st

# 检测是否使用 Supabase
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

if USE_SUPABASE:
    st.sidebar.success("🌐 已连接到云端数据库 (Supabase)")
else:
    st.sidebar.info("💾 使用本地数据库 (SQLite)")
```

---

## 📊 数据迁移

### 从 SQLite 迁移到 Supabase

创建迁移脚本 `migrate_to_supabase.py`：

```python
"""
从 SQLite 迁移数据到 Supabase
"""
import sqlite3
import os
from supabase import create_client, Client
from datetime import datetime

# SQLite 配置
SQLITE_DB = "patients.db"

# Supabase 配置
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-service-role-key"  # 使用 service role key

# 创建 Supabase 客户端
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_data():
    """迁移数据"""
    print("开始迁移数据...")
    
    # 连接 SQLite
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    try:
        # 1. 迁移患者数据
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        
        print(f"找到 {len(patients)} 个患者")
        
        for patient in patients:
            patient_data = {
                "id": patient[0],
                "name": patient[1],
                "gender": patient[2],
                "discharge_date": patient[3],
                "diagnosis": patient[4],
                "contact_person": patient[5],
                "contact_phone": patient[6],
                "hospital_number": patient[7] if len(patient) > 7 else None
            }
            
            # 插入到 Supabase
            supabase.table("patients").insert(patient_data).execute()
            print(f"  ✓ 迁移患者: {patient[1]}")
        
        # 2. 迁移回访计划
        cursor.execute("SELECT * FROM visit_plans")
        plans = cursor.fetchall()
        
        print(f"找到 {len(plans)} 个回访计划")
        
        for plan in plans:
            plan_data = {
                "id": plan[0],
                "patient_id": plan[1],
                "visit_date": plan[2],
                "status": plan[3] if len(plan) > 3 else "pending"
            }
            
            supabase.table("visit_plans").insert(plan_data).execute()
        
        print(f"  ✓ 迁移 {len(plans)} 个回访计划")
        
        # 3. 迁移回访记录
        cursor.execute("SELECT * FROM visit_records")
        records = cursor.fetchall()
        
        if records:
            print(f"找到 {len(records)} 个回访记录")
            
            for record in records:
                record_data = {
                    "id": record[0],
                    "plan_id": record[1],
                    "patient_id": record[2],
                    "visit_date": record[3],
                    "content": record[4],
                    "feedback": record[5],
                    "next_visit_date": record[6] if len(record) > 6 else None
                }
                
                supabase.table("visit_records").insert(record_data).execute()
            
            print(f"  ✓ 迁移 {len(records)} 个回访记录")
        
        print("\n✅ 数据迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_data()
```

运行迁移：

```bash
python migrate_to_supabase.py
```

---

## 🎯 切换数据库

### 本地开发（使用 SQLite）

`.env` 文件：
```env
USE_SUPABASE=false
```

### 生产环境（使用 Supabase）

在 Streamlit Cloud Secrets 中：
```toml
USE_SUPABASE = "true"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

---

## 💰 Supabase 免费额度

| 资源 | 免费额度 | 说明 |
|------|---------|------|
| 数据库空间 | 500 MB | 足够存储数万条患者记录 |
| 带宽 | 2 GB/月 | 足够小型应用使用 |
| API 请求 | 无限制 | 实际受速率限制 |
| 认证用户 | 50,000 | 如需用户系统 |
| 存储 | 1 GB | 文件存储 |

**超出后价格**：
- 额外数据库空间：$0.125/GB/月
- 额外带宽：$0.09/GB

对于患者回访系统，免费额度完全够用！

---

## 🔒 安全建议

### 1. 密钥管理

- ✅ 使用 Streamlit Secrets 存储 Supabase 密钥
- ✅ 不要在代码中硬编码密钥
- ✅ 定期轮换密钥
- ✅ 使用 Row Level Security (RLS)

### 2. 启用 RLS（行级安全）

在 Supabase SQL Editor 中执行：

```sql
-- 启用 RLS
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE visit_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE visit_records ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作，后续可根据需要细化）
CREATE POLICY "Enable all access" ON patients FOR ALL USING (true);
CREATE POLICY "Enable all access" ON visit_plans FOR ALL USING (true);
CREATE POLICY "Enable all access" ON visit_records FOR ALL USING (true);
```

### 3. 备份策略

- ✅ Supabase 自动每日备份
- ✅ 保留 7 天备份
- ✅ 可手动触发备份
- ✅ 建议定期导出 CSV 备份

---

## 📈 性能优化

### 1. 索引优化

已创建的索引：
- 患者姓名
- 住院号
- 回访计划患者ID
- 回访计划日期
- 回访计划状态

### 2. 查询优化

```python
# 使用 select 指定字段，减少数据传输
response = supabase.table("patients").select("id,name,discharge_date").execute()

# 使用 filter 减少数据量
response = supabase.table("visit_plans").select("*").eq("status", "pending").execute()

# 使用 limit 分页
response = supabase.table("patients").select("*").range(0, 99).execute()
```

### 3. 缓存策略

结合 Streamlit 缓存：

```python
@st.cache_data(ttl=300)
def get_cached_patients():
    return db_manager.get_all_patients()
```

---

## 🆘 常见问题

### Q1: 连接超时

**解决**：
- 检查网络连接
- 确认 SUPABASE_URL 正确
- 检查防火墙设置

### Q2: 权限错误

**解决**：
- 确认使用了正确的密钥（anon vs service_role）
- 检查 RLS 策略
- 查看 Supabase 日志

### Q3: 数据不一致

**解决**：
- 检查外键约束
- 确认事务完整性
- 使用批量操作时注意顺序

---

## 📞 获取帮助

- Supabase 文档：https://supabase.com/docs
- Supabase Discord：https://discord.supabase.com
- 本项目 Issues：https://github.com/pathologysmile/patient-followup-system/issues

---

**最后更新**：2026-05-13  
**文档版本**：1.0.0
