import streamlit as st

# 文本输入
user_input = st.text_input("请输入您的名字", "John Doe")

# 滑动条
age = st.slider("请选择您的年龄", 18, 100, 30)

# 选择框
job = st.selectbox("请选择您的职业", ["学生", "教师", "工程师", "其他"])

st.write(f"Hello, {user_input}!")
st.write(f"您的年龄是 {age}，职业是 {job}。")