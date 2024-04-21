import streamlit as st
from sqlalchemy import create_engine, text
import sqlalchemy.exc

# 数据库配置
DATABASE_TYPE = 'mysql'
DBAPI = 'pymysql'
HOST = '111.231.19.111'  # 你的MySQL数据库主机IP
PORT = '3306'
DATABASE = 'result'
USERNAME = 'root'
PASSWORD = 'JK5DPc28ebYZEmhf'

# 创建数据库连接URL
DATABASE_URL = f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

def creat_table():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            x = """CREATE TABLE final (
                    student_id INT,
                    timeBegin DATETIME,
                    timeFinish DATETIME,
                    interests TEXT,
                    purpose TEXT,
                    selected_shops TEXT,
                    model_choice_acc TEXT,
                    model_choice_sup TEXT,
                    rating_A INT,
                    rating_B INT,
                    recommendations_1 TEXT,
                    recommendations_2 TEXT,
                    feedback TEXT
                );"""
            query = text(x)
            result = conn.execute(query)  # 执行新建
            if result:
                st.success("新建成功!")
            else:
                st.error("未能检索数据，连接失败。")
    except Exception as e:
        st.error(f"连接到数据库失败: {e}")

def add_column():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            alter_query = """
                ALTER TABLE final
                ADD COLUMN blind_seed INT
            """
            query = text(alter_query)
            result = conn.execute(query)  # 执行添加列的SQL命令
            if result:
                st.success("列添加成功!")
            else:
                st.error("未能检索数据，操作失败。")
    except sqlalchemy.exc.ProgrammingError as e:
        st.error("可能是列已经存在或其他原因导致添加失败。")
    except Exception as e:
        st.error(f"操作失败: {e}")



# 用 Streamlit 运行应用
if __name__ == "__main__":
    st.title('MySQL 数据库测试')
    add_column()
    st.write('检查上方的消息以确认是否成功连接到数据库。')