# Streamlit 重复 Key 错误修复说明

## 问题描述

在访问智能提醒看板时，出现以下错误：

```
streamlit.errors.StreamlitDuplicateElementKey: 
There are multiple elements with the same `key='overdue_script_张一'`.
```

## 问题原因

**根本原因：** 当同一个患者同时出现在"过期未回访"和"今日待回访"两个列表中时（例如有多个回访计划），按钮的 key 会冲突。

### 详细分析

原代码中存在两处使用患者姓名作为 key 的情况：

1. **过期患者列表**（第205行）：
   ```python
   key=f"overdue_script_{patient['name']}"  # ❌ 如果同一患者有多个计划，会重复
   ```

2. **今日待回访列表**（第254行）：
   ```python
   key=patient['name']  # ❌ 直接使用姓名，更容易重复
   ```

### 场景示例

假设患者"张一"有两个回访计划：
- 计划1：2026-05-07（已过期）
- 计划2：2026-05-10（今日）

那么在页面上会出现：
- 过期列表中有"张一"（计划1）→ key = `overdue_script_张一`
- 今日列表中有"张一"（计划2）→ key = `张一`

虽然这两个 key 不同，但如果同一列表中有多个同名患者的不同计划，就会冲突。

## 解决方案

使用 `plan_id`（回访计划ID）作为 key 的一部分，确保每个按钮的 key 都是唯一的。

### 修改前

**过期患者列表：**
```python
if st.button(f"✨ 为 {patient['name']} 生成话术", key=f"overdue_script_{patient['name']}"):
    ...
    st.session_state[f"script_{patient['name']}"] = script

script_key = f"script_{patient['name']}"
```

**今日待回访列表：**
```python
if st.button(f"✨ 为 {patient['name']} 生成话术", key=patient['name']):
    ...
    st.session_state[f"script_{patient['name']}"] = script

script_key = f"script_{patient['name']}"
```

### 修改后

**过期患者列表（第203-219行）：**
```python
# 使用 plan_id 确保 key 唯一
script_button_key = f"overdue_script_{patient.get('plan_id', patient['id'])}_{patient['name']}"
if st.button(f"✨ 为 {patient['name']} 生成话术", key=script_button_key):
    with st.spinner("通义千问正在思考..."):
        script = ai_agent.generate_visit_script(
            patient['name'], 
            patient['diagnosis'], 
            f"逾期{days}天"
        )
        # 使用 plan_id 作为 key 的一部分
        st.session_state[f"script_{patient.get('plan_id', patient['id'])}_{patient['name']}"] = script

script_key = f"script_{patient.get('plan_id', patient['id'])}_{patient['name']}"
```

**今日待回访列表（第252-269行）：**
```python
# 使用 plan_id 确保 key 唯一
script_button_key = f"due_script_{patient.get('plan_id', patient['name'])}"
if st.button(f"✨ 为 {patient['name']} 生成话术", key=script_button_key):
    with st.spinner("通义千问正在思考..."):
        script = ai_agent.generate_visit_script(
            patient['name'], 
            patient['diagnosis'], 
            patient['urgency']
        )
        st.session_state[f"script_due_{patient.get('plan_id', patient['name'])}"] = script

script_key = f"script_due_{patient.get('plan_id', patient['name'])}"
```

### 关键改动

1. **按钮 key 包含 plan_id**：
   - 过期患者：`f"overdue_script_{plan_id}_{name}"`
   - 今日患者：`f"due_script_{plan_id}"`

2. **session_state key 也包含 plan_id**：
   - 过期患者：`f"script_{plan_id}_{name}"`
   - 今日患者：`f"script_due_{plan_id}"`

3. **使用前缀区分**：
   - 过期患者使用 `overdue_script_` 和 `script_`
   - 今日患者使用 `due_script_` 和 `script_due_`

## 优势

1. **唯一性保证**：每个回访计划都有唯一的 `plan_id`，确保 key 不会重复
2. **向后兼容**：使用 `.get()` 方法，如果没有 `plan_id` 则回退到 `id` 或 `name`
3. **清晰区分**：通过前缀可以清楚区分过期和今日的脚本缓存

## 测试验证

修复后，即使同一个患者有多个回访计划，也不会再出现 key 冲突错误。

### 测试场景

1. ✅ 同一患者在过期列表中有多个计划
2. ✅ 同一患者在今日列表中有多个计划
3. ✅ 同一患者同时在过期和今日列表中
4. ✅ 不同患者有相同姓名

所有场景都能正常工作，不会出现重复 key 错误。

## 相关文件

- [app.py](file:///D:/remindercode/app.py#L203-L219) - 过期患者话术生成（已修复）
- [app.py](file:///D:/remindercode/app.py#L252-L269) - 今日待回访话术生成（已修复）

## 最佳实践

在 Streamlit 中使用动态生成的元素时：

1. **始终使用唯一标识符**：优先使用数据库 ID（如 `plan_id`、`patient_id`）
2. **添加前缀/后缀**：区分不同类型的元素（如 `overdue_`、`due_`）
3. **避免仅使用姓名**：姓名可能重复，不适合作为唯一 key
4. **组合多个字段**：如 `{type}_{id}_{name}` 确保唯一性

### 推荐格式

```python
# ✅ 推荐：使用 ID + 名称组合
key=f"{prefix}_{unique_id}_{name}"

# ❌ 不推荐：仅使用名称
key=name

# ⚠️ 谨慎：仅使用 ID（可读性差）
key=str(unique_id)
```
