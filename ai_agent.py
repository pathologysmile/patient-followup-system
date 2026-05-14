import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 加载 .env 文件中的配置
load_dotenv()

# 获取通义千问 API 配置（支持 Streamlit Secrets 和环境变量）
def get_dashscope_config():
    """获取 DashScope 配置（优先从 Streamlit Secrets 读取）"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            api_key = st.secrets.get("DASHSCOPE_API_KEY", "").strip()
            model = st.secrets.get("DASHSCOPE_MODEL", "qwen-turbo").strip()
            base_url = st.secrets.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").strip()
            return api_key, model, base_url
    except:
        pass
    
    # 回退到环境变量（本地开发）
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    model = os.getenv("DASHSCOPE_MODEL", "qwen-turbo").strip()
    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").strip()
    return api_key, model, base_url

DASHSCOPE_API_KEY, DASHSCOPE_MODEL, DASHSCOPE_BASE_URL = get_dashscope_config()

# 设置环境变量供 ChatTongyi 使用
if DASHSCOPE_API_KEY:
    os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY
if DASHSCOPE_BASE_URL:
    os.environ["DASHSCOPE_BASE_URL"] = DASHSCOPE_BASE_URL

# 调试信息：检查环境变量是否正确设置
if not DASHSCOPE_API_KEY:
    print("⚠️  警告: DASHSCOPE_API_KEY 未设置！")
    print("请在 Streamlit Cloud Secrets 或 .env 文件中配置 API Key")
else:
    print(f"✅ DASHSCOPE_API_KEY 已配置 (长度: {len(DASHSCOPE_API_KEY)})")
    print(f"✅ DASHSCOPE_MODEL: {DASHSCOPE_MODEL}")
    print(f"✅ DASHSCOPE_BASE_URL: {DASHSCOPE_BASE_URL}")


def _create_chat_model(temperature=0.7):
    """
    安全地创建 ChatTongyi 实例
    
    参数:
        temperature: 温度参数
    
    返回:
        ChatTongyi 实例
    """
    if not DASHSCOPE_API_KEY:
        return None  # 返回 None 而不是抛出异常
    
    return ChatTongyi(
        model=DASHSCOPE_MODEL,
        temperature=temperature
    )

def generate_visit_script(patient_name, diagnosis, urgency):
    """
    利用通义千问生成针对性的回访话术
    根据不同病情诊断给出专业的健康建议
    """
    llm = _create_chat_model(temperature=0.7)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY"

    # 根据诊断类型提供针对性的指导
    diagnosis_guidance = _get_diagnosis_guidance(diagnosis)
    
    prompt_template = """
    你是一位经验丰富的专业护士，擅长与患者进行高情商的沟通。
    
    患者信息：
    - 姓名：{name}
    - 诊断：{diagnosis}
    - 状态：{urgency}
    
    该疾病的重点回访内容：
    {guidance}

    任务：
    请根据上述信息，为医生生成一段温馨、专业的回访开场白。
    要求：
    1. 语气要亲切自然，体现人文关怀。
    2. 针对该疾病给出具体的健康建议和注意事项。
    3. 询问患者的恢复情况和是否有不适症状。
    4. 长度控制在 80-120 字之间。
    5. 如果是逾期回访，要表达歉意并说明来意。
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "name": patient_name,
            "diagnosis": diagnosis,
            "urgency": urgency,
            "guidance": diagnosis_guidance
        })
        return response.content
    except Exception as e:
        return f"AI 生成失败: {str(e)}"

