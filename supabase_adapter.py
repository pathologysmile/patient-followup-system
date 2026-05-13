"""
Supabase 数据库适配器
为患者回访系统提供 Supabase 支持

使用方法：
1. 安装依赖: pip install supabase
2. 配置环境变量或使用 Streamlit Secrets
3. 在 db_manager.py 中导入并使用
"""
import os
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


class SupabaseAdapter:
    """Supabase 数据库适配器"""
    
    def __init__(self):
        """初始化 Supabase 客户端"""
        try:
            from supabase import create_client, Client
            
            # 从环境变量或 Streamlit Secrets 获取配置
            SUPABASE_URL = os.getenv("SUPABASE_URL", "")
            SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
            
            # 尝试从 Streamlit Secrets 读取
            if not SUPABASE_URL or not SUPABASE_KEY:
                try:
                    import streamlit as st
                    if hasattr(st, 'secrets'):
                        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
                        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
                except:
                    pass
            
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("Supabase URL 和 Key 未配置")
            
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase 客户端初始化成功")
            
        except ImportError:
            logger.error("❌ 未安装 Supabase SDK，请运行: pip install supabase")
            raise
        except Exception as e:
            logger.error(f"❌ Supabase 客户端初始化失败: {str(e)}")
            raise
    
    def add_patient(self, name, gender, discharge_date, visit_dates, diagnosis, 
                   contact_person, contact_phone, hospital_number=None):
        """添加新患者"""
        logger.info(f"添加患者 | 姓名: {name} | 住院号: {hospital_number or '无'}")
        
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
            
            response = self.client.table("patients").insert(patient_data).execute()
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
                self.client.table("visit_plans").insert(plans_data).execute()
            
            logger.info(f"患者添加成功 | ID: {patient_id} | 回访计划数: {len(visit_dates)}")
            log_database_operation('INSERT', 'patients + visit_plans (Supabase)', success=True)
            
            return patient_id
            
        except Exception as e:
            logger.error(f"患者添加失败 | 姓名: {name} | 错误: {str(e)}", exc_info=True)
            log_database_operation('INSERT', 'patients + visit_plans (Supabase)', 
                                  success=False, error_msg=str(e))
            raise
    
    def get_all_patients(self):
        """获取所有患者"""
        try:
            # 查询患者数据
            response = self.client.table("patients").select("*").order("created_at", desc=True).execute()
            patients = response.data
            
            result = []
            for patient in patients:
                patient_id = patient["id"]
                
                # 查询该患者的回访计划
                plans_response = self.client.table("visit_plans").select("*").eq("patient_id", patient_id).order("visit_date").execute()
                plans = plans_response.data
                
                # 计算整体状态
                has_pending = any(p["status"] == "pending" for p in plans)
                all_completed = all(p["status"] == "completed" for p in plans) if plans else False
                
                if all_completed and plans:
                    overall_status = 'completed'
                elif has_pending:
                    overall_status = 'pending'
                else:
                    overall_status = 'pending'
                
                # 格式化数据（与 SQLite 返回格式一致）
                patient_dict = {
                    "id": patient_id,
                    "name": patient["name"],
                    "gender": patient.get("gender"),
                    "hospital_number": patient.get("hospital_number"),
                    "discharge_date": patient.get("discharge_date"),
                    "visit_dates": [p["visit_date"] for p in plans],
                    "visit_date": plans[0]["visit_date"] if plans else None,
                    "diagnosis": patient.get("diagnosis"),
                    "contact_person": patient.get("contact_person"),
                    "contact_phone": patient.get("contact_phone"),
                    "status": overall_status,
                    "created_at": patient.get("created_at"),
                    "visit_plans": [{
                        "plan_id": p["id"],
                        "visit_date": p["visit_date"],
                        "visit_type": p.get("visit_type", "常规回访"),
                        "status": p["status"],
                        "completed_at": p.get("completed_at")
                    } for p in plans]
                }
                
                result.append(patient_dict)
            
            logger.info(f"获取所有患者 | 数量: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取患者失败 | 错误: {str(e)}", exc_info=True)
            raise
    
    def get_due_patients(self):
        """获取今日待回访患者"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 查询今日的回访计划
            response = self.client.table("visit_plans").select("*").eq("visit_date", today).eq("status", "pending").execute()
            plans = response.data
            
            # 获取关联的患者信息
            result = []
            for plan in plans:
                patient_id = plan["patient_id"]
                patient_response = self.client.table("patients").select("*").eq("id", patient_id).execute()
                
                if patient_response.data:
                    patient = patient_response.data[0]
                    result.append({
                        "name": patient["name"],
                        "gender": patient.get("gender"),
                        "diagnosis": patient.get("diagnosis"),
                        "visit_date": plan["visit_date"],
                        "contact_person": patient.get("contact_person"),
                        "contact_phone": patient.get("contact_phone"),
                        "plan_id": plan["id"],
                        "urgency": "今日紧急"
                    })
            
            logger.info(f"获取今日待回访患者 | 数量: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取待回访患者失败 | 错误: {str(e)}", exc_info=True)
            raise
    
    def get_overdue_patients(self):
        """获取逾期患者"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 查询逾期的回访计划
            response = self.client.table("visit_plans").select("*").lt("visit_date", today).eq("status", "pending").execute()
            plans = response.data
            
            # 获取关联的患者信息
            result = []
            for plan in plans:
                patient_id = plan["patient_id"]
                patient_response = self.client.table("patients").select("*").eq("id", patient_id).execute()
                
                if patient_response.data:
                    patient = patient_response.data[0]
                    visit_date = datetime.strptime(plan["visit_date"], "%Y-%m-%d")
                    days_overdue = (datetime.now() - visit_date).days
                    
                    result.append({
                        "name": patient["name"],
                        "gender": patient.get("gender"),
                        "diagnosis": patient.get("diagnosis"),
                        "visit_date": plan["visit_date"],
                        "contact_person": patient.get("contact_person"),
                        "contact_phone": patient.get("contact_phone"),
                        "plan_id": plan["id"],
                        "days_overdue": days_overdue,
                        "urgency": f"逾期{days_overdue}天"
                    })
            
            logger.info(f"获取逾期患者 | 数量: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取逾期患者失败 | 错误: {str(e)}", exc_info=True)
            raise
    
    def complete_visit(self, plan_id, content, feedback, next_visit_date=None):
        """完成回访"""
        try:
            # 1. 更新回访计划状态
            self.client.table("visit_plans").update({"status": "completed"}).eq("id", plan_id).execute()
            
            # 2. 获取计划信息
            plan_response = self.client.table("visit_plans").select("*").eq("id", plan_id).execute()
            plan = plan_response.data[0]
            patient_id = plan["patient_id"]
            
            # 3. 创建回访记录
            record_data = {
                "plan_id": plan_id,
                "patient_id": patient_id,
                "visit_date": datetime.now().strftime("%Y-%m-%d"),
                "record_content": content,
                "patient_feedback": feedback,
                "next_visit_date": next_visit_date
            }
            
            self.client.table("visit_records").insert(record_data).execute()
            
            logger.info(f"回访完成 | Plan ID: {plan_id}")
            log_database_operation('UPDATE', 'visit_plans + visit_records (Supabase)', success=True)
            
        except Exception as e:
            logger.error(f"完成回访失败 | Plan ID: {plan_id} | 错误: {str(e)}", exc_info=True)
            log_database_operation('UPDATE', 'visit_plans + visit_records (Supabase)', 
                                  success=False, error_msg=str(e))
            raise
    
    def update_visit_plan_status(self, plan_id, status):
        """更新回访计划状态"""
        try:
            update_data = {"status": status}
            if status == "completed":
                update_data["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.client.table("visit_plans").update(update_data).eq("id", plan_id).execute()
            logger.info(f"更新回访计划状态 | Plan ID: {plan_id} | Status: {status}")
            
        except Exception as e:
            logger.error(f"更新回访计划状态失败 | Plan ID: {plan_id} | 错误: {str(e)}", exc_info=True)
            raise
    
    def import_patients_from_csv(self, csv_data):
        """从 CSV 批量导入患者"""
        logger.info(f"CSV批量导入开始 | 记录数: {len(csv_data)}")
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            for i, row in enumerate(csv_data, 1):
                try:
                    # 提取字段
                    name = str(row.get('姓名', '')).strip()
                    gender = str(row.get('性别', '')).strip()
                    hospital_number = str(row.get('住院号', '')).strip() if row.get('住院号') else None
                    discharge_date = str(row.get('出院日期', '')).strip()
                    visit_date = str(row.get('回访日期', '')).strip()
                    diagnosis = str(row.get('诊断', '')).strip()
                    contact_person = str(row.get('联系人', '')).strip()
                    contact_phone = str(row.get('联系电话', '')).strip()
                    status = str(row.get('状态', 'pending')).strip()
                    
                    # 验证必填字段
                    if not all([name, gender, discharge_date, visit_date, diagnosis, contact_person, contact_phone]):
                        error_count += 1
                        errors.append(f"第{i}行：缺少必填字段")
                        continue
                    
                    # 插入患者
                    patient_data = {
                        "name": name,
                        "gender": gender,
                        "hospital_number": hospital_number,
                        "discharge_date": discharge_date,
                        "diagnosis": diagnosis,
                        "contact_person": contact_person,
                        "contact_phone": contact_phone
                    }
                    
                    response = self.client.table("patients").insert(patient_data).execute()
                    patient_id = response.data[0]["id"]
                    
                    # 插入回访计划
                    plan_data = {
                        "patient_id": patient_id,
                        "visit_date": visit_date,
                        "status": status
                    }
                    
                    self.client.table("visit_plans").insert(plan_data).execute()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"第{i}行 ({row.get('姓名', '未知')}): {str(e)}"
                    errors.append(error_msg)
                    logger.warning(f"CSV导入跳过记录 | {error_msg}")
            
            logger.info(f"CSV批量导入完成 | 成功: {success_count} | 失败: {error_count}")
            log_database_operation('BATCH_INSERT', 'patients + visit_plans (Supabase)', success=True)
            
        except Exception as e:
            logger.error(f"CSV批量导入失败 | 错误: {str(e)}", exc_info=True)
            log_database_operation('BATCH_INSERT', 'patients + visit_plans (Supabase)', 
                                  success=False, error_msg=str(e))
            raise
        
        return success_count, error_count, errors
    
    def get_reminder_settings(self):
        """获取提醒配置"""
        try:
            response = self.client.table("reminder_settings").select("*").execute()
            settings = response.data
            
            # 转换为字典格式
            result = {}
            for setting in settings:
                result[setting["setting_key"]] = setting["setting_value"]
            
            return result
            
        except Exception as e:
            logger.error(f"获取提醒配置失败 | 错误: {str(e)}", exc_info=True)
            # 返回默认配置
            return {
                'advance_days': '0',
                'reminder_time': '09:00',
                'repeat_interval': '24',
                'enable_advance_reminder': 'false',
                'enable_repeat_reminder': 'true'
            }
    
    def update_reminder_setting(self, key, value):
        """更新提醒配置"""
        try:
            self.client.table("reminder_settings").update({
                "setting_value": value
            }).eq("setting_key", key).execute()
            
            logger.info(f"更新提醒配置 | Key: {key} | Value: {value}")
            
        except Exception as e:
            logger.error(f"更新提醒配置失败 | Key: {key} | 错误: {str(e)}", exc_info=True)
            raise


# 创建全局实例
supabase_adapter = None

def get_supabase_adapter():
    """获取 Supabase 适配器实例（单例模式）"""
    global supabase_adapter
    
    if supabase_adapter is None:
        supabase_adapter = SupabaseAdapter()
    
    return supabase_adapter
