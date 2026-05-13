import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import db_manager
import ai_agent
import ui_styles
import logging_config
from logging_config import logger, log_user_action, log_system_event, log_database_operation

# 页面配置
st.set_page_config(
    page_title="患者出院回访智能提醒系统",
    page_icon="🏥",
    layout="wide"
)

# 注入自定义CSS样式
st.markdown(ui_styles.BASE_CSS, unsafe_allow_html=True)

# 记录系统启动日志
log_system_event('系统启动', '患者回访系统已启动', 'INFO')
logger.info("="*50)
logger.info("系统启动 - 患者出院回访智能提醒系统")
logger.info("="*50)

# ===== 数据缓存机制 =====
@st.cache_data(ttl=300)  # 5分钟过期
def get_cached_all_patients():
    """
    获取缓存的患者数据
    
    缓存策略：
    - TTL: 300秒（5分钟）
    - 适用于：Dashboard、数据查看等频繁查询场景
    - 数据更新后自动失效
    
    返回:
        list: 患者数据列表
    """
    try:
        patients = db_manager.get_all_patients()
        logger.info(f"数据加载 | 获取所有患者数据 | 数量: {len(patients)}")
        return patients
    except Exception as e:
        logger.error(f"数据加载失败 | 获取所有患者数据 | 错误: {str(e)}", exc_info=True)
        raise


@st.cache_data(ttl=60)  # 1分钟过期
def get_cached_due_patients():
    """
    获取缓存的今日待回访患者
    
    缓存策略：
    - TTL: 60秒（1分钟）
    - 适用于：Dashboard实时提醒
    
    返回:
        list: 今日待回访患者列表
    """
    try:
        patients = db_manager.get_due_patients()
        logger.info(f"数据加载 | 获取今日待回访患者 | 数量: {len(patients)}")
        return patients
    except Exception as e:
        logger.error(f"数据加载失败 | 获取今日待回访患者 | 错误: {str(e)}", exc_info=True)
        raise


@st.cache_data(ttl=60)  # 1分钟过期
def get_cached_overdue_patients():
    """
    获取缓存的逾期患者
    
    缓存策略：
    - TTL: 60秒（1分钟）
    - 适用于：Dashboard逾期提醒
    
    返回:
        list: 逾期患者列表
    """
    try:
        patients = db_manager.get_overdue_patients()
        logger.info(f"数据加载 | 获取逾期患者 | 数量: {len(patients)}")
        return patients
    except Exception as e:
        logger.error(f"数据加载失败 | 获取逾期患者 | 错误: {str(e)}", exc_info=True)
        raise


@st.cache_data(ttl=600)  # 10分钟过期
def get_cached_reminder_settings():
    """
    获取缓存的提醒配置
    
    缓存策略：
    - TTL: 600秒（10分钟）
    - 适用于：配置信息，变化频率低
    
    返回:
        dict: 提醒配置字典
    """
    try:
        settings = db_manager.get_reminder_settings()
        logger.debug(f"配置加载 | 获取提醒配置")
        return settings
    except Exception as e:
        logger.error(f"配置加载失败 | 获取提醒配置 | 错误: {str(e)}", exc_info=True)
        raise


def clear_data_cache():
    """清除所有数据缓存"""
    st.cache_data.clear()
    logger.info("缓存清理 | 已清除所有数据缓存")
    log_system_event('缓存清理', '已清除所有数据缓存', 'INFO')

