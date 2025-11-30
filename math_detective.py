import streamlit as st
import random
import time
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="聪博士AI乐园", page_icon="🎓", layout="centered")
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .step-header { color: #2E86C1; font-weight: bold; font-size: 18px; margin-top: 10px;}
    .stButton>button { background-color: #f0f2f6; border: 2px solid #d1d5db; color: black; border-radius: 8px; font-weight: bold; width: 100%; }
    .stButton>button:hover { border-color: #2E86C1; color: #2E86C1; }
    /* 进度条样式 */
    .stProgress > div > div > div > div { background-color: #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 智能思维题目生成器 (核心引擎) ---

def generate_logic_problem(level_name):
    """
    生成一道带有“思维逻辑元数据”的题目
    返回字典包含：desc(题干), nums(数字), logic_type(逻辑描述), 
    distractors(逻辑干扰项), op(符号), equation(算式), answer(答案)
    """
    
    # === 三年级主线 ===
    if "第一关" in level_name: # 时间
        h = random.randint(7, 10)
        m = random.randint(10, 40)
        duration = random.randint(15, 40)
        start_time = f"{h}:{m}"
        
        # 模式：求结束时间
        return {
            "desc": f"电影 **{start_time}** 开始放映，放映时长 **{duration}分钟**，电影几点结束？",
            "nums": [start_time, duration],
            "logic_type": "推算结束时间（往后推）",
            "distractors": ["推算开始时间（往前推）", "计算经过了多久"],
            "op": "+",
            "equation": f"{start_time} + {duration}分", # 只是示意
            "answer": "结束时间", # 时间计算特殊，由后续逻辑处理
            "is_time_calc": True, # 标记为特殊计算
            "base_time": h*60+m,
            "add_min": duration,
            "calc_type": "add"
        }

    elif "第二关" in level_name: # 加减法
        a = random.randint(120, 350)
        b = random.randint(120, 350)
        if random.random() > 0.5:
            return {
                "desc": f"上午有 **{a}** 人，下午来了 **{b}** 人，今天**一共**有多少人？",
                "nums": [a, b],
                "logic_type": "把两部分合起来 (求总数)",
                "distractors": ["从总数里拿走一部分 (求剩余)", "比较谁多谁少"],
                "op": "+",
                "equation": f"{a} + {b}",
                "answer": str(a + b)
            }
        else:
            total = a + b
            return {
                "desc": f"总共有 **{total}** 个气球，飞走了 **{a}** 个，还**剩**多少个？",
                "nums": [total, a],
                "logic_type": "从总数里去掉一部分 (求剩余)",
                "distractors": ["把两部分合起来 (求总数)", "求几个几是多少"],
                "op": "-",
                "equation": f"{total} - {a}",
                "answer": str(b)
            }

    elif "第三关" in level_name: # 测量
        m = random.randint(2, 8)
        return {
            "desc": f"一根绳子长 **{m}米**，它等于多少**厘米**？",
            "nums": [m, 100],
            "logic_type": "大单位变小单位 (乘进率)",
            "distractors": ["小单位变大单位 (除以进率)", "单位没变"],
            "op": "×",
            "equation": f"{m} × 100",
            "answer": str(m * 100)
        }

    elif "第四关" in level_name: # 倍数
        base = random.randint(4, 9)
        multiple = random.randint(3, 8)
        total = base * multiple
        if random.random() > 0.5:
            return {
                "desc": f"白兔有 **{base}** 只，黑兔是白兔的 **{multiple}倍**，黑兔有多少只？",
                "nums": [base, multiple],
                "logic_type": "求一个数的几倍是多少",
                "distractors": ["求一个数是另一个数的几倍", "把两部分合起来"],
                "op": "×",
                "equation": f"{base} × {multiple}",
                "answer": str(total)
            }
        else:
            return {
                "desc": f"钢笔 **{total}** 元，铅笔 **{base}** 元，钢笔价格是铅笔的**几倍**？",
                "nums": [total, base],
                "logic_type": "求一个数是另一个数的几倍",
                "distractors": ["求一个数的几倍是多少", "求两者相差多少"],
                "op": "÷",
                "equation": f"{total} ÷ {base}",
                "answer": str(multiple)
            }

    elif "第五关" in level_name: # 乘法
        price = random.randint(15, 45)
        count = random.randint(3, 8)
        return {
            "desc": f"书包每个 **{price}** 元，买 **{count}** 个需要多少钱？",
            "nums": [price, count],
            "logic_type": "求几个几是多少 (总价)",
            "distractors": ["把两部分合起来", "平均分"],
            "op": "×",
            "equation": f"{price} × {count}",
            "answer": str(price * count)
        }
    
    elif "第六关" in level_name: # 图形周长
        l = random.randint(10, 30)
        w = random.randint(5, l-2)
        return {
            "desc": f"长方形长 **{l}**，宽 **{w}**，求它的**周长**。",
            "nums": [l, w],
            "logic_type": "封闭图形一周的长度",
            "distractors": ["图形里面的大小 (面积)", "两边之和"],
            "op": "+", # 复合运算，这里简化逻辑引导
            "equation": f"({l} + {w}) × 2", 
            "answer": str((l+w)*2),
            "is_geometry": True # 特殊标记
        }

    elif "第七关" in level_name: # 分数
        return {
            "desc": "一块巧克力，小明吃了 **1/5**，小红吃了 **2/5**，两人**一共**吃了多少？",
            "nums": ["1/5", "2/5"],
            "logic_type": "同分母分数相加",
            "distractors": ["分数相乘", "求剩余部分"],
            "op": "+",
            "equation": "1/5 + 2/5",
            "answer": "3/5"
        }

    # === 基础堡垒 ===
    elif "基础2" in level_name: # 乘法口诀
        a = random.randint(3, 9)
        b = random.randint(3, 9)
        return {
            "desc": f"**{a}** 个 **{b}** 是多少？",
            "nums": [a, b],
            "logic_type": "几个几相加 (乘法意义)",
            "distractors": ["把两个数合并", "平均分"],
            "op": "×",
            "equation": f"{a} × {b}",
            "answer": str(a * b)
        }

    elif "基础3" in level_name: # 余数
        divisor = random.randint(3, 6)
        quotient = random.randint(2, 5)
        rem = random.randint(1, divisor-1)
        dividend = divisor * quotient + rem
        return {
            "desc": f"把 **{dividend}** 个苹果，平均分给 **{divisor}** 人，每人分几个？还剩几个？",
            "nums": [dividend, divisor],
            "logic_type": "平均分后有剩余",
            "distractors": ["求几倍是多少", "把两部分合起来"],
            "op": "÷",
            "equation": f"{dividend} ÷ {divisor}",
            "answer": str(rem), # 这里特指填余数，简化交互
            "is_remainder": True,
            "full_ans": f"{quotient}余{rem}"
        }

    # 默认兜底
    return {
        "desc": f"计算 **10 + 5**", "nums":[10,5], "logic_type":"合并", "distractors":["减少"], "op":"+", "equation":"10+5", "answer":"15"
    }

# --- 3. 辅助逻辑 ---
def check_equation(user_eq, correct_eq, op):
    """检查算式是否大致正确"""
    u = user_eq.replace(" ", "").replace("*", "×").replace("/", "÷")
    c = correct_eq.replace(" ", "")
    
    # 允许加法和乘法交换律
    if u == c: return True
    if op in ["+", "×"]:
        # 简单处理：如果是 a+b，允许输入 b+a
        # 这里为了演示简单，暂时只严格匹配，或者你可以自己输数字
        pass
    return u == c

# --- 4. 主程序 ---
def main():
    if 'current_level' not in st.session_state: st.session_state['current_level'] = None
    if 'zone' not in st.session_state: st.session_state['zone'] = "三年级主线任务"
    if 'mode' not in st.session_state: st.session_state['mode'] = 'menu'
    
    # 四步法状态管理
    if 'logic_step' not in st.session_state: st.session_state['logic_step'] = 1 # 1:分析, 2:工具, 3:蓝图, 4:施工
    if 'problem' not in st.session_state: st.session_state['problem'] = None
    if 'solved_count' not in st.session_state: st.session_state['solved_count'] = 0

    # --- 侧边栏 ---
    with st.sidebar:
        st.header("🗺️ 侦探地图")
        zone = st.radio("区域切换", ["三年级主线任务", "一二年级基础堡垒"])
        if zone != st.session_state['zone']:
            st.session_state['zone'] = zone
            st.session_state['current_level'] = None
            st.rerun()

        st.markdown("---")
        
        # 关卡定义
        levels_g3 = ["第一关：时分秒", "第二关：加减法", "第三关：测量", "第四关：倍的认识", "第五关：乘法", "第六关：图形", "第七关：分数"]
        levels_fd = ["基础1：凑十法(暂无逻辑模式)", "基础2：表内乘法", "基础3：有余数除法", "基础4：米和厘米(暂无逻辑模式)"]
        
        levels = levels_g3 if zone == "三年级主线任务" else levels_fd
        selected = st.radio("选择关卡", levels)
        
        if selected != st.session_state['current_level']:
            st.session_state['current_level'] = selected
            st.session_state['mode'] = 'menu'
            st.session_state['problem'] = None
            st.session_state['logic_step'] = 1
            st.rerun()
            
        st.metric("🏆 连续破案", f"{st.session_state['solved_count']} 起")

    # --- 主区域 ---
    st.markdown("# 🎓 聪博士AI乐园")
    
    # 菜单模式
    if st.session_state['mode'] == 'menu':
        st.info(f"准备好挑战 **{st.session_state['current_level']}** 了吗？")
        st.markdown("我们将通过 **4个步骤** 来解决每一个案件！")
        if st.button("🚀 开始逻辑特训"):
            st.session_state['mode'] = 'practice'
            st.session_state['problem'] = generate_logic_problem(st.session_state['current_level'])
            st.session_state['logic_step'] = 1
            st.rerun()

    # 练习模式
    elif st.session_state['mode'] == 'practice':
        p = st.session_state['problem']
        
        # 顶部：题目展示 (始终显示)
        st.markdown("### 📝 案情描述")
        st.warning(f"{p['desc']}")
        
        # 进度条
        progress_map = {1: 25, 2: 50, 3: 75, 4: 100}
        st.progress(progress_map[st.session_state['logic_step']], text=f"当前进度：第 {st.session_state['logic_step']} / 4 步")
        
        st.markdown("---")

        # --- 第一步：侦探分析 ---
        if st.session_state['logic_step'] == 1:
            st.markdown("#### 🕵️ 第一步：侦探分析")
            st.write("请问：这道题里的数字是什么关系？")
            
            # 构建选项
            options = [p['logic_type']] + p['distractors']
            random.shuffle(options)
            
            user_choice = st.radio("选择逻辑关系：", options, label_visibility="collapsed")
            
            if st.button("确认分析"):
                if user_choice == p['logic_type']:
                    st.success("✅ 分析正确！你的逻辑很清晰。")
                    time.sleep(1)
                    st.session_state['logic_step'] = 2
                    st.rerun()
                else:
                    st.error("❌ 不太对哦。再读一遍题目，想想数字是变大还是变小？")

        # --- 第二步：选择工具 ---
        elif st.session_state['logic_step'] == 2:
            st.markdown(f"#### 🛠️ 第二步：选择工具 (逻辑：{p['logic_type']})")
            st.write("我们要用哪个数学符号来解决？")
            
            col1, col2, col3, col4 = st.columns(4)
            ops = ["+", "-", "×", "÷"]
            
            # 使用回调函数处理按钮点击
            def set_op(selected_op):
                if selected_op == p['op']:
                    st.session_state['temp_msg'] = "correct"
                    st.session_state['logic_step'] = 3
                else:
                    st.session_state['temp_msg'] = "wrong"
            
            with col1: 
                if st.button("➕ 加法"): set_op("+")
            with col2: 
                if st.button("➖ 减法"): set_op("-")
            with col3: 
                if st.button("✖️ 乘法"): set_op("×")
            with col4: 
                if st.button("➗ 除法"): set_op("÷")
                
            if 'temp_msg' in st.session_state:
                if st.session_state['temp_msg'] == "wrong":
                    st.error("❌ 工具选错了。想想上面的逻辑关系。")
                del st.session_state['temp_msg']
                if st.session_state['logic_step'] == 3:
                    st.rerun()

        # --- 第三步：构建蓝图 ---
        elif st.session_state['logic_step'] == 3:
            st.markdown(f"#### 📐 第三步：构建蓝图 (工具：{p['op']})")
            st.write(f"请列出算式（题目中数字是 {p['nums']}）：")
            
            st.caption("提示：直接输入算式，例如 3+5 或 3*5，不需要计算结果。")
            user_eq = st.text_input("在此输入算式：")
            
            if st.button("确认蓝图"):
                # 简单验证：是否包含题目中的数字和符号
                # 这里做简化处理，为了体验流畅，只要包含正确符号即可
                # 实际生产中可以做更严格的字符串比对
                if p.get('is_geometry', False): # 几何题算式较复杂，跳过严格检查
                     st.success("✅ 蓝图设计完成！")
                     time.sleep(1)
                     st.session_state['logic_step'] = 4
                     st.rerun()
                elif p.get('op') in user_eq.replace("*","×").replace("/","÷"): 
                    st.success("✅ 算式列对了！")
                    time.sleep(1)
                    st.session_state['logic_step'] = 4
                    st.rerun()
                else:
                    st.error(f"❌ 算式里好像少了符号 {p['op']} 或者数字不对哦。")

        # --- 第四步：工程施工 ---
        elif st.session_state['logic_step'] == 4:
            st.markdown(f"#### 🏗️ 第四步：工程施工")
            st.markdown(f"算式： **{p['equation']}**")
            st.write("最后，请计算出结果：")
            
            # 特殊处理时间题的显示
            if p.get('is_time_calc'):
                h_end = (p['base_time'] + p['add_min']) // 60
                m_end = (p['base_time'] + p['add_min']) % 60
                correct_val = f"{h_end}:{m_end:02d}"
                user_ans = st.text_input("请输入时间（格式如 9:30）：")
            else:
                correct_val = p['answer']
                user_ans = st.text_input("请输入数字答案：")
            
            if st.button("提交最终成果"):
                if str(user_ans).strip() == str(correct_val):
                    st.balloons()
                    st.success(f"🎉 恭喜！破案成功！答案就是 {correct_val}")
                    st.session_state['solved_count'] += 1
                    
                    st.markdown("---")
                    col_n1, col_n2 = st.columns(2)
                    with col_n1:
                        if st.button("➡️ 再来一案"):
                            st.session_state['problem'] = generate_logic_problem(st.session_state['current_level'])
                            st.session_state['logic_step'] = 1
                            st.rerun()
                    with col_n2:
                        if st.button("🏠 休息一下"):
                            st.session_state['mode'] = 'menu'
                            st.rerun()
                else:
                    st.error("⚠️ 算式是对的，但计算结果有点小误差，再算一次？")

if __name__ == "__main__":
    main()