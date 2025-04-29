import streamlit as st

if 'button' not in st.session_state:
    st.session_state.button = False

def click_button():
    st.session_state.button = not st.session_state.button

# 创建按钮
st.button('点击我', on_click=click_button)

if st.session_state.button:
    # 消息和嵌套小部件将保留在页面上
    st.write('按钮已打开！')
else:
    st.write('按钮已关闭！')