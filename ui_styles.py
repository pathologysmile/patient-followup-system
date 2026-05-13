"""
医疗SaaS风格样式配置 - Linear Design System
采用干净、专业的设计风格，体现医疗行业的信任感
"""

# 主色调 - 医疗蓝（体现专业与信任）
PRIMARY_COLOR = "#2563EB"        # 主蓝色 - 用于主要操作
PRIMARY_LIGHT = "#DBEAFE"        # 浅蓝色背景
PRIMARY_DARK = "#1E40AF"         # 深蓝色 - hover状态

# 辅助色
SUCCESS_COLOR = "#10B981"        # 成功绿
WARNING_COLOR = "#F59E0B"        # 警告橙
ERROR_COLOR = "#EF4444"          # 错误红
INFO_COLOR = "#3B82F6"           # 信息蓝

# 中性色 - 灰色系
GRAY_50 = "#F9FAFB"              # 最浅灰 - 页面背景
GRAY_100 = "#F3F4F6"             # 浅灰 - 卡片背景
GRAY_200 = "#E5E7EB"             # 边框灰
GRAY_300 = "#D1D5DB"             # 分割线
GRAY_400 = "#9CA3AF"             # 禁用文本
GRAY_500 = "#6B7280"             # 次要文本
GRAY_600 = "#4B5563"             # 常规文本
GRAY_700 = "#374151"             # 主要文本
GRAY_800 = "#1F2937"             # 标题
GRAY_900 = "#111827"             # 最深灰

# 语义化颜色
STATUS_PENDING_BG = "#FEF3C7"    # 待回访背景
STATUS_PENDING_TEXT = "#92400E"  # 待回访文字
STATUS_COMPLETED_BG = "#D1FAE5"  # 已完成背景
STATUS_COMPLETED_TEXT = "#065F46"# 已完成文字
STATUS_OVERDUE_BG = "#FEE2E2"    # 逾期背景
STATUS_OVERDUE_TEXT = "#991B1B"  # 逾期文字

# 字体配置
FONT_FAMILY = """
-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
"Helvetica Neue", Arial, "Noto Sans SC", sans-serif
"""

# 字号系统
FONT_SIZE_XS = "0.75rem"         # 12px
FONT_SIZE_SM = "0.875rem"        # 14px
FONT_SIZE_BASE = "1rem"          # 16px
FONT_SIZE_LG = "1.125rem"        # 18px
FONT_SIZE_XL = "1.25rem"         # 20px
FONT_SIZE_2XL = "1.5rem"         # 24px
FONT_SIZE_3XL = "1.875rem"       # 30px

# 间距系统
SPACING_XS = "0.25rem"           # 4px
SPACING_SM = "0.5rem"            # 8px
SPACING_MD = "1rem"              # 16px
SPACING_LG = "1.5rem"            # 24px
SPACING_XL = "2rem"              # 32px
SPACING_2XL = "3rem"             # 48px

# 圆角
RADIUS_SM = "0.375rem"           # 6px
RADIUS_MD = "0.5rem"             # 8px
RADIUS_LG = "0.75rem"            # 12px
RADIUS_XL = "1rem"               # 16px

# 阴影
SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_HOVER = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

