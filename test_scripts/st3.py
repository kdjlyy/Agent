import streamlit as st

# Streamlit提供了灵活的布局选项，使您可以设计出符合需求的界面布局。
# 利用列(column)和展开器(expander)等组件，您可以创建出复杂而有组织的布局。
# 使用列进行布局
col1, col2, col3 = st.columns(3)
with col1:
    st.header("Column 1")
    st.write("这是第一列的内容")
with col2:
    st.header("Column 2")
    st.write("这是第二列的内容")
with col3:
    st.header("Column 3")
    st.write("这是第三列的内容")

# 使用展开器创建隐藏内容
with st.expander("点击展开更多信息"):
    st.write("这里是一些可以展开的详细信息。")

# 为了在应用中管理复杂的用户交互，Streamlit引入了会话状态(session state)的概念。
# 会话状态允许您在用户与应用交互时保持某些信息的状态，这对于创建复杂的交互逻辑至关重要。
# 增加一个计数器
if 'count' not in st.session_state:
    st.session_state.count = 0

increment = st.button("增加")
if increment:
    st.session_state.count += 1

st.write(f"计数器值：{st.session_state.count}")
