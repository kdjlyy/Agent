import pandas as pd
import numpy as np
import streamlit as st
import matplotlib
import matplotlib.pyplot as plt

# 假设我们有一些数据
data = pd.DataFrame({
    'first_column': list(range(1, 101)),
    'second_column': np.random.randn(100)
})

# 用户选择显示的数据数量
number = st.slider("请选择显示数据的数量", 1, 100, 50)
# 显示数据
st.write(data.head(number))


# 创建一个简单的图表
fig, ax = plt.subplots()
ax.hist(data['second_column'], bins=20)
st.pyplot(fig)