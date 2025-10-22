import streamlit as st
import pandas as pd
import numpy as np

# 设置页面配置
st.set_page_config(page_title="加州房屋数据", layout="wide")

# 加载和缓存数据
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('housing.csv')
        return df
    except FileNotFoundError:
        st.error("❌ 错误：找不到 'housing.csv' 文件！")
        st.stop()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 加载数据时出错：{str(e)}")
        st.stop()
        return pd.DataFrame()

def main():
    # 加载数据
    df = load_data()
    
    if df.empty:
        st.error("无法加载数据，应用停止运行。")
        return
    
    # 主标题 - 替换为您自己的名字
    st.title("加州房屋数据 (1990) - 王启润")
    
    # 价格滑块
    st.subheader("最低房屋中位数价格")
    min_price, max_price = int(df['median_house_value'].min()), int(df['median_house_value'].max())
    price_range = st.slider(
        "选择价格范围",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        label_visibility="collapsed"
    )
    
    st.write("在侧边栏查看更多筛选条件:")
    
    # 侧边栏筛选器
    st.sidebar.header("筛选条件")
    
    # 位置类型多选
    st.sidebar.subheader("位置类型")
    location_types = st.sidebar.multiselect(
        "选择位置类型",
        options=df['ocean_proximity'].unique(),
        default=df['ocean_proximity'].unique()
    )
    
    # 收入水平单选按钮
    st.sidebar.subheader("收入水平")
    income_level = st.sidebar.radio(
        "选择收入水平",
        options=["全部", "低 (≤2.5)", "中 (>2.5 & <4.5)", "高 (≥4.5)"]
    )
    
    # 应用筛选条件
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['median_house_value'] >= price_range[0]) & 
        (filtered_df['median_house_value'] <= price_range[1])
    ]
    
    if location_types:
        filtered_df = filtered_df[filtered_df['ocean_proximity'].isin(location_types)]
    
    if income_level == "低 (≤2.5)":
        filtered_df = filtered_df[filtered_df['median_income'] <= 2.5]
    elif income_level == "中 (>2.5 & <4.5)":
        filtered_df = filtered_df[(filtered_df['median_income'] > 2.5) & (filtered_df['median_income'] < 4.5)]
    elif income_level == "高 (≥4.5)":
        filtered_df = filtered_df[filtered_df['median_income'] >= 4.5]
    
    st.sidebar.write(f"筛选后数据点数: {len(filtered_df)}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("房屋位置分布")
        if not filtered_df.empty:
            st.map(filtered_df[['latitude', 'longitude']])
        else:
            st.warning("没有数据符合筛选条件")
    
    with col2:
        st.subheader("数据概览")
        if not filtered_df.empty:
            st.metric("总记录数", len(filtered_df))
            st.metric("平均价格", f"${filtered_df['median_house_value'].mean():,.0f}")
            st.metric("平均收入", f"{filtered_df['median_income'].mean():.2f}")
    
    # 使用Streamlit原生图表替代matplotlib直方图
    st.subheader("房屋中位数价值分布")
    if not filtered_df.empty:
        # 方法1：使用st.bar_chart显示分布
        value_counts = filtered_df['median_house_value'].value_counts().sort_index()
        st.bar_chart(value_counts.head(30))
        
        # 方法2：显示数据统计
        with st.expander("查看详细统计"):
            st.write(f"价格范围: ${filtered_df['median_house_value'].min():,} - ${filtered_df['median_house_value'].max():,}")
            st.write(f"中位数价格: ${filtered_df['median_house_value'].median():,}")
    else:
        st.warning("没有数据可用于生成直方图")
    
    with st.expander("查看筛选后的数据"):
        if not filtered_df.empty:
            st.dataframe(filtered_df.head(100))
        else:
            st.info("没有数据可显示")

if __name__ == "__main__":
    main()

