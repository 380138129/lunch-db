import streamlit as st
import mysql.connector  # MySQL 数据库连接
from datetime import datetime
import pandas as pd  # 用于展示表格

# MySQL 数据库连接配置
def get_db_connection():
    conn = mysql.connector.connect(
        host="39.100.182.215",  # MySQL 主机地址
        user="emlunch",       # MySQL 用户名
        password="rbGyVy2P2dHM",  # MySQL 密码
        database="lunch"  # 数据库名称
    )
    return conn

# 初始化数据库
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_name VARCHAR(255),
            report_date DATE,
            report_time TIME,
            is_eating ENUM('是', '否') DEFAULT '是',
            UNIQUE(employee_name, report_date)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# 初始化数据库
init_db()

# Streamlit 页面标题
st.title("食堂用餐上报系统")

# 侧边栏
st.sidebar.title("功能导航")
option = st.sidebar.radio("选择功能", ["上报用餐意愿", "查看上报情况", "查看历史记录"])

# 添加 JavaScript 代码，用于自动收起侧边栏
st.markdown(
    """
    <script>
    // 获取侧边栏的收起按钮
    const sidebarToggle = document.querySelector('.sidebar-collapse');
    // 模拟点击收起按钮
    sidebarToggle.click();
    </script>
    """,
    unsafe_allow_html=True
)

# 上报用餐意愿
if option == "上报用餐意愿":
    st.header("上报用餐意愿")
    employee_name = st.text_input("请输入您的姓名：")

    if st.button("提交"):
        current_time = datetime.now().strftime('%H:%M')
        current_date = datetime.now().strftime('%Y-%m-%d')

        if current_time > '17:30':
            st.error("已超过上报时间，请明天再报！")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO reports (employee_name, report_date, report_time)
                    VALUES (%s, %s, %s)
                ''', (employee_name, current_date, current_time))
                conn.commit()
                st.success("上报成功！")
            except mysql.connector.IntegrityError:
                st.error("您今天已经上报过了！")
            except Exception as e:
                st.error(f"发生错误：{e}")
            finally:
                cursor.close()
                conn.close()

# 查看上报情况
elif option == "查看上报情况":
    st.header("查看上报情况")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT employee_name, report_date, report_time, is_eating FROM reports WHERE report_date = %s
    ''', (datetime.now().strftime('%Y-%m-%d'),))
    reports = cursor.fetchall()
    cursor.close()
    conn.close()

    if reports:
        # 将数据转换为 DataFrame
        df = pd.DataFrame(reports, columns=["员工姓名", "上报日期", "上报时间", "是否用餐"])
        # 添加序号列
        df.insert(0, "序号", range(1, len(df) + 1))
        # 展示表格
        st.table(df)
    else:
        st.info("今天还没有上报记录。")

# 查看历史记录
elif option == "查看历史记录":
    st.header("查看历史记录")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT employee_name, report_date, report_time, is_eating FROM reports ORDER BY report_date DESC
    ''')
    reports = cursor.fetchall()
    cursor.close()
    conn.close()

    if reports:
        # 将数据转换为 DataFrame
        df = pd.DataFrame(reports, columns=["员工姓名", "上报日期", "上报时间", "是否用餐"])
        # 添加序号列
        df.insert(0, "序号", range(1, len(df) + 1))
        # 展示表格
        st.table(df)
    else:
        st.info("还没有历史上报记录。")