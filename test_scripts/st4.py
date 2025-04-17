import streamlit as st

# 创建横向布局列（左侧80%宽度给输入框，右侧20%给按钮）
col_input, col_btn = st.columns([0.9, 0.1])

with col_input:
    user_input = st.chat_input("输入消息...", key="user_input")

with col_btn:
    if st.button("发送", use_container_width=True):
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            # 触发消息处理逻辑...