# CSS 样式字符串
BASE_CSS = f"""
<!-- Font Awesome 图标库 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
/* ===== 全局样式重置 ===== */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {FONT_FAMILY};
    background-color: {GRAY_50};
    color: {GRAY_800};
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ===== 主容器 ===== */
.main-container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: {SPACING_2XL};
}}

/* ===== 页面标题 ===== */
.page-title {{
    font-size: {FONT_SIZE_3XL};
    font-weight: 700;
    color: {GRAY_900};
    margin-bottom: {SPACING_LG};
    letter-spacing: -0.025em;
}}

.page-subtitle {{
    font-size: {FONT_SIZE_BASE};
    color: {GRAY_500};
    margin-bottom: {SPACING_XL};
}}

/* ===== 关键指标卡片 ===== */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: {SPACING_LG};
    margin-bottom: {SPACING_2XL};
}}

.metric-card {{
    background: white;
    border-radius: {RADIUS_LG};
    padding: {SPACING_XL};
    box-shadow: {SHADOW_SM};
    border: 1px solid {GRAY_200};
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    animation: slideUp 0.5s ease-out;
}}

/* 卡片进入动画 */
@keyframes slideUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.metric-card:hover {{
    box-shadow: {SHADOW_LG};
    transform: translateY(-2px);
    border-color: {PRIMARY_COLOR};
}}

.metric-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, {PRIMARY_COLOR}, {PRIMARY_LIGHT});
}}

.metric-card.warning::before {{
    background: linear-gradient(90deg, {WARNING_COLOR}, #FCD34D);
}}

.metric-card.danger::before {{
    background: linear-gradient(90deg, {ERROR_COLOR}, #FCA5A5);
}}

.metric-card.success::before {{
    background: linear-gradient(90deg, {SUCCESS_COLOR}, #6EE7B7);
}}

.metric-icon {{
    width: 48px;
    height: 48px;
    border-radius: {RADIUS_MD};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: {SPACING_MD};
    background: {PRIMARY_LIGHT};
}}

.metric-card.warning .metric-icon {{
    background: #FEF3C7;
}}

.metric-card.danger .metric-icon {{
    background: #FEE2E2;
}}

.metric-card.success .metric-icon {{
    background: #D1FAE5;
}}

.metric-value {{
    font-size: {FONT_SIZE_3XL};
    font-weight: 700;
    color: {GRAY_900};
    margin-bottom: {SPACING_XS};
    line-height: 1;
}}

.metric-label {{
    font-size: {FONT_SIZE_SM};
    color: {GRAY_500};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.metric-trend {{
    font-size: {FONT_SIZE_XS};
    color: {GRAY_400};
    margin-top: {SPACING_SM};
}}

/* ===== 数据表格区域 ===== */
.data-section {{
    background: white;
    border-radius: {RADIUS_LG};
    box-shadow: {SHADOW_SM};
    border: 1px solid {GRAY_200};
    overflow: hidden;
    margin-bottom: {SPACING_XL};
}}

.section-header {{
    padding: {SPACING_LG} {SPACING_XL};
    border-bottom: 1px solid {GRAY_200};
    background: {GRAY_50};
}}

.section-title {{
    font-size: {FONT_SIZE_XL};
    font-weight: 600;
    color: {GRAY_900};
    margin-bottom: {SPACING_SM};
}}

.section-description {{
    font-size: {FONT_SIZE_SM};
    color: {GRAY_500};
}}

/* ===== 筛选器 ===== */
.filter-bar {{
    padding: {SPACING_LG} {SPACING_XL};
    border-bottom: 1px solid {GRAY_200};
    display: flex;
    gap: {SPACING_MD};
    flex-wrap: wrap;
    align-items: center;
    background: white;
}}

.filter-group {{
    flex: 1;
    min-width: 200px;
}}

.filter-label {{
    font-size: {FONT_SIZE_XS};
    font-weight: 600;
    color: {GRAY_600};
    margin-bottom: {SPACING_XS};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Streamlit 输入框样式覆盖 */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {{
    border: 1px solid {GRAY_300} !important;
    border-radius: {RADIUS_MD} !important;
    padding: {SPACING_SM} {SPACING_MD} !important;
    font-size: {FONT_SIZE_SM} !important;
    transition: all 0.2s ease !important;
    background: white !important;
}}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {{
    border-color: {PRIMARY_COLOR} !important;
    box-shadow: 0 0 0 3px {PRIMARY_LIGHT} !important;
    outline: none !important;
}}

/* ===== 表格样式 ===== */
.patient-table {{
    width: 100%;
    border-collapse: collapse;
}}

.patient-table thead {{
    background: {GRAY_50};
    border-bottom: 2px solid {GRAY_200};
}}

.patient-table th {{
    padding: {SPACING_MD} {SPACING_LG};
    text-align: left;
    font-size: {FONT_SIZE_XS};
    font-weight: 600;
    color: {GRAY_600};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}}

.patient-table td {{
    padding: {SPACING_MD} {SPACING_LG};
    border-bottom: 1px solid {GRAY_200};
    font-size: {FONT_SIZE_SM};
    color: {GRAY_700};
    vertical-align: middle;
}}

.patient-table tbody tr {{
    transition: background-color 0.15s ease;
}}

.patient-table tbody tr:hover {{
    background-color: {GRAY_50};
}}

.patient-table tbody tr:last-child td {{
    border-bottom: none;
}}

/* ===== 状态标签 ===== */
.status-badge {{
    display: inline-flex;
    align-items: center;
    padding: {SPACING_XS} {SPACING_SM};
    border-radius: {RADIUS_SM};
    font-size: {FONT_SIZE_XS};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}}

.status-pending {{
    background-color: {STATUS_PENDING_BG};
    color: {STATUS_PENDING_TEXT};
}}

.status-completed {{
    background-color: {STATUS_COMPLETED_BG};
    color: {STATUS_COMPLETED_TEXT};
}}

.status-overdue {{
    background-color: {STATUS_OVERDUE_BG};
    color: {STATUS_OVERDUE_TEXT};
}}

/* ===== 按钮样式 ===== */
.action-buttons {{
    display: flex;
    gap: {SPACING_SM};
}}

.btn {{
    padding: {SPACING_SM} {SPACING_MD};
    border-radius: {RADIUS_MD};
    font-size: {FONT_SIZE_SM};
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    display: inline-flex;
    align-items: center;
    gap: {SPACING_XS};
    white-space: nowrap;
}}

.btn-primary {{
    background-color: {PRIMARY_COLOR};
    color: white;
    box-shadow: {SHADOW_SM};
}}

.btn-primary:hover {{
    background-color: {PRIMARY_DARK};
    box-shadow: {SHADOW_MD};
    transform: translateY(-1px);
}}

.btn-primary:active {{
    transform: translateY(0);
}}

.btn-secondary {{
    background-color: white;
    color: {GRAY_700};
    border: 1px solid {GRAY_300};
}}

.btn-secondary:hover {{
    background-color: {GRAY_50};
    border-color: {GRAY_400};
}}

.btn-success {{
    background-color: {SUCCESS_COLOR};
    color: white;
}}

.btn-success:hover {{
    background-color: #059669;
}}

.btn-warning {{
    background-color: {WARNING_COLOR};
    color: white;
}}

.btn-warning:hover {{
    background-color: #D97706;
}}

/* ===== 骨架屏加载动画 ===== */
.skeleton {{
    background: linear-gradient(
        90deg,
        {GRAY_200} 25%,
        {GRAY_100} 50%,
        {GRAY_200} 75%
    );
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s ease-in-out infinite;
    border-radius: {RADIUS_SM};
}}

@keyframes skeleton-loading {{
    0% {{
        background-position: 200% 0;
    }}
    100% {{
        background-position: -200% 0;
    }}
}}

.skeleton-text {{
    height: 16px;
    margin-bottom: {SPACING_SM};
}}

.skeleton-title {{
    height: 24px;
    width: 60%;
    margin-bottom: {SPACING_MD};
}}

/* ===== 微交互动画 ===== */
@keyframes fadeIn {{
    from {{
        opacity: 0;
        transform: translateY(10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.fade-in {{
    animation: fadeIn 0.3s ease-out;
}}

@keyframes slideIn {{
    from {{
        opacity: 0;
        transform: translateX(-20px);
    }}
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

.slide-in {{
    animation: slideIn 0.4s ease-out;
}}

/* ===== 提示框 ===== */
.alert {{
    padding: {SPACING_MD} {SPACING_LG};
    border-radius: {RADIUS_MD};
    margin-bottom: {SPACING_LG};
    border-left: 4px solid;
}}

.alert-info {{
    background-color: {PRIMARY_LIGHT};
    border-color: {PRIMARY_COLOR};
    color: {PRIMARY_DARK};
}}

.alert-warning {{
    background-color: #FEF3C7;
    border-color: {WARNING_COLOR};
    color: #92400E;
}}

.alert-error {{
    background-color: #FEE2E2;
    border-color: {ERROR_COLOR};
    color: #991B1B;
}}

.alert-success {{
    background-color: #D1FAE5;
    border-color: {SUCCESS_COLOR};
    color: #065F46;
}}

/* ===== 侧边栏优化 ===== */
.sidebar {{
    background: white;
    border-right: 1px solid {GRAY_200};
    padding: {SPACING_XL};
}}

.sidebar-title {{
    font-size: {FONT_SIZE_XL};
    font-weight: 700;
    color: {GRAY_900};
    margin-bottom: {SPACING_LG};
    padding-bottom: {SPACING_MD};
    border-bottom: 2px solid {PRIMARY_COLOR};
}}

.nav-button {{
    width: 100%;
    padding: {SPACING_MD};
    margin-bottom: {SPACING_SM};
    border: none;
    background: transparent;
    border-radius: {RADIUS_MD};
    text-align: left;
    font-size: {FONT_SIZE_SM};
    color: {GRAY_600};
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: {SPACING_SM};
}}

.nav-button:hover {{
    background-color: {GRAY_100};
    color: {GRAY_900};
}}

.nav-button.active {{
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY_COLOR};
    font-weight: 600;
}}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {{
    .main-container {{
        padding: {SPACING_MD};
    }}
    
    .metrics-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .filter-bar {{
        flex-direction: column;
    }}
    
    .filter-group {{
        width: 100%;
    }}
    
    .action-buttons {{
        flex-direction: column;
    }}
}}

/* 小屏幕手机适配 */
@media (max-width: 480px) {{
    .metrics-grid {{
        grid-template-columns: 1fr;
    }}
}}

/* ===== Streamlit 特定覆盖 ===== */
.stApp {{
    background-color: {GRAY_50} !important;
}}

.stButton > button {{
    border-radius: {RADIUS_MD} !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: {SHADOW_MD} !important;
}}

.stExpander {{
    border: 1px solid {GRAY_200} !important;
    border-radius: {RADIUS_MD} !important;
    margin-bottom: {SPACING_MD} !important;
}}

/* ===== 按钮波纹效果 ===== */
.stButton > button {{
    position: relative;
    overflow: hidden;
}}

.stButton > button:active::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 5px;
    background: rgba(255, 255, 255, 0.5);
    opacity: 0;
    border-radius: 100%;
    transform: scale(1, 1) translate(-50%);
    transform-origin: 50% 50%;
}}

@keyframes ripple {{
    0% {{
        transform: scale(0, 0);
        opacity: 1;
    }}
    20% {{
        transform: scale(25, 25);
        opacity: 1;
    }}
    100% {{
        opacity: 0;
        transform: scale(40, 40);
    }}
}}

.stButton > button:focus:not(:active)::after {{
    animation: ripple 0.6s ease-out;
}}

/* ===== 数据行悬停效果 ===== */
.data-row {{
    transition: all 0.2s ease;
}}

.data-row:hover {{
    background-color: {GRAY_50};
    transform: translateX(4px);
}}

/* ===== 渐入动画 ===== */
.fade-in {{
    animation: fadeIn 0.5s ease-in;
}}

@keyframes fadeIn {{
    from {{
        opacity: 0;
    }}
    to {{
        opacity: 1;
    }}
}}

/* ===== 滑入动画 ===== */
.slide-in {{
    animation: slideIn 0.5s ease-out;
}}

@keyframes slideIn {{
    from {{
        opacity: 0;
        transform: translateX(-20px);
    }}
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

/* ===== 脉冲动画（用于提醒） ===== */
.pulse {{
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{
        opacity: 1;
    }}
    50% {{
        opacity: 0.5;
    }}
}}

/* ===== 摇晃动画（用于错误提示） ===== */
.shake {{
    animation: shake 0.5s ease-in-out;
}}

@keyframes shake {{
    0%, 100% {{
        transform: translateX(0);
    }}
    10%, 30%, 50%, 70%, 90% {{
        transform: translateX(-5px);
    }}
    20%, 40%, 60%, 80% {{
        transform: translateX(5px);
    }}
}}

/* ===== 缩放动画（用于成功提示） ===== */
.scale-in {{
    animation: scaleIn 0.3s ease-out;
}}

@keyframes scaleIn {{
    from {{
        opacity: 0;
        transform: scale(0.8);
    }}
    to {{
        opacity: 1;
        transform: scale(1);
    }}
}}

/* ===== 加载旋转动画 ===== */
.spin {{
    animation: spin 1s linear infinite;
}}

@keyframes spin {{
    from {{
        transform: rotate(0deg);
    }}
    to {{
        transform: rotate(360deg);
    }}
}}

/* ===== 弹跳动画 ===== */
.bounce {{
    animation: bounce 1s ease infinite;
}}

@keyframes bounce {{
    0%, 100% {{
        transform: translateY(0);
    }}
    50% {{
        transform: translateY(-10px);
    }}
}}

/* ===== 通知徽章动画 ===== */
.badge-pulse {{
    animation: badgePulse 1.5s ease-in-out infinite;
}}

@keyframes badgePulse {{
    0% {{
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }}
    70% {{
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }}
    100% {{
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }}
}}

/* ===== 渐变边框动画 ===== */
.gradient-border {{
    position: relative;
    background: white;
    border-radius: {RADIUS_LG};
}}

.gradient-border::before {{
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: {RADIUS_LG};
    padding: 2px;
    background: linear-gradient(45deg, {PRIMARY_COLOR}, {SUCCESS_COLOR}, {WARNING_COLOR}, {ERROR_COLOR});
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    animation: gradientRotate 3s linear infinite;
}}

@keyframes gradientRotate {{
    0% {{
        filter: hue-rotate(0deg);
    }}
    100% {{
        filter: hue-rotate(360deg);
    }}
}}

/* ===== 数字滚动动画 ===== */
.count-up {{
    transition: all 0.3s ease;
}}

.count-up:hover {{
    transform: scale(1.1);
    color: {PRIMARY_COLOR};
}}

/* ===== 工具提示动画 ===== */
.tooltip {{
    position: relative;
    cursor: help;
}}

.tooltip::after {{
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-5px);
    padding: {SPACING_XS} {SPACING_SM};
    background: {GRAY_900};
    color: white;
    font-size: {FONT_SIZE_XS};
    border-radius: {RADIUS_SM};
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
}}

.tooltip:hover::after {{
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(-10px);
}}

/* ===== 进度条动画 ===== */
.progress-bar {{
    height: 8px;
    background: {GRAY_200};
    border-radius: {RADIUS_SM};
    overflow: hidden;
    position: relative;
}}

.progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, {PRIMARY_COLOR}, {SUCCESS_COLOR});
    border-radius: {RADIUS_SM};
    transition: width 0.5s ease;
    position: relative;
    overflow: hidden;
}}

.progress-fill::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    animation: shimmer 2s infinite;
}}

@keyframes shimmer {{
    0% {{
        transform: translateX(-100%);
    }}
    100% {{
        transform: translateX(100%);
    }}
}}

/* ===== 卡片翻转效果 ===== */
.flip-card {{
    perspective: 1000px;
}}

.flip-card-inner {{
    transition: transform 0.6s;
    transform-style: preserve-3d;
}}

.flip-card:hover .flip-card-inner {{
    transform: rotateY(180deg);
}}

/* ===== 打字机效果 ===== */
.typewriter {{
    overflow: hidden;
    border-right: 2px solid {PRIMARY_COLOR};
    white-space: nowrap;
    animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
}}

@keyframes typing {{
    from {{
        width: 0;
    }}
    to {{
        width: 100%;
    }}
}}

@keyframes blink-caret {{
    from, to {{
        border-color: transparent;
    }}
    50% {{
        border-color: {PRIMARY_COLOR};
    }}
}}

/* ===== 悬浮提示框 ===== */
.float-alert {{
    animation: float 3s ease-in-out infinite;
}}

@keyframes float {{
    0%, 100% {{
        transform: translateY(0);
    }}
    50% {{
        transform: translateY(-10px);
    }}
}}

/* ===== 淡出动画 ===== */
.fade-out {{
    animation: fadeOut 0.5s ease-out;
}}

@keyframes fadeOut {{
    from {{
        opacity: 1;
    }}
    to {{
        opacity: 0;
    }}
}}

</style>
"""

