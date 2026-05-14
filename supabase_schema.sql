-- ============================================
-- 患者出院回访智能提醒系统 - Supabase 数据库表结构
-- ============================================
-- 使用方法：
-- 1. 登录 Supabase 控制台
-- 2. 进入 SQL Editor
-- 3. 复制粘贴此文件内容
-- 4. 点击 "Run" 执行
-- ============================================

-- 1. 创建患者表
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    discharge_date DATE,
    diagnosis TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    hospital_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE patients IS '患者信息表';
COMMENT ON COLUMN patients.id IS '患者ID（主键）';
COMMENT ON COLUMN patients.name IS '患者姓名';
COMMENT ON COLUMN patients.gender IS '性别';
COMMENT ON COLUMN patients.discharge_date IS '出院日期';
COMMENT ON COLUMN patients.diagnosis IS '诊断结果';
COMMENT ON COLUMN patients.contact_person IS '联系人';
COMMENT ON COLUMN patients.contact_phone IS '联系电话';
COMMENT ON COLUMN patients.hospital_number IS '住院号';

-- 2. 创建回访计划表
CREATE TABLE IF NOT EXISTS visit_plans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'overdue')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE visit_plans IS '回访计划表';
COMMENT ON COLUMN visit_plans.id IS '计划ID（主键）';
COMMENT ON COLUMN visit_plans.patient_id IS '患者ID（外键）';
COMMENT ON COLUMN visit_plans.visit_date IS '回访日期';
COMMENT ON COLUMN visit_plans.status IS '状态：pending-待回访, completed-已完成, overdue-逾期';

-- 3. 创建回访记录表
CREATE TABLE IF NOT EXISTS visit_records (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES visit_plans(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_date DATE,
    content TEXT,
    feedback TEXT,
    next_visit_date DATE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE visit_records IS '回访记录表';
COMMENT ON COLUMN visit_records.id IS '记录ID（主键）';
COMMENT ON COLUMN visit_records.plan_id IS '计划ID（外键）';
COMMENT ON COLUMN visit_records.patient_id IS '患者ID（外键）';
COMMENT ON COLUMN visit_records.visit_date IS '实际回访日期';
COMMENT ON COLUMN visit_records.content IS '回访内容';
COMMENT ON COLUMN visit_records.feedback IS '患者反馈';
COMMENT ON COLUMN visit_records.next_visit_date IS '下次回访日期';
COMMENT ON COLUMN visit_records.created_by IS '创建人';

-- 4. 创建提醒配置表（支持多个配置项）
CREATE TABLE IF NOT EXISTS reminder_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE reminder_settings IS '提醒配置表';
COMMENT ON COLUMN reminder_settings.setting_key IS '配置键名';
COMMENT ON COLUMN reminder_settings.setting_value IS '配置值';
COMMENT ON COLUMN reminder_settings.description IS '配置说明';

-- 插入默认提醒配置
INSERT INTO reminder_settings (setting_key, setting_value, description) VALUES
('advance_days', '0', '提前N天提醒（0表示当天提醒）'),
('reminder_time', '09:00', '每天固定提醒时间（24小时制）'),
('repeat_interval', '24', '重复提醒间隔（小时）'),
('enable_advance_reminder', 'false', '是否启用提前提醒'),
('enable_repeat_reminder', 'true', '是否启用重复提醒')
ON CONFLICT (setting_key) DO NOTHING;

-- 5. 创建索引（优化查询性能）
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_patients_hospital_number ON patients(hospital_number);
CREATE INDEX IF NOT EXISTS idx_patients_discharge_date ON patients(discharge_date);
CREATE INDEX IF NOT EXISTS idx_visit_plans_patient_id ON visit_plans(patient_id);
CREATE INDEX IF NOT EXISTS idx_visit_plans_visit_date ON visit_plans(visit_date);
CREATE INDEX IF NOT EXISTS idx_visit_plans_status ON visit_plans(status);
CREATE INDEX IF NOT EXISTS idx_visit_plans_date_status ON visit_plans(visit_date, status);
CREATE INDEX IF NOT EXISTS idx_visit_records_patient_id ON visit_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_visit_records_plan_id ON visit_records(plan_id);
CREATE INDEX IF NOT EXISTS idx_visit_records_visit_date ON visit_records(visit_date);

-- 6. 启用行级安全（RLS）
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE visit_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE visit_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminder_settings ENABLE ROW LEVEL SECURITY;

-- 7. 创建 RLS 策略（允许所有操作，后续可根据需要细化）
-- 注意：这些策略允许匿名访问，生产环境建议添加用户认证

CREATE POLICY "Enable all access for patients" 
ON patients FOR ALL 
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable all access for visit_plans" 
ON visit_plans FOR ALL 
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable all access for visit_records" 
ON visit_records FOR ALL 
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable all access for reminder_settings" 
ON reminder_settings FOR ALL 
USING (true)
WITH CHECK (true);

-- 8. 创建触发器（自动更新 updated_at）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patients_updated_at 
    BEFORE UPDATE ON patients 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminder_settings_updated_at 
    BEFORE UPDATE ON reminder_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 常用查询示例
-- ============================================

-- 获取所有患者
-- SELECT * FROM patients ORDER BY created_at DESC;

-- 获取今日待回访患者
-- SELECT vp.*, p.name, p.diagnosis, p.contact_phone
-- FROM visit_plans vp
-- JOIN patients p ON vp.patient_id = p.id
-- WHERE vp.visit_date = CURRENT_DATE AND vp.status = 'pending';

-- 获取逾期患者
-- SELECT vp.*, p.name, p.diagnosis, p.contact_phone,
--        (CURRENT_DATE - vp.visit_date) as days_overdue
-- FROM visit_plans vp
-- JOIN patients p ON vp.patient_id = p.id
-- WHERE vp.visit_date < CURRENT_DATE AND vp.status = 'pending';

-- 获取患者及其回访计划
-- SELECT p.*, json_agg(vp) as visit_plans
-- FROM patients p
-- LEFT JOIN visit_plans vp ON p.id = vp.patient_id
-- GROUP BY p.id;

-- ============================================
-- 完成！
-- ============================================