def _get_diagnosis_guidance(diagnosis):
    """
    根据诊断返回针对性的回访指导
    """
    # 将诊断转换为小写以便匹配
    diagnosis_lower = diagnosis.lower()
    
    # 癌症类疾病
    if any(keyword in diagnosis_lower for keyword in ['癌', '肿瘤', '恶性']):
        if '胃' in diagnosis_lower:
            return """- 饮食情况：是否少食多餐，避免辛辣刺激性食物
- 消化功能：有无恶心、呕吐、腹胀等症状
- 体重变化：近期体重是否稳定
- 伤口恢复：手术伤口愈合情况
- 心理状态：情绪是否稳定，有无焦虑抑郁
- 后续治疗：是否需要化疗或放疗"""
        elif '肝' in diagnosis_lower:
            return """- 肝功能指标：最近复查结果如何
- 饮食禁忌：是否严格戒酒，避免油腻食物
- 休息情况：保证充足睡眠，避免劳累
- 腹部症状：有无腹痛、腹胀、黄疸
- 药物服用：是否按时服用保肝药物
- 定期复查：是否按计划进行复查"""
        elif '肺' in diagnosis_lower:
            return """- 呼吸状况：有无咳嗽、咳痰、呼吸困难
- 活动能力：日常活动是否受限
- 戒烟情况：是否已经完全戒烟
- 胸部症状：有无胸痛、胸闷
- 氧饱和度：如有条件可监测
- 康复锻炼：是否进行呼吸功能锻炼"""
        elif '食管' in diagnosis_lower or '食道' in diagnosis_lower:
            return """- 吞咽功能：进食是否顺畅，有无哽噎感
- 饮食类型：是否以流质或半流质为主
- 营养状况：体重变化，营养摄入是否充足
- 反流情况：有无反酸、烧心
- 进食姿势：是否保持坐姿或半卧位进食
- 餐具选择：是否使用小勺，细嚼慢咽"""
        else:
            return """- 整体状况：精神状态和体力恢复情况
- 疼痛管理：有无疼痛，疼痛程度如何
- 治疗方案：后续治疗计划和执行情况
- 营养支持：饮食是否正常，营养摄入情况
- 并发症：有无出现任何不适症状
- 心理支持：情绪状态和家庭支持情况"""
    
    # 心血管疾病
    elif any(keyword in diagnosis_lower for keyword in ['心脏', '心血管', '高血压', '冠心病']):
        return """- 血压监测：每日血压记录情况
- 用药依从：是否按时服用降压药或其他药物
- 症状观察：有无头晕、头痛、胸闷、心悸
- 生活方式：饮食是否低盐低脂，是否戒烟限酒
- 运动情况：是否进行适度的有氧运动
- 定期复查：是否按计划进行心电图等检查"""
    
    # 糖尿病
    elif '糖尿病' in diagnosis_lower or '血糖' in diagnosis_lower:
        return """- 血糖控制：空腹和餐后血糖监测情况
- 饮食管理：是否控制碳水化合物摄入
- 用药情况：胰岛素或口服药的使用情况
- 足部护理：有无足部溃疡、麻木
- 视力变化：有无视力模糊
- 并发症筛查：是否定期检查眼底、肾功能"""
    
    # 骨科疾病
    elif any(keyword in diagnosis_lower for keyword in ['骨折', '关节', '骨科', '脊柱']):
        return """- 疼痛评估：疼痛程度和变化情况
- 活动能力：日常活动是否受限
- 康复训练：是否按医嘱进行功能锻炼
- 伤口情况：手术伤口愈合情况
- 用药情况：止痛药或其他药物的使用
- 辅助设备：拐杖、轮椅等使用情况"""
    
    # 消化系统疾病
    elif any(keyword in diagnosis_lower for keyword in ['胃', '肠', '消化', '肝胆']):
        return """- 饮食情况：饮食习惯和食欲变化
- 消化症状：有无腹痛、腹胀、恶心、呕吐
- 排便情况：大便性状和频率
- 体重变化：近期体重波动情况
- 用药情况：是否按时服用相关药物
- 生活规律：作息是否规律，压力情况"""
    
    # 呼吸系统疾病
    elif any(keyword in diagnosis_lower for keyword in ['肺炎', '呼吸', '哮喘', '慢阻肺']):
        return """- 呼吸状况：有无咳嗽、咳痰、呼吸困难
- 体温监测：有无发热
- 用药情况：抗生素或支气管扩张剂使用
- 活动耐力：日常活动是否气喘
- 环境因素：是否避免烟雾、粉尘刺激
- 氧疗情况：如需要，是否正确吸氧"""
    
    # 默认通用指导
    else:
        return """- 整体恢复：精神状态和体力恢复情况
- 症状观察：有无任何不适症状
- 用药依从：是否按时服用药物
- 饮食起居：饮食和睡眠情况
- 复诊计划：是否按医嘱定期复诊
- 生活调整：生活方式的改善情况"""