def get_metric_card_html(icon, value, label, trend=None, card_type="default"):
    """生成指标卡片HTML"""
    type_class = ""
    if card_type == "warning":
        type_class = "warning"
    elif card_type == "danger":
        type_class = "danger"
    elif card_type == "success":
        type_class = "success"
    
    trend_html = f'<div class="metric-trend">{trend}</div>' if trend else ""
    
    return f"""
    <div class="metric-card {type_class} fade-in">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {trend_html}
    </div>
    """

def get_status_badge(status):
    """生成状态标签HTML"""
    status_map = {
        'pending': ('待回访', 'status-pending'),
        'completed': ('已完成', 'status-completed'),
        'overdue': ('已逾期', 'status-overdue')
    }
    
    text, css_class = status_map.get(status, ('未知', 'status-pending'))
    return f'<span class="status-badge {css_class}">{text}</span>'

# ===== 图标系统辅助函数 =====

def get_icon_html(icon_name, size="md", color=None, custom_class=""):
    """
    生成Font Awesome图标HTML
    
    参数:
        icon_name: 图标名称，如 'phone', 'user', 'calendar'
        size: 图标尺寸 - 'xs', 'sm', 'md', 'lg', 'xl', '2x', '3x'
        color: 图标颜色（可选），如 '#2563EB' 或 'primary'
        custom_class: 自定义CSS类（可选）
    
    返回:
        HTML字符串
    """
    size_map = {
        'xs': 'fa-xs',
        'sm': 'fa-sm',
        'md': '',
        'lg': 'fa-lg',
        'xl': 'fa-xl',
        '2x': 'fa-2x',
        '3x': 'fa-3x'
    }
    
    size_class = size_map.get(size, '')
    style_attr = f'style="color: {color};"' if color else ''
    class_attr = f'class="fas fa-{icon_name} {size_class} {custom_class}"'.strip()
    
    return f'<i {class_attr} {style_attr}></i>'