# 初始化会话状态
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 侧边栏导航
with st.sidebar:
    st.title("🏥 患者出院回访智能提醒系统")
    st.markdown("---")
    
    # 页面导航按钮
    if st.button("📊 智能提醒看板", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
        st.session_state.page = 'dashboard'
    
    if st.button("📋 患者数据查看", use_container_width=True, type="primary" if st.session_state.page == 'data' else "secondary"):
        st.session_state.page = 'data'
    
    if st.button("💬 智能体对话", use_container_width=True, type="primary" if st.session_state.page == 'chat' else "secondary"):
        st.session_state.page = 'chat'
    
    if st.button("🔧 数据管理", use_container_width=True, type="primary" if st.session_state.page == 'admin' else "secondary"):
        st.session_state.page = 'admin'
    
    if st.button("⚙️ 提醒设置", use_container_width=True, type="primary" if st.session_state.page == 'settings' else "secondary"):
        st.session_state.page = 'settings'
    
    if st.button("📈 数据分析", use_container_width=True, type="primary" if st.session_state.page == 'analytics' else "secondary"):
        st.session_state.page = 'analytics'
    
    st.markdown("---")
    
    # 缓存控制
    st.markdown("### 🔄 数据缓存")
    st.caption("💡 提示：系统自动缓存数据以提升性能，如需立即查看最新数据可手动刷新")
    
    if st.button("🔄 刷新数据", use_container_width=True):
        clear_data_cache()
        st.success("✅ 缓存已清除，数据将重新加载")
        log_user_action('刷新缓存', '', '手动清除数据缓存')
        st.rerun()
    
    st.markdown("---")
    
    # CSV 导入功能
    st.header("📥 CSV 批量导入")
    
    # 提供模板下载
    st.markdown("### 📋 导入说明")
    st.info("""
    **CSV 文件格式要求：**
    - 必需列：姓名、性别、出院日期、回访日期、诊断、联系人、联系电话
    - 可选列：住院号、状态
    - 日期格式：YYYY-MM-DD（例如：2026-05-10）
    - 性别：男 或 女
    - 状态：pending（待回访）或 completed（已完成），默认为 pending
    """)
    
    # 创建示例数据
    sample_data = {
        '姓名': ['张三', '李四', '王五'],
        '性别': ['男', '女', '男'],
        '住院号': ['202605051705', '202605061234', '202605071890'],
        '出院日期': ['2026-05-05', '2026-05-06', '2026-05-07'],
        '回访日期': ['2026-05-12', '2026-05-13', '2026-05-14'],
        '诊断': ['胃癌术后', '糖尿病', '高血压'],
        '联系人': ['张家属', '李家属', '王家属'],
        '联系电话': ['13800138001', '13800138002', '13800138003'],
        '状态': ['pending', 'pending', 'pending']
    }
    
    sample_df = pd.DataFrame(sample_data)
    
    # 提供下载按钮
    col_download1, col_download2 = st.columns([1, 3])
    with col_download1:
        if st.button("📥 下载模板", use_container_width=True):
            # 生成 CSV 文件
            csv_content = sample_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="💾 点击下载",
                data=csv_content,
                file_name="患者导入模板.csv",
                mime="text/csv",
                use_container_width=True
            )
    with col_download2:
        st.caption("点击下载标准格式的 CSV 模板文件")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("选择 CSV 文件", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # 读取 CSV 文件
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            st.info(f"📄 检测到 {len(df)} 条记录")
            
            # 显示预览
            with st.expander("👀 预览数据", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            
            # 验证列名
            required_columns = ['姓名', '性别', '出院日期', '回访日期', '诊断', '联系人', '联系电话']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ CSV 文件缺少必需列: {', '.join(missing_columns)}")
            else:
                # 转换 DataFrame 为字典列表
                csv_data = df.to_dict('records')
                
                # 确认导入
                if st.button("🚀 开始导入", type="primary", use_container_width=True):
                    with st.spinner("正在导入数据..."):
                        success_count, error_count, errors = db_manager.import_patients_from_csv(csv_data)
                    
                    # 显示结果
                    if success_count > 0:
                        st.success(f"✅ 成功导入 {success_count} 个患者")
                    
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} 条记录导入失败")
                        with st.expander("查看错误详情"):
                            for error in errors:
                                st.text(error)
                    
                    if success_count > 0:
                        st.balloons()
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ 读取 CSV 文件失败: {str(e)}")
    
    st.markdown("---")
    
    # 新患者登记表单（始终显示）
    st.header("📝 新患者出院登记")
    
    # 初始化会话状态存储回访日期列表
    if 'visit_dates_list' not in st.session_state:
        st.session_state.visit_dates_list = [datetime.now()]
    
    # 多回访日期设置（在表单外）
    st.markdown("#### 📅 设置回访日期")
    st.caption("💡 提示：可以设置多个回访日期，例如：出院后7天、30天、90天")
    
    # 显示已添加的回访日期
    visit_dates_to_remove = []
    for i, vdate in enumerate(st.session_state.visit_dates_list):
        col_date, col_btn = st.columns([4, 1])
        with col_date:
            new_date = st.date_input(
                f"回访日期 {i+1}",
                value=vdate,
                key=f"visit_date_{i}"
            )
            st.session_state.visit_dates_list[i] = new_date
        with col_btn:
            if len(st.session_state.visit_dates_list) > 1:
                if st.button("❌", key=f"remove_date_{i}"):
                    visit_dates_to_remove.append(i)
    
    # 删除标记的日期
    for idx in sorted(visit_dates_to_remove, reverse=True):
        st.session_state.visit_dates_list.pop(idx)
    
    # 添加新日期按钮（在表单外）
    if st.button("➕ 添加回访日期", use_container_width=True, key="add_visit_date_btn"):
        st.session_state.visit_dates_list.append(datetime.now())
        st.rerun()
    
    # 表单开始
    with st.form("add_patient_form"):
        col0, col1 = st.columns(2)
        with col0:
            hospital_number = st.text_input("住院号")
        with col1:
            name = st.text_input("患者姓名")
        
        col2, col3 = st.columns(2)
        with col2:
            gender = st.selectbox("性别", ["男", "女"])
        with col3:
            discharge_date = st.date_input("出院日期", value=datetime.now())
        
        diagnosis = st.text_area("出院诊断")
        
        col6, col7 = st.columns(2)
        with col6:
            contact_person = st.text_input("联系人")
        with col7:
            contact_phone = st.text_input("联系电话")
        
        submitted = st.form_submit_button("保存档案")
        
        if submitted:
            if name and diagnosis and contact_person and contact_phone:
                # 转换回访日期列表为字符串格式
                visit_dates_str = [d.strftime('%Y-%m-%d') for d in st.session_state.visit_dates_list]
                
                try:
                    db_manager.add_patient(
                        name, 
                        gender,
                        discharge_date.strftime('%Y-%m-%d'), 
                        visit_dates_str,  # 多个回访日期
                        diagnosis,
                        contact_person,
                        contact_phone,
                        hospital_number if hospital_number else None  # 住院号（可选）
                    )
                    log_user_action('新增患者', f'姓名: {name}', f'住院号: {hospital_number or "无"}')
                    log_database_operation('INSERT', 'patients + visit_plans', success=True)
                    
                    # 清除缓存，确保数据立即更新
                    clear_data_cache()
                    
                    st.success(f"✅ {name} 的档案已保存！共设置 {len(visit_dates_str)} 个回访日期")
                    # 重置回访日期列表
                    st.session_state.visit_dates_list = [datetime.now()]
                except Exception as e:
                    logger.error(f"患者登记失败 | 姓名: {name} | 错误: {str(e)}", exc_info=True)
                    log_database_operation('INSERT', 'patients + visit_plans', success=False, error_msg=str(e))
                    st.error(f"❌ 保存失败: {str(e)}")
            else:
                st.error("请填写完整信息")

# 根据选择的页面显示不同内容
if st.session_state.page == 'dashboard':
    # --- 主视图：智能提醒看板（全新医疗SaaS风格）---
    
    # 页面标题
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">{ui_styles.get_icon_html("chart-bar", size="lg", color=ui_styles.PRIMARY_COLOR)} 智能提醒看板</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">实时监控患者回访状态，提升医疗服务质量</p>', unsafe_allow_html=True)
    
    # 显示加载状态指示器
    loading_placeholder = st.empty()
    with loading_placeholder:
        st.markdown('''
        <div style="padding: 2rem;">
            <div class="skeleton skeleton-title" style="width: 40%; margin-bottom: 1rem;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
        </div>
        ''', unsafe_allow_html=True)
    
    # ⚠️ 首先检查是否有过期未回访的患者（忘记回访）
    try:
        overdue_patients = get_cached_overdue_patients()
        log_database_operation('SELECT', 'visit_plans + patients (overdue)', success=True)
    except Exception as e:
        loading_placeholder.empty()
        logger.error(f"Dashboard加载失败 | 获取逾期患者 | 错误: {str(e)}", exc_info=True)
        st.markdown(f'''
        <div class="alert alert-error">
            <strong>⚠️ 数据加载失败</strong>
            <p>无法获取逾期患者信息：{str(e)}</p>
            <button class="btn btn-secondary" onclick="location.reload()">🔄 重试</button>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()
    
    if overdue_patients:
        st.markdown(f'''
        <div class="alert alert-error fade-in">
            <strong>{ui_styles.icon_warning()} 紧急提醒：</strong>发现 {len(overdue_patients)} 个患者已过回访日期但未回访！请立即处理。
        </div>
        ''', unsafe_allow_html=True)
    
    # 获取今日待回访患者列表
    try:
        due_patients = get_cached_due_patients()
        log_database_operation('SELECT', 'visit_plans + patients (due)', success=True)
    except Exception as e:
        loading_placeholder.empty()
        logger.error(f"Dashboard加载失败 | 获取今日待回访患者 | 错误: {str(e)}", exc_info=True)
        st.markdown(f'''
        <div class="alert alert-error">
            <strong>⚠️ 数据加载失败</strong>
            <p>无法获取今日待回访患者：{str(e)}</p>
            <button class="btn btn-secondary" onclick="location.reload()">🔄 重试</button>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()
    
    # 获取所有患者数据用于统计
    try:
        all_patients = get_cached_all_patients()
        log_database_operation('SELECT', 'patients (all)', success=True)
    except Exception as e:
        loading_placeholder.empty()
        logger.error(f"Dashboard加载失败 | 获取所有患者数据 | 错误: {str(e)}", exc_info=True)
        st.markdown(f'''
        <div class="alert alert-error">
            <strong>⚠️ 数据加载失败</strong>
            <p>无法获取患者数据：{str(e)}</p>
            <p style="margin-top: 0.5rem; font-size: 0.875rem;">可能原因：数据库文件损坏、权限不足或数据库被锁定</p>
            <button class="btn btn-secondary" onclick="location.reload()">🔄 重试</button>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()
    
    # 清除加载指示器
    loading_placeholder.empty()
    
    if all_patients:
        df_all = pd.DataFrame(all_patients)
        
        total_patients = len(df_all)
        completed_patients = len(df_all[df_all['status'] == 'completed'])
        pending_patients = len(df_all[df_all['status'] == 'pending'])
        completion_rate = (completed_patients / total_patients * 100) if total_patients > 0 else 0
        overdue_count = len(overdue_patients)
        today_due_count = len(due_patients)
        
        # ===== 关键指标卡片区域 =====
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        # 今日待回访
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_phone(),
            today_due_count,
            "今日待回访",
            "需要立即处理" if today_due_count > 0 else "暂无任务",
            "warning" if today_due_count > 0 else "default"
        ), unsafe_allow_html=True)
        
        # 逾期数
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_warning(),
            overdue_count,
            "逾期数",
            "需紧急跟进" if overdue_count > 0 else "无逾期",
            "danger" if overdue_count > 0 else "success"
        ), unsafe_allow_html=True)
        
        # 完成率
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_check(),
            f"{completion_rate:.1f}%",
            "完成率",
            f"已完成 {completed_patients}/{total_patients}",
            "success" if completion_rate >= 80 else "warning" if completion_rate >= 50 else "danger"
        ), unsafe_allow_html=True)
        
        # 总患者数
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_user(),
            total_patients,
            "总患者数",
            f"待回访 {pending_patients} 人",
            "default"
        ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # 结束 metrics-grid
        
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 逾期患者提醒区域 =====
        if overdue_patients:
            st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
            st.markdown(f'''
            <div class="section-header">
                <h3 class="section-title">{ui_styles.icon_warning()} 逾期患者列表</h3>
                <p class="section-description">以下患者已过回访日期，请立即处理</p>
            </div>
            ''', unsafe_allow_html=True)
            
            for patient in overdue_patients:
                days = patient['days_overdue']
                overdue_text = f"逾期 {days} 天" if days > 1 else "逾期 1 天"
                
                status_badge = ui_styles.get_status_badge('overdue')
                
                st.markdown(f'''
                <div style="padding: 1.5rem; border-bottom: 1px solid #E5E7EB;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <strong style="font-size: 1.125rem; color: #111827;">{patient['name']}</strong>
                            <span style="margin-left: 0.5rem; color: #6B7280;">({patient['gender']})</span>
                            {status_badge}
                        </div>
                        <div style="color: #EF4444; font-weight: 600;">{overdue_text}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                        <div><span style="color: #6B7280; font-size: 0.875rem;">诊断：</span><span style="color: #374151;">{patient['diagnosis']}</span></div>
                        <div><span style="color: #6B7280; font-size: 0.875rem;">回访日期：</span><span style="color: #374151;">{patient['visit_date']}</span></div>
                        {f'<div><span style="color: #6B7280; font-size: 0.875rem;">联系人：</span><span style="color: #374151;">{patient["contact_person"]}</span></div>' if patient.get('contact_person') else ''}
                        {f'<div><span style="color: #6B7280; font-size: 0.875rem;">电话：</span><span style="color: #374151;">{patient["contact_phone"]}</span></div>' if patient.get('contact_phone') else ''}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # 操作按钮
                col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
                with col_act1:
                    if st.button(f"✅ 完成", key=f"overdue_complete_{patient.get('plan_id', patient['id'])}"):
                        if 'plan_id' in patient:
                            db_manager.update_visit_plan_status(patient['plan_id'], 'completed')
                        else:
                            db_manager.update_patient_status(patient['id'], 'completed')
                        st.success(f"已将 {patient['name']} 标记为已完成")
                        st.rerun()
                
                with col_act2:
                    if st.button(f"📅 推迟", key=f"overdue_reschedule_{patient.get('plan_id', patient['id'])}"):
                        st.session_state[f"reschedule_{patient.get('plan_id', patient['id'])}"] = True
                
                with col_act3:
                    script_btn_key = f"overdue_script_btn_{patient.get('plan_id', patient['id'])}"
                    script_state_key = f"overdue_script_data_{patient.get('plan_id', patient['id'])}"
                    if st.button(f"✨ 生成话术", key=script_btn_key):
                        # 显示骨架屏加载效果
                        script_loading_placeholder = st.empty()
                        with script_loading_placeholder:
                            st.markdown('''
                            <div style="background: #FEF3C7; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 4px solid #F59E0B;">
                                <div class="skeleton skeleton-text" style="width: 30%; margin-bottom: 0.5rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 90%;"></div>
                                <div class="skeleton skeleton-text" style="width: 85%; margin-top: 0.5rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 80%; margin-top: 0.5rem;"></div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        with st.spinner("AI 正在生成..."):
                            script = ai_agent.generate_visit_script(
                                patient['name'], 
                                patient['diagnosis'], 
                                overdue_text
                            )
                            st.session_state[script_state_key] = script
                        
                        # 清除骨架屏
                        script_loading_placeholder.empty()
                
                # 修改回访日期
                if st.session_state.get(f"reschedule_{patient.get('plan_id', patient['id'])}", False):
                    with st.form(key=f"reschedule_form_{patient.get('plan_id', patient['id'])}"):
                        new_date = st.date_input("选择新的回访日期", value=datetime.now(), key=f"new_date_{patient.get('plan_id', patient['id'])}")
                        col_save, col_cancel = st.columns(2)
                        if col_save.form_submit_button("💾 保存"):
                            if 'plan_id' in patient:
                                import sqlite3
                                conn = sqlite3.connect(db_manager.DB_NAME)
                                cursor = conn.cursor()
                                cursor.execute('UPDATE visit_plans SET visit_date = ? WHERE id = ?', 
                                             (new_date.strftime('%Y-%m-%d'), patient['plan_id']))
                                conn.commit()
                                conn.close()
                                st.success(f"已更新回访日期为 {new_date.strftime('%Y-%m-%d')}")
                            del st.session_state[f"reschedule_{patient.get('plan_id', patient['id'])}"]
                            st.rerun()
                        if col_cancel.form_submit_button("❌ 取消"):
                            del st.session_state[f"reschedule_{patient.get('plan_id', patient['id'])}"]
                            st.rerun()
                
                # 显示AI话术
                script_state_key_check = f"overdue_script_data_{patient.get('plan_id', patient['id'])}"
                if script_state_key_check in st.session_state:
                    st.markdown(f'''
                    <div style="background: #FEF3C7; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 4px solid #F59E0B;">
                        <strong style="color: #92400E;">💬 AI 建议话术：</strong>
                        <p style="margin-top: 0.5rem; color: #78350F;">{st.session_state[script_state_key_check]}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # 结束 data-section
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 今日待回访患者 =====
        if due_patients:
            st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
            st.markdown('''
            <div class="section-header">
                <h3 class="section-title">📞 今日待回访</h3>
                <p class="section-description">以下患者需要在今天进行回访</p>
            </div>
            ''', unsafe_allow_html=True)
            
            for patient in due_patients:
                status_badge = ui_styles.get_status_badge('pending')
                
                st.markdown(f'''
                <div style="padding: 1.5rem; border-bottom: 1px solid #E5E7EB;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <strong style="font-size: 1.125rem; color: #111827;">{patient['name']}</strong>
                            <span style="margin-left: 0.5rem; color: #6B7280;">({patient['gender']})</span>
                            {status_badge}
                        </div>
                        <div style="color: #F59E0B; font-weight: 600;">{patient['urgency']}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                        <div><span style="color: #6B7280; font-size: 0.875rem;">诊断：</span><span style="color: #374151;">{patient['diagnosis']}</span></div>
                        <div><span style="color: #6B7280; font-size: 0.875rem;">回访日期：</span><span style="color: #374151;">{patient['visit_date']}</span></div>
                        {f'<div><span style="color: #6B7280; font-size: 0.875rem;">联系人：</span><span style="color: #374151;">{patient["contact_person"]}</span></div>' if patient.get('contact_person') else ''}
                        {f'<div><span style="color: #6B7280; font-size: 0.875rem;">电话：</span><span style="color: #374151;">{patient["contact_phone"]}</span></div>' if patient.get('contact_phone') else ''}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # 操作按钮
                col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
                with col_act1:
                    if st.button(f"✅ 完成", key=f"due_complete_{patient.get('plan_id', patient['name'])}"):
                        if 'plan_id' in patient:
                            db_manager.update_visit_plan_status(patient['plan_id'], 'completed')
                        else:
                            db_manager.update_patient_status(patient.get('id', 0), 'completed')
                        st.success(f"已将 {patient['name']} 标记为已完成")
                        st.rerun()
                
                with col_act2:
                    if st.button(f"📅 推迟", key=f"due_reschedule_{patient.get('plan_id', patient['name'])}"):
                        st.session_state[f"due_reschedule_{patient.get('plan_id', patient['name'])}"] = True
                
                with col_act3:
                    script_btn_key = f"due_script_btn_{patient.get('plan_id', patient['name'])}"
                    script_state_key = f"due_script_data_{patient.get('plan_id', patient['name'])}"
                    if st.button(f"✨ 生成话术", key=script_btn_key):
                        # 显示骨架屏加载效果
                        script_loading_placeholder = st.empty()
                        with script_loading_placeholder:
                            st.markdown('''
                            <div style="background: #D1FAE5; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 4px solid #10B981;">
                                <div class="skeleton skeleton-text" style="width: 30%; margin-bottom: 0.5rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 90%;"></div>
                                <div class="skeleton skeleton-text" style="width: 85%; margin-top: 0.5rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 80%; margin-top: 0.5rem;"></div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        with st.spinner("AI 正在生成..."):
                            script = ai_agent.generate_visit_script(
                                patient['name'], 
                                patient['diagnosis'], 
                                patient['urgency']
                            )
                            st.session_state[script_state_key] = script
                        
                        # 清除骨架屏
                        script_loading_placeholder.empty()
                
                # 显示AI话术
                script_state_key_check = f"due_script_data_{patient.get('plan_id', patient['name'])}"
                if script_state_key_check in st.session_state:
                    st.markdown(f'''
                    <div style="background: #D1FAE5; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 4px solid #10B981;">
                        <strong style="color: #065F46;">💬 AI 建议话术：</strong>
                        <p style="margin-top: 0.5rem; color: #064E3B;">{st.session_state[script_state_key_check]}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # 结束 data-section
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        elif not overdue_patients:
            st.markdown('''
            <div class="alert alert-success fade-in">
                <strong>✅ 太好了！</strong>暂无今日回访任务，祝您工作愉快！
            </div>
            ''', unsafe_allow_html=True)
        
        # ===== 患者数据表格（带高级筛选）=====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">📋 患者数据管理</h3>
            <p class="section-description">查看所有患者信息，支持高级筛选和批量操作</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 筛选器栏
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
        
        with col_f1:
            search_keyword = st.text_input(
                "",
                placeholder="🔍 搜索姓名或住院号...",
                key="dashboard_search",
                label_visibility="collapsed"
            )
        
        with col_f2:
            status_filter_options = {
                "全部状态": "all",
                "待回访": "pending",
                "已完成": "completed"
            }
            status_label = st.selectbox(
                "",
                list(status_filter_options.keys()),
                key="dashboard_status_filter",
                label_visibility="collapsed"
            )
            status_filter = status_filter_options[status_label]
        
        with col_f3:
            diagnosis_list = ["全部病种"] + sorted(df_all['diagnosis'].unique().tolist())
            diagnosis_filter = st.selectbox(
                "",
                diagnosis_list,
                key="dashboard_diagnosis_filter",
                label_visibility="collapsed"
            )
        
        with col_f4:
            sort_options = {
                "创建时间 ↓": "created_at_desc",
                "创建时间 ↑": "created_at_asc",
                "回访日期 ↑": "visit_date_asc",
                "姓名 A-Z": "name_asc"
            }
            sort_label = st.selectbox(
                "",
                list(sort_options.keys()),
                key="dashboard_sort",
                label_visibility="collapsed"
            )
            sort_by = sort_options[sort_label]
        
        st.markdown('</div>', unsafe_allow_html=True)  # 结束 filter-bar
        
        # 应用筛选条件
        filtered_df = df_all.copy()
        
        if search_keyword:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_keyword, na=False) |
                filtered_df['hospital_number'].astype(str).str.contains(search_keyword, na=False)
            ]
        
        if status_filter != "all":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        if diagnosis_filter != "全部病种":
            filtered_df = filtered_df[filtered_df['diagnosis'] == diagnosis_filter]
        
        # 排序
        if sort_by == "created_at_desc":
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
        elif sort_by == "created_at_asc":
            filtered_df = filtered_df.sort_values('created_at', ascending=True)
        elif sort_by == "visit_date_asc":
            # 需要处理多回访日期的情况
            pass  # 简化处理，暂时不排序
        elif sort_by == "name_asc":
            filtered_df = filtered_df.sort_values('name', ascending=True)
        
        # 显示筛选结果统计
        if search_keyword or status_filter != "all" or diagnosis_filter != "全部病种":
            st.markdown(f'''
            <div style="padding: 0.75rem 1.5rem; background: #EFF6FF; border-bottom: 1px solid #DBEAFE;">
                <span style="color: #1E40AF; font-size: 0.875rem;">📊 显示 {len(filtered_df)} / {len(df_all)} 条记录</span>
            </div>
            ''', unsafe_allow_html=True)
        
        # 显示数据表格
        if len(filtered_df) > 0:
            # 显示表格加载骨架屏
            table_loading_placeholder = st.empty()
            with table_loading_placeholder:
                st.markdown('''
                <div style="padding: 1.5rem;">
                    <div class="skeleton skeleton-title" style="width: 20%; margin-bottom: 1rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 100%; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 100%; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 100%; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 100%; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 100%;"></div>
                </div>
                ''', unsafe_allow_html=True)
            
            # 准备表格数据
            table_data = []
            for _, patient in filtered_df.iterrows():
                # 确定状态
                if patient['id'] in [p['id'] for p in overdue_patients]:
                    status_text = '⚠️ 已逾期'
                elif patient['status'] == 'completed':
                    status_text = '✅ 已完成'
                else:
                    status_text = '⏳ 待回访'
                
                table_data.append({
                    '姓名': patient['name'],
                    '性别': patient['gender'],
                    '住院号': patient.get('hospital_number', '-') or '-',
                    '诊断': patient['diagnosis'],
                    '回访日期': patient.get('visit_date', '-'),
                    '联系人': patient.get('contact_person', '-'),
                    '联系电话': patient.get('contact_phone', '-'),
                    '状态': status_text,
                    'patient_id': patient['id'],
                    'plan_id': patient['visit_plans'][0]['plan_id'] if patient.get('visit_plans') else None
                })
            
            table_df = pd.DataFrame(table_data)
            
            # 清除骨架屏
            table_loading_placeholder.empty()
            
            # 使用 Streamlit 的 dataframe 显示（隐藏ID列）
            display_cols = ['姓名', '性别', '住院号', '诊断', '回访日期', '联系人', '联系电话', '状态']
            
            st.dataframe(
                table_df[display_cols],
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # 批量操作区域
            st.markdown('<div style="padding: 1rem 1.5rem; border-top: 1px solid #E5E7EB; background: #F9FAFB;">', unsafe_allow_html=True)
            
            batch_col1, batch_col2, batch_col3 = st.columns([3, 1, 1])
            
            with batch_col1:
                patient_options_batch = {f"{row['姓名']} ({row['住院号']})": row['patient_id'] for _, row in table_df.iterrows()}
                selected_for_batch = st.multiselect(
                    "选择患者进行批量操作",
                    list(patient_options_batch.keys()),
                    key="batch_select_dashboard"
                )
            
            with batch_col2:
                if selected_for_batch and st.button("✅ 批量完成", use_container_width=True):
                    count = 0
                    for pname in selected_for_batch:
                        pid = patient_options_batch[pname]
                        db_manager.update_patient_status(pid, 'completed')
                        count += 1
                    st.success(f"已标记 {count} 个患者为完成")
                    st.rerun()
            
            with batch_col3:
                if selected_for_batch and st.button("🔄 批量重置", use_container_width=True):
                    count = 0
                    for pname in selected_for_batch:
                        pid = patient_options_batch[pname]
                        db_manager.update_patient_status(pid, 'pending')
                        count += 1
                    st.success(f"已重置 {count} 个患者")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="padding: 3rem; text-align: center; color: #9CA3AF;">
                <p style="font-size: 1.125rem;">📭 暂无符合条件的患者数据</p>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # 结束 data-section
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("🥧 回访完成情况")
            
            # 准备饼图数据
            status_counts = df_all['status'].value_counts()
            status_labels = {
                'completed': '已完成',
                'pending': '待回访'
            }
            
            pie_data = pd.DataFrame({
                '状态': [status_labels.get(s, s) for s in status_counts.index],
                '数量': status_counts.values
            })
            
            st.bar_chart(
                pie_data.set_index('状态'),
                use_container_width=True
            )
            
            # 显示详细数据
            for _, row in pie_data.iterrows():
                percentage = (row['数量'] / total_patients * 100)
                st.caption(f"{row['状态']}: {row['数量']} 人 ({percentage:.1f}%)")
        
        with chart_col2:
            st.subheader("📊 病种分布")
            
            # 准备病种分布数据
            diagnosis_counts = df_all['diagnosis'].value_counts().head(10)  # 前10个病种
            
            diagnosis_df = pd.DataFrame({
                '病种': diagnosis_counts.index,
                '患者数': diagnosis_counts.values
            })
            
            st.bar_chart(
                diagnosis_df.set_index('病种'),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # 第三行：月度统计
        st.subheader("📅 月度回访统计")
        
        # 提取月份信息
        df_all['created_month'] = pd.to_datetime(df_all['created_at']).dt.to_period('M')
        
        monthly_stats = df_all.groupby('created_month').agg({
            'id': 'count',
            'status': lambda x: (x == 'completed').sum()
        }).rename(columns={'id': '总患者数', 'status': '完成数'})
        
        monthly_stats['完成率'] = (monthly_stats['完成数'] / monthly_stats['总患者数'] * 100).round(1)
        
        # 显示月度统计表
        st.dataframe(
            monthly_stats.reset_index().rename(columns={'created_month': '月份'}),
            use_container_width=True,
            hide_index=True,
            column_config={
                "月份": "月份",
                "总患者数": "总患者数",
                "完成数": "完成数",
                "完成率": st.column_config.ProgressColumn(
                    "完成率",
                    help="月度回访完成率",
                    format="%f",
                    min_value=0,
                    max_value=100,
                )
            }
        )
        
        st.markdown("---")
        
        # 第四行：逾期率趋势
        st.subheader("⚠️ 逾期情况分析")
        
        if overdue_patients:
            # 按逾期天数分组
            overdue_df = pd.DataFrame(overdue_patients)
            overdue_df['逾期区间'] = pd.cut(
                overdue_df['days_overdue'],
                bins=[0, 3, 7, 15, 30, 999],
                labels=['1-3天', '4-7天', '8-15天', '16-30天', '30天以上']
            )
            
            overdue_distribution = overdue_df['逾期区间'].value_counts().sort_index()
            
            col_overdue1, col_overdue2 = st.columns([2, 1])
            
            with col_overdue1:
                st.bar_chart(
                    overdue_distribution,
                    use_container_width=True
                )
            
            with col_overdue2:
                st.metric("平均逾期天数", f"{overdue_df['days_overdue'].mean():.1f}天")
                st.metric("最长逾期", f"{overdue_df['days_overdue'].max()}天")
                st.metric("最短逾期", f"{overdue_df['days_overdue'].min()}天")
        else:
            st.success("✅ 当前无逾期患者")

elif st.session_state.page == 'data':
    # --- 数据查看页面 ---
    st.title("📋 患者数据查看")
    st.markdown("---")
    
    # 获取所有患者数据
    try:
        all_patients = get_cached_all_patients()
        log_database_operation('SELECT', 'patients (all) - data page', success=True)
    except Exception as e:
        logger.error(f"数据查看页面加载失败 | 错误: {str(e)}", exc_info=True)
        st.markdown(f'''
        <div class="alert alert-error">
            <strong>⚠️ 数据加载失败</strong>
            <p>无法获取患者数据：{str(e)}</p>
            <button class="btn btn-secondary" onclick="location.reload()">🔄 重试</button>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()
    
    if all_patients:
        # 转换为 DataFrame
        df = pd.DataFrame(all_patients)
        
        st.markdown("### 🔍 搜索和筛选")
        col_search1, col_search2, col_search3 = st.columns(3)
        
        with col_search1:
            # 按姓名或住院号搜索
            search_keyword = st.text_input("🔎 搜索（姓名/住院号）", placeholder="输入关键词...")
        
        with col_search2:
            # 按状态筛选
            status_filter = st.selectbox(
                "筛选状态",
                ["全部", "pending", "completed"],
                index=0,
                key="status_filter"
            )
        
        with col_search3:
            # 按诊断类型筛选
            diagnosis_list = ["全部"] + sorted(df['diagnosis'].unique().tolist())
            diagnosis_filter = st.selectbox(
                "筛选诊断",
                diagnosis_list,
                index=0,
                key="diagnosis_filter"
            )
        
        # 应用筛选条件
        filtered_df = df.copy()
        
        if search_keyword:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_keyword, na=False) |
                filtered_df['hospital_number'].astype(str).str.contains(search_keyword, na=False)
            ]
        
        if status_filter != "全部":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        if diagnosis_filter != "全部":
            filtered_df = filtered_df[filtered_df['diagnosis'] == diagnosis_filter]
        
        # 显示筛选结果统计
        if search_keyword or status_filter != "全部" or diagnosis_filter != "全部":
            st.info(f"📊 显示 {len(filtered_df)} / {len(df)} 条记录")
        
        # 显示数据统计
        col1, col2, col3 = st.columns(3)
        col1.metric("总患者数", len(filtered_df))
        col2.metric("待回访", len(filtered_df[filtered_df['status'] == 'pending']))
        col3.metric("已完成", len(filtered_df[filtered_df['status'] == 'completed']))
        
        st.markdown("---")
        
        # 批量操作区域
        if len(filtered_df) > 0:
            with st.expander("📦 批量操作", expanded=False):
                st.markdown("**选择要操作的患者：**")
                
                # 创建患者选择列表
                patient_options = {f"{row['name']} ({row.get('hospital_number', '无住院号')})": row['id'] for _, row in filtered_df.iterrows()}
                selected_patients = st.multiselect(
                    "选择患者（可多选）",
                    list(patient_options.keys()),
                    key="batch_select"
                )
                
                if selected_patients:
                    col_batch1, col_batch2, col_batch3 = st.columns(3)
                    
                    with col_batch1:
                        if st.button("✅ 批量标记为完成", type="primary", use_container_width=True):
                            try:
                                count = 0
                                for patient_name in selected_patients:
                                    patient_id = patient_options[patient_name]
                                    db_manager.update_patient_status(patient_id, 'completed')
                                    count += 1
                                
                                log_user_action('批量更新状态', f'数量: {count}', '标记为完成')
                                log_database_operation('UPDATE', 'visit_plans (batch)', success=True)
                                
                                # 清除缓存
                                clear_data_cache()
                                
                                st.success(f"已将 {count} 个患者标记为完成")
                                st.rerun()
                            except Exception as e:
                                logger.error(f"批量更新失败 | 错误: {str(e)}", exc_info=True)
                                log_database_operation('UPDATE', 'visit_plans (batch)', success=False, error_msg=str(e))
                                st.error(f"操作失败: {str(e)}")
                    
                    with col_batch2:
                        if st.button("🔄 批量重置为待回访", use_container_width=True):
                            try:
                                count = 0
                                for patient_name in selected_patients:
                                    patient_id = patient_options[patient_name]
                                    db_manager.update_patient_status(patient_id, 'pending')
                                    count += 1
                                
                                log_user_action('批量更新状态', f'数量: {count}', '重置为待回访')
                                log_database_operation('UPDATE', 'visit_plans (batch)', success=True)
                                
                                # 清除缓存
                                clear_data_cache()
                                
                                st.success(f"已将 {count} 个患者重置为待回访")
                                st.rerun()
                            except Exception as e:
                                logger.error(f"批量重置失败 | 错误: {str(e)}", exc_info=True)
                                log_database_operation('UPDATE', 'visit_plans (batch)', success=False, error_msg=str(e))
                                st.error(f"操作失败: {str(e)}")
                    
                    with col_batch3:
                        st.caption(f"已选择 {len(selected_patients)} 个患者")
        
        st.markdown("---")
        
        # ===== 分页控制 =====
        items_per_page = 20  # 每页显示条数
        total_items = len(filtered_df)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)  # 向上取整
        
        if total_items > items_per_page:
            col_page1, col_page2, col_page3, col_page4 = st.columns([1, 2, 1, 2])
            
            with col_page1:
                st.markdown(f"**共 {total_items} 条记录**")
            
            with col_page2:
                # 页码选择器
                page_options = [f"第 {i} 页" for i in range(1, total_pages + 1)]
                selected_page_label = st.selectbox(
                    "选择页码",
                    page_options,
                    index=0,
                    label_visibility="collapsed"
                )
                current_page = int(selected_page_label.replace("第 ", "").replace(" 页", ""))
            
            with col_page3:
                st.markdown(f"**共 {total_pages} 页**")
            
            with col_page4:
                # 快速跳转
                jump_page = st.number_input(
                    "跳转到",
                    min_value=1,
                    max_value=total_pages,
                    value=current_page,
                    step=1,
                    label_visibility="collapsed"
                )
                if jump_page != current_page:
                    current_page = jump_page
                    st.rerun()
            
            # 计算当前页的数据范围
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            page_df = filtered_df.iloc[start_idx:end_idx]
            
            st.caption(f"📄 显示第 {start_idx + 1}-{end_idx} 条，共 {total_items} 条")
        else:
            page_df = filtered_df
            current_page = 1
        
        st.markdown("---")
        
        # 显示数据表格（使用分页后的数据）
        st.dataframe(
            page_df[['name', 'gender', 'hospital_number', 'discharge_date', 'visit_date', 'diagnosis', 'contact_person', 'contact_phone', 'status', 'created_at']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": "姓名",
                "gender": "性别",
                "hospital_number": "住院号",
                "discharge_date": "出院日期",
                "visit_date": "回访日期",
                "diagnosis": "诊断",
                "contact_person": "联系人",
                "contact_phone": "联系电话",
                "status": "状态",
                "created_at": "创建时间"
            }
        )
        
        st.markdown("---")
        
        # 显示详细的回访计划
        st.markdown("### 📅 回访计划详情")
        for _, patient in filtered_df.iterrows():
            visit_plans = patient.get('visit_plans', [])
            if visit_plans:
                with st.expander(f"{patient['name']} ({patient['gender']}) - {len(visit_plans)}个回访计划", expanded=False):
                    # 时间轴视图
                    for idx, plan in enumerate(visit_plans):
                        status_icon = "✅" if plan['status'] == 'completed' else "⏳"
                        status_text = "已完成" if plan['status'] == 'completed' else "待回访"
                        completed_info = f" | 完成时间: {plan['completed_at']}" if plan['completed_at'] else ""
                        
                        # 计算进度（0.0-1.0之间）
                        progress_value = (idx + 1) / len(visit_plans)
                        progress_percent = int(progress_value * 100)
                        
                        st.markdown(f"""
                        **{status_icon} 回访 {idx + 1}/{len(visit_plans)}**
                        - 📅 日期: {plan['visit_date']}
                        - 📋 类型: {plan['visit_type']}
                        - 📊 状态: {status_text}{completed_info}
                        """)
                        
                        # 显示进度条
                        if idx < len(visit_plans) - 1:
                            st.progress(progress_value, text=f"进度: {progress_percent}%")
        
        # 操作区域
        st.markdown("### 🔧 操作区")
        selected_patient = st.selectbox(
            "选择患者",
            filtered_df['name'].tolist() if len(filtered_df) > 0 else [],
            key="select_patient"
        )
        
        if selected_patient:
            patient_data = df[df['name'] == selected_patient].iloc[0]
            hospital_info = f" | 住院号：{patient_data.get('hospital_number', '无')}" if patient_data.get('hospital_number') else ""
            st.info(f"**当前选中：** {selected_patient} | 性别：{patient_data['gender']}{hospital_info} | 诊断：{patient_data['diagnosis']} | 状态：{patient_data['status']}")
            
            # 显示该患者的所有回访计划
            visit_plans = patient_data.get('visit_plans', [])
            if visit_plans:
                st.markdown("**回访计划列表：**")
                for plan in visit_plans:
                    status_icon = "✅" if plan['status'] == 'completed' else "⏳"
                    col_plan, col_action = st.columns([3, 1])
                    with col_plan:
                        st.markdown(f"{status_icon} {plan['visit_date']} - {plan['visit_type']} - {'已完成' if plan['status'] == 'completed' else '待回访'}")
                    with col_action:
                        if plan['status'] == 'pending':
                            if st.button("✅ 完成", key=f"complete_plan_{plan['plan_id']}"):
                                db_manager.update_visit_plan_status(plan['plan_id'], 'completed')
                                st.success(f"已标记 {plan['visit_date']} 的回访为完成")
                                st.rerun()
                        else:
                            if st.button("🔄 重置", key=f"reset_plan_{plan['plan_id']}"):
                                db_manager.update_visit_plan_status(plan['plan_id'], 'pending')
                                st.success(f"已重置 {plan['visit_date']} 的回访为待回访")
                                st.rerun()
            
            col1, col2 = st.columns(2)
            if col1.button("✅ 标记所有为已完成", key="mark_complete"):
                db_manager.update_patient_status(patient_data['id'], 'completed')
                st.success(f"已将 {selected_patient} 的所有回访标记为已完成")
                st.rerun()
            
            if col2.button("🔄 重置所有为待回访", key="reset_pending"):
                db_manager.update_patient_status(patient_data['id'], 'pending')
                st.success(f"已将 {selected_patient} 的所有回访重置为待回访")
                st.rerun()
            
            st.markdown("---")
            
            # 📝 回访记录管理
            st.markdown("### 📝 回访记录管理")
            
            # 选择要添加记录的回访计划
            plan_options = {}
            for plan in visit_plans:
                status_icon = "✅" if plan['status'] == 'completed' else "⏳"
                plan_options[f"{status_icon} {plan['visit_date']} - {plan['visit_type']}"] = plan['plan_id']
            
            selected_plan_label = st.selectbox(
                "选择回访计划",
                list(plan_options.keys()),
                key="select_plan_for_record"
            )
            
            if selected_plan_label:
                selected_plan_id = plan_options[selected_plan_label]
                
                # 显示该计划的已有记录
                existing_records = db_manager.get_visit_records(patient_data['id'], selected_plan_id)
                if existing_records:
                    with st.expander(f"📋 已有回访记录 ({len(existing_records)}条)", expanded=False):
                        for record in existing_records:
                            st.markdown(f"**📅 {record['visit_date']}**")
                            if record['record_content']:
                                st.markdown(f"- **回访内容:** {record['record_content']}")
                            if record['patient_feedback']:
                                st.markdown(f"- **患者反馈:** {record['patient_feedback']}")
                            if record['health_status']:
                                st.markdown(f"- **健康状况:** {record['health_status']}")
                            if record['medication_info']:
                                st.markdown(f"- **用药情况:** {record['medication_info']}")
                            if record['recorder']:
                                st.markdown(f"- **记录人:** {record['recorder']}")
                            st.markdown("---")
                
                # 添加新记录表单
                with st.form(key=f"add_record_form_{selected_plan_id}"):
                    st.markdown("**➕ 添加新回访记录**")
                    
                    record_date = st.date_input(
                        "回访日期",
                        value=datetime.strptime(selected_plan_label.split()[1], '%Y-%m-%d').date() if len(selected_plan_label.split()) > 1 else datetime.now().date(),
                        key=f"record_date_{selected_plan_id}"
                    )
                    
                    record_content = st.text_area(
                        "回访内容",
                        placeholder="例如：电话回访，患者表示恢复良好...",
                        key=f"record_content_{selected_plan_id}"
                    )
                    
                    patient_feedback = st.text_area(
                        "患者反馈",
                        placeholder="例如：患者表示伤口愈合良好，无不适感...",
                        key=f"patient_feedback_{selected_plan_id}"
                    )
                    
                    col_health1, col_health2 = st.columns(2)
                    with col_health1:
                        health_status = st.selectbox(
                            "健康状况",
                            ["良好", "一般", "较差", "需就医"],
                            key=f"health_status_{selected_plan_id}"
                        )
                    with col_health2:
                        medication_info = st.text_input(
                            "用药情况",
                            placeholder="例如：按时服药，无不良反应",
                            key=f"medication_info_{selected_plan_id}"
                        )
                    
                    next_visit = st.date_input(
                        "下次回访日期（可选）",
                        value=None,
                        key=f"next_visit_{selected_plan_id}"
                    )
                    
                    recorder = st.text_input(
                        "记录人",
                        placeholder="您的姓名",
                        key=f"recorder_{selected_plan_id}"
                    )
                    
                    submit_record = st.form_submit_button("💾 保存回访记录", use_container_width=True)
                    
                    if submit_record:
                        if record_content or patient_feedback:
                            db_manager.add_visit_record(
                                plan_id=selected_plan_id,
                                patient_id=patient_data['id'],
                                visit_date=record_date.strftime('%Y-%m-%d'),
                                record_content=record_content,
                                patient_feedback=patient_feedback,
                                health_status=health_status,
                                medication_info=medication_info,
                                next_visit_date=next_visit.strftime('%Y-%m-%d') if next_visit else None,
                                recorder=recorder
                            )
                            st.success("✅ 回访记录已保存")
                            st.rerun()
                        else:
                            st.error("❌ 请至少填写回访内容或患者反馈")
            
            st.markdown("---")
            
            # 📤 档案导出
            st.markdown("### 📤 档案导出")
            
            col_export1, col_export2 = st.columns([1, 3])
            with col_export1:
                if st.button("📥 导出Excel档案", use_container_width=True):
                    # 生成文件名
                    export_filename = f"{selected_patient}_档案_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    export_path = f"D:\\remindercode\\exports\\{export_filename}"
                    
                    # 确保目录存在
                    import os
                    os.makedirs("D:\\remindercode\\exports", exist_ok=True)
                    
                    with st.spinner("正在生成档案..."):
                        success, message = db_manager.export_patient_to_excel(patient_data['id'], export_path)
                    
                    if success:
                        st.success(message)
                        
                        # 提供下载按钮
                        with open(export_path, 'rb') as f:
                            st.download_button(
                                label="💾 点击下载档案",
                                data=f.read(),
                                file_name=export_filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    else:
                        st.error(message)
                        st.info("💡 提示：需要安装 openpyxl 库，请运行: pip install openpyxl")
            
            with col_export2:
                st.caption("导出包含：患者基本信息、回访计划、回访记录")
    else:
        st.info("📭 暂无患者数据，请在左侧添加新患者")

elif st.session_state.page == 'chat':
    # --- 智能体对话页面 ---
    st.title("💬 智能体对话")
    st.markdown("---")
    
    st.caption("💡 提示：您可以询问关于患者回访技巧、疾病护理知识、健康管理建议等问题")
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**👤 您：** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI助手：** {msg['content']}")
                st.markdown("---")
    
    # 输入框
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 添加用户消息到历史
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 调用 AI 生成回复
        with st.spinner("AI 正在思考..."):
            response = ai_agent.chat_with_agent(
                user_input, 
                st.session_state.chat_history[:-1]  # 传入除当前消息外的历史
            )
        
        # 添加 AI 回复到历史
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # 重新加载页面以显示新消息
        st.rerun()
    
    # 清空对话按钮
    if st.session_state.chat_history:
        if st.button("🗑️ 清空对话历史"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    
    # 🤖 AI 功能增强
    st.header("🚀 AI 功能增强")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["✨ 话术优化", "📊 病情预测", "📚 案例学习"])
    
    with tab1:
        st.markdown("### ✨ 智能话术优化")
        st.caption("根据患者反馈，优化回访话术，使其更加个性化")
        
        # 选择患者
        all_patients = db_manager.get_all_patients()
        if all_patients:
            patient_options = {f"{p['name']} ({p['diagnosis']})": p for p in all_patients}
            selected_patient_name = st.selectbox(
                "选择患者",
                list(patient_options.keys()),
                key="optimize_patient"
            )
            
            if selected_patient_name:
                patient = patient_options[selected_patient_name]
                
                col_opt1, col_opt2 = st.columns(2)
                with col_opt1:
                    original_script = st.text_area(
                        "原始话术（可选）",
                        placeholder="粘贴原始话术，留空则自动生成",
                        height=100,
                        key=f"original_script_{patient['id']}"
                    )
                
                with col_opt2:
                    patient_feedback = st.text_area(
                        "患者反馈",
                        placeholder="例如：患者表示伤口有些疼痛，担心恢复情况...",
                        height=100,
                        key=f"patient_feedback_opt_{patient['id']}"
                    )
                
                if st.button("🔄 优化话术", type="primary", use_container_width=True, key=f"optimize_btn_{patient['id']}"):
                    if patient_feedback:
                        # 显示骨架屏加载效果
                        optimize_loading_placeholder = st.empty()
                        with optimize_loading_placeholder:
                            st.markdown('''
                            <div style="padding: 1.5rem; background: #F9FAFB; border-radius: 0.5rem; margin-top: 1rem;">
                                <div class="skeleton skeleton-title" style="width: 30%; margin-bottom: 1rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 90%;"></div>
                                <div class="skeleton skeleton-text" style="width: 85%; margin-top: 0.5rem;"></div>
                                <div class="skeleton skeleton-text" style="width: 80%; margin-top: 0.5rem;"></div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        with st.spinner("AI 正在优化话术..."):
                            optimized = ai_agent.optimize_visit_script(
                                patient['name'],
                                patient['diagnosis'],
                                patient_feedback,
                                original_script
                            )
                        
                        # 清除骨架屏
                        optimize_loading_placeholder.empty()
                        
                        st.markdown("### ✅ 优化后的话术：")
                        st.success(optimized)
                        
                        # 提供复制按钮
                        st.code(optimized, language="markdown")
                    else:
                        st.error("❌ 请填写患者反馈")
        else:
            st.info("📭 暂无患者数据")
    
    with tab2:
        st.markdown("### 📊 病情预测与风险评估")
        st.caption("基于历史数据预测复发风险，推荐个性化回访频率")
        
        all_patients = db_manager.get_all_patients()
        if all_patients:
            patient_options = {f"{p['name']} ({p['diagnosis']})": p for p in all_patients}
            selected_patient_name = st.selectbox(
                "选择患者",
                list(patient_options.keys()),
                key="predict_patient"
            )
            
            if selected_patient_name:
                patient = patient_options[selected_patient_name]
                
                if st.button("🔮 进行风险评估", type="primary", use_container_width=True):
                    # 显示骨架屏加载效果
                    risk_loading_placeholder = st.empty()
                    with risk_loading_placeholder:
                        st.markdown('''
                        <div style="padding: 1.5rem; background: #F9FAFB; border-radius: 0.5rem; margin-top: 1rem;">
                            <div class="skeleton skeleton-title" style="width: 30%; margin-bottom: 1rem;"></div>
                            <div class="skeleton skeleton-text" style="width: 90%;"></div>
                            <div class="skeleton skeleton-text" style="width: 85%; margin-top: 0.5rem;"></div>
                            <div class="skeleton skeleton-text" style="width: 80%; margin-top: 0.5rem;"></div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with st.spinner("AI 正在分析患者数据..."):
                        # 获取患者的回访记录
                        visit_records = db_manager.get_visit_records(patient['id'])
                        
                        # 进行风险评估
                        risk_assessment = ai_agent.predict_recurrence_risk(
                            patient['diagnosis'],
                            {
                                'gender': patient['gender'],
                                'discharge_date': patient['discharge_date'],
                                'hospital_number': patient.get('hospital_number', '')
                            },
                            visit_records
                        )
                    
                    # 清除骨架屏
                    risk_loading_placeholder.empty()
                    
                    # 显示评估结果
                    st.markdown("### 📋 风险评估报告")
                    
                    # 风险等级和评分
                    col_risk1, col_risk2, col_risk3 = st.columns(3)
                    
                    risk_level = risk_assessment.get('risk_level', '中风险')
                    risk_score = risk_assessment.get('risk_score', 50)
                    
                    # 根据风险等级设置颜色
                    if risk_level == "高风险":
                        risk_color = "red"
                        risk_icon = "🔴"
                    elif risk_level == "低风险":
                        risk_color = "green"
                        risk_icon = "🟢"
                    else:
                        risk_color = "orange"
                        risk_icon = "🟡"
                    
                    col_risk1.metric(
                        f"{risk_icon} 风险等级",
                        risk_level
                    )
                    col_risk2.metric(
                        "📊 风险评分",
                        f"{risk_score}/100"
                    )
                    
                    # 推荐回访频率
                    recommended_freq = risk_assessment.get('recommended_frequency', '常规随访')
                    col_risk3.metric(
                        "📅 建议回访频率",
                        recommended_freq
                    )
                    
                    st.markdown("---")
                    
                    # 完整评估报告
                    st.markdown("#### 📝 详细评估")
                    st.info(risk_assessment.get('full_assessment', '无评估结果'))
                    
                    st.markdown("---")
                    
                    # 生成个性化回访频率建议
                    if st.button("💡 生成个性化回访计划"):
                        with st.spinner("AI 正在制定回访计划..."):
                            frequency_plan = ai_agent.recommend_visit_frequency(
                                patient['diagnosis'],
                                risk_assessment
                            )
                        
                        st.markdown("### 📅 个性化回访计划")
                        st.success(frequency_plan)
        else:
            st.info("📭 暂无患者数据")
    
    with tab3:
        st.markdown("### 📚 优秀案例学习")
        st.caption("学习优秀回访案例，提取最佳实践")
        
        case_description = st.text_area(
            "案例描述",
            placeholder="描述一个成功的回访案例，例如：\n张医生在回访胃癌术后患者时，首先关心患者的饮食情况，然后耐心倾听患者的担忧，最后给出了具体的饮食建议。患者非常满意，表示感受到了关怀。",
            height=150,
            key="case_description_global"
        )
        
        key_points = st.text_area(
            "关键点总结",
            placeholder="总结案例的关键点，例如：\n1. 先关心生活细节\n2. 耐心倾听\n3. 给出具体建议\n4. 体现人文关怀",
            height=100,
            key="key_points_global"
        )
        
        if st.button("🎓 学习案例", type="primary", use_container_width=True, key="learn_case_btn"):
            if case_description and key_points:
                # 显示骨架屏加载效果
                case_loading_placeholder = st.empty()
                with case_loading_placeholder:
                    st.markdown('''
                    <div style="padding: 1.5rem; background: #F9FAFB; border-radius: 0.5rem; margin-top: 1rem;">
                        <div class="skeleton skeleton-title" style="width: 30%; margin-bottom: 1rem;"></div>
                        <div class="skeleton skeleton-text" style="width: 90%;"></div>
                        <div class="skeleton skeleton-text" style="width: 85%; margin-top: 0.5rem;"></div>
                        <div class="skeleton skeleton-text" style="width: 80%; margin-top: 0.5rem;"></div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with st.spinner("AI 正在分析案例..."):
                    learning_result = ai_agent.learn_from_excellent_cases(
                        case_description,
                        key_points
                    )
                
                # 清除骨架屏
                case_loading_placeholder.empty()
                
                st.markdown("### 📖 学习总结")
                st.success(learning_result)
                
                st.markdown("---")
                st.caption("💡 提示：可以将学到的经验应用到实际回访工作中")
            else:
                st.error("❌ 请填写案例描述和关键点")

elif st.session_state.page == 'admin':
    # --- 数据管理页面 ---
    st.title("🔧 数据管理")
    st.markdown("---")
    
    st.warning("⚠️ **警告：** 以下操作会修改数据库，请谨慎操作！建议先备份数据库。")
    
    # 查找重复数据
    st.header("🔍 查找重复患者记录")
    st.caption("根据住院号查找重复的患者记录")
    
    if st.button("🔎 扫描重复记录", type="primary"):
        # 显示骨架屏加载效果
        scan_loading_placeholder = st.empty()
        with scan_loading_placeholder:
            st.markdown('''
            <div style="padding: 2rem; background: #F9FAFB; border-radius: 0.5rem;">
                <div class="skeleton skeleton-title" style="width: 40%; margin-bottom: 1rem;"></div>
                <div class="skeleton skeleton-text" style="width: 80%;"></div>
                <div class="skeleton skeleton-text" style="width: 70%; margin-top: 0.5rem;"></div>
            </div>
            ''', unsafe_allow_html=True)
        
        with st.spinner("正在扫描..."):
            duplicates = db_manager.find_duplicate_patients_by_hospital_number()
        
        # 清除骨架屏
        scan_loading_placeholder.empty()
        
        if duplicates:
            st.error(f"⚠️ 发现 {len(duplicates)} 个住院号存在重复记录")
            
            for hosp_num, patients in duplicates.items():
                with st.expander(f"📋 住院号: {hosp_num} ({len(patients)}条记录)", expanded=True):
                    st.markdown("**重复的患者记录：**")
                    
                    # 显示表格
                    df_dup = pd.DataFrame(patients)
                    st.dataframe(
                        df_dup[['id', 'name', 'gender', 'discharge_date', 'diagnosis', 'contact_person', 'status', 'created_at']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id": "ID",
                            "name": "姓名",
                            "gender": "性别",
                            "discharge_date": "出院日期",
                            "diagnosis": "诊断",
                            "contact_person": "联系人",
                            "status": "状态",
                            "created_at": "创建时间"
                        }
                    )
                    
                    # 选择要保留的记录
                    st.markdown("**选择要保留的记录：**")
                    st.info("💡 建议选择创建时间最新或信息最完整的记录")
                    
                    keep_options = {f"{p['name']} (ID: {p['id']}, 创建: {p['created_at']})": p['id'] for p in patients}
                    # 清理住院号中的特殊字符，确保key安全
                    safe_hosp_num = hosp_num.replace(' ', '_').replace('-', '_').replace('.', '_')
                    keep_patient_name = st.selectbox(
                        f"选择要保留的患者记录（住院号: {hosp_num}）",
                        list(keep_options.keys()),
                        key=f"keep_hosp_{safe_hosp_num}"
                    )
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("✅ 合并", key=f"merge_hosp_{safe_hosp_num}", type="primary"):
                            keep_id = keep_options[keep_patient_name]
                            
                            with st.spinner("正在合并..."):
                                merged_count, deleted_count, message = db_manager.merge_duplicate_patients(hosp_num, keep_id)
                            
                            if merged_count > 0 or deleted_count > 0:
                                st.success(message)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col2:
                        st.caption("合并后将：1) 将所有回访计划迁移到保留的记录 2) 删除其他重复记录")
        else:
            st.success("✅ 未发现重复的患者记录")
    
    st.markdown("---")
    
    # 数据库统计
    st.header("📊 数据库统计")
    
    all_patients = db_manager.get_all_patients()
    
    if all_patients:
        col1, col2, col3, col4 = st.columns(4)
        
        total_patients = len(all_patients)
        pending_count = sum(1 for p in all_patients if p['status'] == 'pending')
        completed_count = sum(1 for p in all_patients if p['status'] == 'completed')
        total_plans = sum(len(p.get('visit_plans', [])) for p in all_patients)
        
        col1.metric("总患者数", total_patients)
        col2.metric("待回访", pending_count)
        col3.metric("已完成", completed_count)
        col4.metric("回访计划总数", total_plans)
    
    st.markdown("---")
    
    # 数据备份提示
    st.header("💾 数据备份")
    st.info("📌 建议定期备份数据库文件 `patients.db`")
    st.caption("数据库文件位置: D:\\remindercode\\patients.db")

elif st.session_state.page == 'settings':
    # --- 提醒规则设置页面 ---
    st.title("⚙️ 提醒规则自定义")
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 功能说明
    
    您可以自定义系统的提醒规则，让回访提醒更加灵活和个性化：
    
    - **提前N天提醒**：在回访日期前 N 天开始提醒您
    - **每天固定时间提醒**：设置每天的提醒时间点
    - **重复提醒间隔**：如果未处理，每隔多久再次提醒
    """)
    
    st.markdown("---")
    
    # 获取当前配置
    settings = db_manager.get_reminder_settings()
    
    # 第一行：基本提醒设置
    st.header("📅 基本提醒设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔔 提前提醒")
        
        # 是否启用提前提醒
        enable_advance = settings.get('enable_advance_reminder', {}).get('value', 'false') == 'true'
        enable_advance = st.checkbox(
            "启用提前提醒",
            value=enable_advance,
            help="开启后，系统会在回访日期前 N 天开始提醒您",
            key="enable_advance_global"
        )
        
        # 提前天数
        advance_days = int(settings.get('advance_days', {}).get('value', '0'))
        advance_days = st.slider(
            "提前天数",
            min_value=0,
            max_value=30,
            value=advance_days,
            step=1,
            help="设置为 0 表示仅在当天提醒",
            disabled=not enable_advance,
            key="advance_days_slider_global"
        )
        
        if enable_advance and advance_days > 0:
            st.info(f"💡 系统将在回访日期前 {advance_days} 天开始提醒您")
        elif enable_advance:
            st.info("💡 仅在回访当天提醒")
        else:
            st.caption("关闭后将不会提前提醒")
    
    with col2:
        st.markdown("#### ⏰ 每日提醒时间")
        
        # 提醒时间
        reminder_time = settings.get('reminder_time', {}).get('value', '09:00')
        
        # 解析时间
        try:
            hour, minute = map(int, reminder_time.split(':'))
        except:
            hour, minute = 9, 0
        
        reminder_time_input = st.time_input(
            "选择提醒时间",
            value=datetime.now().replace(hour=hour, minute=minute),
            help="系统会在这个时间点发送提醒",
            key="reminder_time_input_global"
        )
        
        formatted_time = reminder_time_input.strftime('%H:%M')
        st.success(f"✅ 每天 {formatted_time} 提醒您")
    
    st.markdown("---")
    
    # 第二行：重复提醒设置
    st.header("🔄 重复提醒设置")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 🔁 重复提醒")
        
        # 是否启用重复提醒
        enable_repeat = settings.get('enable_repeat_reminder', {}).get('value', 'true') == 'true'
        enable_repeat = st.checkbox(
            "启用重复提醒",
            value=enable_repeat,
            help="开启后，如果回访任务未处理，系统会按设定的间隔重复提醒",
            key="enable_repeat_global"
        )
        
        # 重复间隔
        repeat_interval = int(settings.get('repeat_interval', {}).get('value', '24'))
        repeat_options = {
            "每 6 小时": 6,
            "每 12 小时": 12,
            "每 24 小时（每天）": 24,
            "每 48 小时（每两天）": 48,
            "每 72 小时（每三天）": 72,
        }
        
        selected_label = None
        for label, value in repeat_options.items():
            if value == repeat_interval:
                selected_label = label
                break
        
        if not selected_label:
            selected_label = "每 24 小时（每天）"
        
        repeat_interval_selected = st.selectbox(
            "重复提醒间隔",
            list(repeat_options.keys()),
            index=list(repeat_options.values()).index(repeat_interval) if repeat_interval in repeat_options.values() else 2,
            help="未处理的回访任务会按此间隔重复提醒",
            disabled=not enable_repeat,
            key="repeat_interval_select_global"
        )
        
        repeat_hours = repeat_options[repeat_interval_selected]
        
        if enable_repeat:
            if repeat_hours < 24:
                st.warning(f"⚠️ 系统将每 {repeat_hours} 小时重复提醒一次")
            else:
                days = repeat_hours // 24
                st.info(f"💡 系统将每 {days} 天重复提醒一次")
        else:
            st.caption("关闭后只会提醒一次")
    
    with col4:
        st.markdown("#### 📊 当前配置预览")
        
        # 显示配置摘要
        st.markdown("**当前生效的规则：**")
        
        config_summary = []
        
        if enable_advance and advance_days > 0:
            config_summary.append(f"✅ 提前 {advance_days} 天提醒")
        elif enable_advance:
            config_summary.append("✅ 当天提醒")
        else:
            config_summary.append("❌ 不提前提醒")
        
        config_summary.append(f"⏰ 每日 {formatted_time} 提醒")
        
        if enable_repeat:
            if repeat_hours < 24:
                config_summary.append(f"🔄 每 {repeat_hours} 小时重复")
            else:
                days = repeat_hours // 24
                config_summary.append(f"🔄 每 {days} 天重复")
        else:
            config_summary.append("🔄 不重复提醒")
        
        for item in config_summary:
            st.markdown(f"- {item}")
        
        st.markdown("---")
        
        # 示例场景
        st.markdown("**示例场景：**")
        
        from datetime import timedelta
        sample_visit_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        scenario_text = f"""
        假设患者回访日期为 **{sample_visit_date}**：
        """
        
        if enable_advance and advance_days > 0:
            advance_date = (datetime.now() + timedelta(days=7-advance_days)).strftime('%Y-%m-%d')
            scenario_text += f"\n- 📅 **{advance_date}** 开始第一次提醒"
        
        scenario_text += f"\n- ⏰ 每天 **{formatted_time}** 提醒您"
        
        if enable_repeat:
            scenario_text += f"\n- 🔄 如未处理，每 {repeat_hours} 小时再次提醒"
        
        st.info(scenario_text)
    
    st.markdown("---")
    
    # 保存按钮
    st.header("💾 保存配置")
    
    col_save1, col_save2, col_save3 = st.columns([1, 1, 2])
    
    with col_save1:
        if st.button("✅ 保存设置", type="primary", use_container_width=True):
            # 准备配置数据
            new_settings = {
                'enable_advance_reminder': 'true' if enable_advance else 'false',
                'advance_days': str(advance_days),
                'reminder_time': formatted_time,
                'enable_repeat_reminder': 'true' if enable_repeat else 'false',
                'repeat_interval': str(repeat_hours),
            }
            
            # 批量更新
            success_count, error_count = db_manager.update_reminder_settings_batch(new_settings)
            
            if success_count > 0:
                st.success(f"✅ 成功保存 {success_count} 项配置")
                st.balloons()
            
            if error_count > 0:
                st.error(f"❌ {error_count} 项配置保存失败")
    
    with col_save2:
        if st.button("🔄 重置默认", use_container_width=True):
            # 重置为默认值
            default_settings = {
                'enable_advance_reminder': 'false',
                'advance_days': '0',
                'reminder_time': '09:00',
                'enable_repeat_reminder': 'true',
                'repeat_interval': '24',
            }
            
            success_count, error_count = db_manager.update_reminder_settings_batch(default_settings)
            
            if success_count > 0:
                st.success("已重置为默认配置")
                st.rerun()
    
    with col_save3:
        st.caption("💡 提示：修改配置后立即生效，无需重启系统")
    
    st.markdown("---")
    
    # 高级说明
    with st.expander("📖 高级说明与最佳实践", expanded=False):
        st.markdown("""
        ### 💡 最佳实践建议
        
        #### 1. 提前提醒设置
        - **常规情况**：提前 1-2 天提醒，给医护人员预留准备时间
        - **重要患者**：提前 3-5 天提醒，确保充分准备
        - **紧急情况**：设置为 0，仅当天提醒
        
        #### 2. 提醒时间选择
        - **上午时段**（08:00-10:00）：适合开始工作时查看当日任务
        - **下午时段**（14:00-15:00）：适合午休后处理回访
        - **避免时间**：午休时间（12:00-13:30）、下班后
        
        #### 3. 重复提醒策略
        - **高频模式**（每 6-12 小时）：适合忙碌时期，防止遗漏
        - **标准模式**（每 24 小时）：平衡提醒频率，推荐使用
        - **低频模式**（每 48-72 小时）：适合工作量较小的情况
        
        ### ⚠️ 注意事项
        
        1. **提醒叠加**：如果同时启用提前提醒和重复提醒，可能会收到多次提醒
        2. **及时处理**：看到提醒后应及时处理，避免重复提醒造成干扰
        3. **灵活调整**：根据实际工作节奏调整配置，找到最适合的设置
        
        ### 🔧 技术说明
        
        - 配置存储在本地数据库中，修改后立即生效
        - 系统会在后台定时检查回访任务并发送提醒
        - 提醒会通过智能提醒看板显示，请定期查看
        """)

elif st.session_state.page == 'analytics':
    # --- 数据分析中心 ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">📈 数据分析中心</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">深度洞察回访数据，优化医疗服务质量</p>', unsafe_allow_html=True)
    
    # 获取所有患者数据
    all_patients = db_manager.get_all_patients()
    
    if not all_patients:
        st.info("📭 暂无数据，请先添加患者")
    else:
        df = pd.DataFrame(all_patients)
        
        # ===== 顶部概览卡片 =====
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        total_patients = len(df)
        completed_count = len(df[df['status'] == 'completed'])
        pending_count = len(df[df['status'] == 'pending'])
        completion_rate = (completed_count / total_patients * 100) if total_patients > 0 else 0
        
        # 计算逾期数
        overdue_patients = db_manager.get_overdue_patients()
        overdue_count = len(overdue_patients)
        overdue_rate = (overdue_count / total_patients * 100) if total_patients > 0 else 0
        
        # 总回访计划数
        total_plans = sum(len(p.get('visit_plans', [])) for p in all_patients)
        completed_plans = sum(
            sum(1 for vp in p.get('visit_plans', []) if vp.get('status') == 'completed')
            for p in all_patients
        )
        plan_completion_rate = (completed_plans / total_plans * 100) if total_plans > 0 else 0
        
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_user(),
            total_patients,
            "总患者数",
            f"已完成 {completed_count} 人",
            "default"
        ), unsafe_allow_html=True)
        
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_check(),
            f"{completion_rate:.1f}%",
            "完成率",
            f"{completed_count}/{total_patients}",
            "success" if completion_rate >= 80 else "warning"
        ), unsafe_allow_html=True)
        
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_warning(),
            f"{overdue_rate:.1f}%",
            "逾期率",
            f"{overdue_count} 人逾期",
            "danger" if overdue_rate > 10 else "success"
        ), unsafe_allow_html=True)
        
        st.markdown(ui_styles.get_metric_card_html(
            ui_styles.icon_calendar(),
            total_plans,
            "回访计划总数",
            f"完成 {plan_completion_rate:.1f}%",
            "default"
        ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 回访趋势分析 =====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">📊 回访趋势分析</h3>
            <p class="section-description">查看每日/每周回访完成情况</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 准备趋势数据
        trend_data = []
        for patient in all_patients:
            for plan in patient.get('visit_plans', []):
                trend_data.append({
                    'date': plan['visit_date'],
                    'status': plan['status'],
                    'diagnosis': patient['diagnosis']
                })
        
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            df_trend['date'] = pd.to_datetime(df_trend['date'])
            
            # 按日期分组统计
            daily_stats = df_trend.groupby('date').agg({
                'status': ['count', lambda x: (x == 'completed').sum()]
            }).reset_index()
            daily_stats.columns = ['date', 'total', 'completed']
            daily_stats['pending'] = daily_stats['total'] - daily_stats['completed']
            
            # 显示图表
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### 每日回访统计")
                st.line_chart(
                    daily_stats.set_index('date')[['total', 'completed']],
                    use_container_width=True
                )
            
            with col_chart2:
                st.markdown("#### 完成 vs 待完成")
                st.bar_chart(
                    daily_stats.set_index('date')[['completed', 'pending']],
                    use_container_width=True
                )
        else:
            st.info("📭 暂无回访数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 病种分布分析 =====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">🏥 病种分布分析</h3>
            <p class="section-description">了解不同病种的回访情况</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 病种统计
        diagnosis_stats = df['diagnosis'].value_counts().reset_index()
        diagnosis_stats.columns = ['病种', '患者数']
        
        col_diag1, col_diag2 = st.columns([2, 1])
        
        with col_diag1:
            st.markdown("#### 病种分布柱状图")
            st.bar_chart(
                diagnosis_stats.set_index('病种'),
                use_container_width=True
            )
        
        with col_diag2:
            st.markdown("#### 病种统计表")
            st.dataframe(
                diagnosis_stats,
                use_container_width=True,
                hide_index=True
            )
        
        # 病种完成率
        st.markdown("#### 各病种完成率")
        diagnosis_completion = []
        for diagnosis in df['diagnosis'].unique():
            diag_patients = df[df['diagnosis'] == diagnosis]
            total = len(diag_patients)
            completed = len(diag_patients[diag_patients['status'] == 'completed'])
            rate = (completed / total * 100) if total > 0 else 0
            diagnosis_completion.append({
                '病种': diagnosis,
                '总人数': total,
                '已完成': completed,
                '完成率': f"{rate:.1f}%"
            })
        
        df_diag_completion = pd.DataFrame(diagnosis_completion)
        st.dataframe(
            df_diag_completion,
            use_container_width=True,
            hide_index=True,
            column_config={
                "病种": "病种名称",
                "总人数": "患者总数",
                "已完成": "已完成回访",
                "完成率": st.column_config.ProgressColumn(
                    "完成率",
                    min_value=0,
                    max_value=100,
                    format="%f%%"
                )
            }
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 月度对比分析 =====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">📅 月度对比分析</h3>
            <p class="section-description">查看每月回访趋势变化</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 按月统计
        df['discharge_month'] = pd.to_datetime(df['discharge_date']).dt.to_period('M')
        monthly_stats = df.groupby('discharge_month').agg({
            'id': 'count',
            'status': lambda x: (x == 'completed').sum()
        }).reset_index()
        monthly_stats.columns = ['月份', '出院人数', '已完成回访']
        monthly_stats['月份'] = monthly_stats['月份'].astype(str)
        
        col_month1, col_month2 = st.columns(2)
        
        with col_month1:
            st.markdown("#### 月度出院人数")
            st.bar_chart(
                monthly_stats.set_index('月份')['出院人数'],
                use_container_width=True
            )
        
        with col_month2:
            st.markdown("#### 月度回访完成")
            st.bar_chart(
                monthly_stats.set_index('月份')['已完成回访'],
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 逾期率趋势 =====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">⚠️ 逾期率趋势</h3>
            <p class="section-description">监控逾期情况，及时改进</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 计算每日逾期率
        if trend_data:
            df_trend_copy = df_trend.copy()
            today = datetime.now().strftime('%Y-%m-%d')
            df_trend_copy['is_overdue'] = df_trend_copy['date'].apply(
                lambda x: 1 if x.strftime('%Y-%m-%d') < today and 
                any(p['status'] == 'pending' for p in all_patients 
                    for vp in p.get('visit_plans', []) 
                    if vp['visit_date'] == x.strftime('%Y-%m-%d')) else 0
            )
            
            overdue_daily = df_trend_copy.groupby('date')['is_overdue'].sum().reset_index()
            overdue_daily.columns = ['date', '逾期数']
            
            st.markdown("#### 每日逾期数量")
            st.area_chart(
                overdue_daily.set_index('date'),
                use_container_width=True
            )
            
            # 逾期统计摘要
            col_overdue1, col_overdue2, col_overdue3 = st.columns(3)
            
            total_overdue = overdue_daily['逾期数'].sum()
            avg_overdue = overdue_daily['逾期数'].mean()
            max_overdue = overdue_daily['逾期数'].max()
            
            col_overdue1.metric("总逾期次数", int(total_overdue))
            col_overdue2.metric("日均逾期", f"{avg_overdue:.1f}")
            col_overdue3.metric("最高单日逾期", int(max_overdue))
        else:
            st.info("📭 暂无数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        # ===== 导出报告 =====
        st.markdown('<div class="data-section fade-in">', unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <h3 class="section-title">📤 数据导出</h3>
            <p class="section-description">导出分析报告供进一步研究</p>
        </div>
        ''', unsafe_allow_html=True)
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("📥 导出Excel报告", use_container_width=True):
                import os
                os.makedirs("D:\\remindercode\\exports", exist_ok=True)
                
                export_filename = f"回访分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                export_path = f"D:\\remindercode\\exports\\{export_filename}"
                
                try:
                    with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                        # 患者总表
                        df[['name', 'gender', 'hospital_number', 'diagnosis', 'discharge_date', 'status']].to_excel(
                            writer, sheet_name='患者总表', index=False
                        )
                        
                        # 病种统计
                        diagnosis_stats.to_excel(writer, sheet_name='病种统计', index=False)
                        
                        # 月度统计
                        monthly_stats.to_excel(writer, sheet_name='月度统计', index=False)
                        
                        # 回访趋势
                        if trend_data:
                            daily_stats.to_excel(writer, sheet_name='回访趋势', index=False)
                    
                    st.success(f"✅ 报告已导出：{export_filename}")
                    
                    # 提供下载按钮
                    with open(export_path, 'rb') as f:
                        st.download_button(
                            label="💾 下载报告",
                            data=f.read(),
                            file_name=export_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ 导出失败：{str(e)}")
                    st.info("💡 提示：需要安装 openpyxl 库，请运行: pip install openpyxl")
        
        with col_export2:
            if st.button("📊 导出CSV数据", use_container_width=True):
                import os
                os.makedirs("D:\\remindercode\\exports", exist_ok=True)
                
                csv_filename = f"回访数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_path = f"D:\\remindercode\\exports\\{csv_filename}"
                
                df[['name', 'gender', 'hospital_number', 'diagnosis', 'discharge_date', 'status']].to_csv(
                    csv_path, index=False, encoding='utf-8-sig'
                )
                
                st.success(f"✅ CSV已导出：{csv_filename}")
                
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        label="💾 下载CSV",
                        data=f.read(),
                        file_name=csv_filename,
                        mime="text/csv",
                        use_container_width=True
                    )
        
        with col_export3:
            st.caption("导出包含：患者数据、病种统计、月度分析、趋势数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # 结束 main-container

# 底部说明
st.markdown("---")
st.caption("Powered by LangChain + Qwen (ModelScope)")