def chat_with_agent(message, history=None):
    """
    与智能体进行对话
    """
    llm = _create_chat_model(temperature=0.7)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY"
    
    # 构建系统提示
    system_prompt = """你是一位专业的医疗助手，专门帮助医护人员进行患者回访工作。
    你可以：
    1. 提供患者回访的建议和技巧
    2. 解答关于常见疾病护理的问题
    3. 协助生成个性化的回访话术
    4. 提供健康管理建议
    
    请用专业、温暖、易懂的语言回答问题。"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    # 添加历史对话
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    
    # 添加当前消息
    messages.append(HumanMessage(content=message))
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"AI 回复失败: {str(e)}"

def optimize_visit_script(patient_name, diagnosis, previous_feedback, original_script=''):
    """
    根据患者反馈优化回访话术
    
    参数:
        patient_name: 患者姓名
        diagnosis: 诊断
        previous_feedback: 之前的患者反馈
        original_script: 原始话术（可选）
    
    返回:
        优化后的话术
    """
    llm = _create_chat_model(temperature=0.6)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY"
    
    prompt_template = """
    你是一位经验丰富的医疗沟通专家，擅长根据患者反馈优化回访话术。
    
    患者信息：
    - 姓名：{name}
    - 诊断：{diagnosis}
    
    患者之前的反馈：
    {feedback}
    
    原始话术（如果有）：
    {original}
    
    任务：
    请根据患者的反馈，优化回访话术，使其更加个性化和有针对性。
    
    要求：
    1. 针对患者提到的具体问题或关注点进行调整
    2. 保持专业和温暖的语气
    3. 体现对患者反馈的重视和回应
    4. 提供更具体的健康建议
    5. 长度控制在 100-150 字之间
    6. 如果患者有负面情绪，要给予安慰和鼓励
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "name": patient_name,
            "diagnosis": diagnosis,
            "feedback": previous_feedback,
            "original": original_script if original_script else "无"
        })
        return response.content
    except Exception as e:
        return f"AI 优化失败: {str(e)}"

def predict_recurrence_risk(diagnosis, patient_history, visit_records):
    """
    基于历史数据预测复发风险
    
    参数:
        diagnosis: 诊断
        patient_history: 患者历史信息（字典）
        visit_records: 回访记录列表
    
    返回:
        风险评估结果（字典）
    """
    llm = _create_chat_model(temperature=0.3)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return {
            "full_assessment": "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY",
            "risk_level": "未知",
            "risk_score": 0,
            "recommended_frequency": "常规随访"
        }
    
    # 构建患者历史摘要
    history_summary = f"""
    患者基本信息：
    - 性别：{patient_history.get('gender', '未知')}
    - 出院日期：{patient_history.get('discharge_date', '未知')}
    - 住院号：{patient_history.get('hospital_number', '无')}
    
    回访记录摘要：
    """
    
    if visit_records:
        for i, record in enumerate(visit_records[:5], 1):  # 最近5条记录
            history_summary += f"""
{i}. 日期：{record.get('visit_date', '未知')}
   - 健康状况：{record.get('health_status', '未知')}
   - 回访内容：{record.get('record_content', '无')[:50]}...
   - 患者反馈：{record.get('patient_feedback', '无')[:50]}...
   - 用药情况：{record.get('medication_info', '未知')}
"""
    else:
        history_summary += "暂无回访记录"
    
    prompt_template = """
    你是一位资深的临床医生，擅长疾病预后评估和风险管理。
    
    患者信息：
    - 诊断：{diagnosis}
    
    {history}
    
    任务：
    请基于上述信息，评估该患者的复发风险和康复情况。
    
    请按以下格式输出：
    
    【风险评估】
    - 风险等级：[低风险/中风险/高风险]
    - 风险评分：[0-100分]
    - 主要风险因素：[列出2-3个]
    
    【康复状况】
    - 整体评估：[良好/一般/较差]
    - 恢复进度：[描述]
    - 关键指标：[列出需要关注的指标]
    
    【建议措施】
    - 回访频率：[建议的回访间隔]
    - 重点关注：[需要特别关注的方面]
    - 生活建议：[具体的生活指导]
    - 就医建议：[是否需要进一步检查或治疗]
    
    要求：
    1. 评估要客观、专业
    2. 基于实际数据，避免过度推测
    3. 给出具体可操作的建议
    4. 如有高风险因素，要明确指出
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "diagnosis": diagnosis,
            "history": history_summary
        })
        
        # 解析响应，提取关键信息
        result = {
            "full_assessment": response.content,
            "risk_level": _extract_risk_level(response.content),
            "risk_score": _extract_risk_score(response.content),
            "recommended_frequency": _extract_frequency(response.content)
        }
        
        return result
    except Exception as e:
        return {
            "full_assessment": f"AI 评估失败: {str(e)}",
            "risk_level": "未知",
            "risk_score": 0,
            "recommended_frequency": "常规随访"
        }

def recommend_visit_frequency(diagnosis, risk_assessment, patient_age=None):
    """
    推荐个性化回访频率
    
    参数:
        diagnosis: 诊断
        risk_assessment: 风险评估结果
        patient_age: 患者年龄（可选）
    
    返回:
        回访频率建议
    """
    llm = _create_chat_model(temperature=0.5)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY"
    
    prompt_template = """
    你是一位专业的慢病管理专家，擅长制定个性化的随访计划。
    
    患者信息：
    - 诊断：{diagnosis}
    - 风险等级：{risk_level}
    - 风险评分：{risk_score}
    - 年龄：{age}
    
    任务：
    请为该患者推荐个性化的回访频率和随访计划。
    
    要求：
    1. 考虑疾病类型和风险等级
    2. 给出具体的回访时间安排
    3. 说明每个阶段的重点关注内容
    4. 提供调整建议的条件
    
    请按以下格式输出：
    
    【近期安排（1-3个月）】
    - 回访频率：[例如：每2周一次]
    - 重点内容：[需要关注的方面]
    
    【中期安排（3-6个月）】
    - 回访频率：[例如：每月一次]
    - 重点内容：[需要关注的方面]
    
    【长期安排（6个月后）】
    - 回访频率：[例如：每3个月一次]
    - 重点内容：[需要关注的方面]
    
    【调整建议】
    - 增加频率的情况：[什么情况下需要更频繁回访]
    - 减少频率的情况：[什么情况下可以减少回访]
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "diagnosis": diagnosis,
            "risk_level": risk_assessment.get('risk_level', '中风险'),
            "risk_score": risk_assessment.get('risk_score', 50),
            "age": patient_age if patient_age else "未知"
        })
        return response.content
    except Exception as e:
        return f"AI 推荐失败: {str(e)}"