def get_button_icon(icon_name, label, button_type="primary"):
    """
    生成带图标的按钮文本
    
    参数:
        icon_name: 图标名称
        label: 按钮文本
        button_type: 按钮类型 - 'primary', 'success', 'warning', 'danger', 'default'
    
    返回:
        HTML字符串
    """
    icon_colors = {
        'primary': PRIMARY_COLOR,
        'success': SUCCESS_COLOR,
        'warning': WARNING_COLOR,
        'danger': ERROR_COLOR,
        'default': GRAY_600
    }
    
    color = icon_colors.get(button_type, GRAY_600)
    icon_html = get_icon_html(icon_name, size='sm', color=color)
    
    return f'{icon_html} {label}'

def get_action_icon(action_type, size="md"):
    """
    获取常用操作图标
    
    参数:
        action_type: 操作类型
            - 'complete': 完成
            - 'edit': 编辑
            - 'delete': 删除
            - 'view': 查看
            - 'add': 添加
            - 'refresh': 刷新
            - 'search': 搜索
            - 'filter': 筛选
            - 'export': 导出
            - 'import': 导入
            - 'phone': 电话
            - 'calendar': 日历
            - 'user': 用户
            - 'message': 消息
            - 'warning': 警告
            - 'info': 信息
            - 'success': 成功
            - 'error': 错误
        size: 图标尺寸
    
    返回:
        HTML字符串
    """
    icon_map = {
        'complete': 'check-circle',
        'edit': 'edit',
        'delete': 'trash-alt',
        'view': 'eye',
        'add': 'plus-circle',
        'refresh': 'sync-alt',
        'search': 'search',
        'filter': 'filter',
        'export': 'download',
        'import': 'upload',
        'phone': 'phone',
        'calendar': 'calendar-alt',
        'user': 'user',
        'message': 'comment-dots',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'success': 'check-circle',
        'error': 'times-circle'
    }
    
    color_map = {
        'complete': SUCCESS_COLOR,
        'edit': INFO_COLOR,
        'delete': ERROR_COLOR,
        'view': PRIMARY_COLOR,
        'add': SUCCESS_COLOR,
        'refresh': INFO_COLOR,
        'search': GRAY_600,
        'filter': GRAY_600,
        'export': PRIMARY_COLOR,
        'import': SUCCESS_COLOR,
        'phone': SUCCESS_COLOR,
        'calendar': WARNING_COLOR,
        'user': PRIMARY_COLOR,
        'message': INFO_COLOR,
        'warning': WARNING_COLOR,
        'info': INFO_COLOR,
        'success': SUCCESS_COLOR,
        'error': ERROR_COLOR
    }
    
    icon_name = icon_map.get(action_type, 'circle')
    color = color_map.get(action_type, GRAY_600)
    
    return get_icon_html(icon_name, size=size, color=color)