def learn_from_excellent_cases(case_description, key_points):
    """
    学习优秀回访案例，提取经验
    
    参数:
        case_description: 案例描述
        key_points: 关键点总结
    
    返回:
        学习总结和建议
    """
    llm = _create_chat_model(temperature=0.7)
    
    # 如果 API Key 未配置，返回提示
    if llm is None:
        return "⚠️ AI 功能暂未启用（API Key 未配置）\n请联系管理员配置 DASHSCOPE_API_KEY"
    
    prompt_template = """
    你是一位医疗质量管理专家，擅长从优秀案例中提取最佳实践。
    
    优秀回访案例：
    {case}
    
    案例关键点：
    {points}
    
    任务：
    请分析这个优秀案例，提取可复制的经验和技巧。
    
    请按以下格式输出：
    
    【成功经验】
    1. [经验点1]
    2. [经验点2]
    3. [经验点3]
    
    【沟通技巧】
    - 开场方式：[如何开始对话]
    - 提问技巧：[如何引导患者表达]
    - 倾听方法：[如何有效倾听]
    - 回应策略：[如何回应患者]
    
    【可复制做法】
    - 适用场景：[在什么情况下可以使用]
    - 注意事项：[需要注意的地方]
    - 改进建议：[可以优化的方面]
    
    【话术模板】
    提供一个可复用的话术模板，供其他医护人员参考。
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "case": case_description,
            "points": key_points
        })
        return response.content
    except Exception as e:
        return f"AI 学习失败: {str(e)}"

# 辅助函数：从评估文本中提取关键信息
def _extract_risk_level(text):
    """提取风险等级"""
    if "高风险" in text:
        return "高风险"
    elif "低风险" in text:
        return "低风险"
    else:
        return "中风险"

def _extract_risk_score(text):
    """提取风险评分"""
    import re
    match = re.search(r'风险评分[：:]\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return 50  # 默认中等风险

def _extract_frequency(text):
    """提取建议频率"""
    if "每周" in text or "1周" in text:
        return "每周回访"
    elif "2周" in text or "半月" in text:
        return "每2周回访"
    elif "每月" in text or "1月" in text:
        return "每月回访"
    elif "3个月" in text or "季度" in text:
        return "每季度回访"
    else:
        return "常规随访"