# 常用图标快捷方式
def icon_phone():
    return get_icon_html('phone', color=SUCCESS_COLOR)

def icon_calendar():
    return get_icon_html('calendar-alt', color=WARNING_COLOR)

def icon_user():
    return get_icon_html('user', color=PRIMARY_COLOR)

def icon_check():
    return get_icon_html('check-circle', color=SUCCESS_COLOR)

def icon_warning():
    return get_icon_html('exclamation-triangle', color=WARNING_COLOR)

def icon_error():
    return get_icon_html('times-circle', color=ERROR_COLOR)

def icon_info():
    return get_icon_html('info-circle', color=INFO_COLOR)

def icon_search():
    return get_icon_html('search', color=GRAY_600)

def icon_filter():
    return get_icon_html('filter', color=GRAY_600)

def icon_add():
    return get_icon_html('plus-circle', color=SUCCESS_COLOR)

def icon_edit():
    return get_icon_html('edit', color=INFO_COLOR)

def icon_delete():
    return get_icon_html('trash-alt', color=ERROR_COLOR)

def icon_refresh():
    return get_icon_html('sync-alt', color=INFO_COLOR)

def icon_export():
    return get_icon_html('download', color=PRIMARY_COLOR)

def icon_import():
    return get_icon_html('upload', color=SUCCESS_COLOR)
