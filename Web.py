from queue import Full
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
from data_pre import Category,new_data as data
from datetime import datetime, timedelta
import plotly.express as px 
from sqlalchemy import create_engine, text
import pymysql

# 数据库配置
DATABASE_TYPE = 'mysql'
DBAPI = 'pymysql'
HOST = '111.231.19.111'  
PORT = '3306'
DATABASE = 'result'
USERNAME = 'root'
PASSWORD = 'JK5DPc28ebYZEmhf'

# 创建数据库连接URL
DATABASE_URL = f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# 启用 wide mode
st.set_page_config(layout="wide")

custom_css = """
<style>
@font-face {
    font-family: 'MyLocalFont';
    src: url('SimHei.ttf') format('truetype');
}
body, html {
    font-family: 'MyLocalFont';
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
    #st.session_state.page = 'rec_page'
   

floor_images = {
    1: '1f.png',
    2: '2f.png',
    3: '3f.png',
    4: '4f.png'
}

####################################################
def click_welcome():
    if st.session_state.student_id != "":
        st.session_state.page = 'shopping_page'            
        


def render_welcome_sidebar():
    with st.sidebar:
        st.markdown("# 请在下方填写对应信息并提交：😊")
        st.session_state.student_id = ""
        st.session_state.student_id = st.text_input("学号:",placeholder="2023214419")
        st.session_state.purpose = st.selectbox("你可以预想一下你逛商场的目的:", ["购物", "吃饭", "休闲娱乐","随便逛逛"],placeholder=" ")
        submit = st.button("提交",on_click= click_welcome())
        if submit:
            if st.session_state.student_id == "":
                st.sidebar.error("请填写完整信息！")
            
def render_welcome_main():
    col1, col2, col3 = st.columns([1,8,1]) # 调整比例以达到视觉上的居中
    with col2: # 使用中间的列来显示图片
        image = Image.open("title.jpg")
        st.image(image, width=1000) # 动态调整图片宽度以适应列宽
        
    st.title("欢迎来到我们的商场推荐系统实验项目！💕")
    st.markdown("## 请在侧边栏填写对应信息并提交，并仔细阅读下方的注意事项，我们将为您推荐最适合您的商场体验！")
    st.markdown("### 注意事项：")
    st.markdown("1. 请仔细填写信息，请勿随便填写。")
    st.markdown("2. 请模拟您的真实逛店想法，以帮助我们实现更好的推荐效果。")
    st.markdown("3. 请在提交前仔细核对您的信息，提交后将无法更改。")
def render_welcome_page():
    render_welcome_sidebar()
    render_welcome_main()
            

##############################################   

def render_floor_sidebar():
    st.session_state.selected_category = st.sidebar.selectbox('可以选择对应品类查询所在楼层：',options=data['CategoryName'].unique())
    filtered_data = data[data['CategoryName'] == st.session_state.selected_category]
    category_count = filtered_data['floor'].value_counts().sort_index()

    fig = px.pie(values=category_count.values, 
                names=category_count.index.map(str), 
                title=f"{st.session_state.selected_category}各楼层分布")

    # 显示图表
    fig.update_layout(width=400, height=300)
    fig.update_traces(textinfo='label+value', textfont_size=14)
    st.sidebar.plotly_chart(fig)
    st.sidebar.markdown("---")

def gettime():
    t = datetime.now()
    return t

def sidebarclick():
    time_end = gettime()
    time_to_compare = timedelta(seconds=2)#改时间
    delta = time_end - st.session_state.time_s
    if delta > time_to_compare:
        st.session_state.selected_shops.append(st.session_state.selected_store)
        st.session_state.sidebar_input = str(int(st.session_state.sidebar_input)+1)
    else : st.sidebar.error('时间间隔过短，请稍2s后再试')
        

def render_floor_sidebar2(): 
    st.session_state.selected_store = ''
    if "sidebar_input" not in st.session_state:
        st.session_state.sidebar_input = "1"
        st.session_state.selected_shops = []
        st.session_state.selected_store = ''
    if st.session_state.sidebar_input == "1":
        st.session_state.time_s = gettime()
        st.sidebar.markdown("👇请到对应楼层选择你想要的要逛的店铺：")
        st.session_state.shop_list= data['StoreName'].unique().tolist()
        st.session_state.selected_store=st.sidebar.selectbox(f"选择您第一个逛的商铺：",st.session_state.shop_list,key="select1")
        st.sidebar.markdown("😊请确定您选择店铺在地图中的位置再点击确定")
        st.sidebar.button("选第二个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "2":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)
        st.sidebar.markdown(selected_info)
        st.sidebar.markdown("👇请继续探索第二个您想逛的店铺：")
        st.session_state.shop_list= data['StoreName'].unique().tolist()
        st.session_state.selected_store=st.sidebar.selectbox(f"选择您第二个逛的商铺：",st.session_state.shop_list,key="select2")
        st.sidebar.markdown("😊请确定您选择店铺在地图中的位置再点击确定")
        st.sidebar.button("选第三个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "3":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)
        st.sidebar.markdown(selected_info)
        st.sidebar.markdown("👇请继续探索第三个您想逛的店铺：")
        st.session_state.shop_list= data['StoreName'].unique().tolist()
        st.session_state.selected_store=st.sidebar.selectbox(f"选择您第三个逛的商铺：",st.session_state.shop_list,key="select3")
        st.sidebar.markdown("😊请确定您选择店铺在地图中的位置再点击确定")
        st.sidebar.button('我选好了，开始推荐！',on_click= go_to_page_rec)
        st.sidebar.button("选第四个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "4":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)   
        st.sidebar.markdown(selected_info)
        st.sidebar.markdown("👇请继续探索第四个您想逛的店铺：")
        st.session_state.shop_list= data['StoreName'].unique().tolist()
        st.session_state.selected_store=st.sidebar.selectbox(f"请选择您第四个逛的商铺：",st.session_state.shop_list,key="select4")
        st.sidebar.markdown("😊请确定您选择店铺在地图中的位置再点击确定")
        st.sidebar.button('我选好了，开始推荐！',on_click= go_to_page_rec)
        st.sidebar.button("选第五个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "5":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)   
        st.sidebar.markdown(selected_info)
        st.sidebar.markdown("👇请继续探索第五个您想逛的店铺：")
        st.session_state.shop_list= data['StoreName'].unique().tolist()
        st.session_state.selected_store=st.sidebar.selectbox(f"请选择您第五个逛的商铺：",st.session_state.shop_list,key="select5")
        st.sidebar.markdown("😊请确定您选择店铺在地图中的位置再点击确定")
        st.sidebar.button('我选好了，开始推荐！！',on_click= go_to_page_rec)     


def go_to_page_rec():
    st.session_state.selected_shops.append(st.session_state.selected_store)
    st.session_state.page = 'rec_page'

        
def render_floor_page():
    st.title(f"请沉浸浏览该商场交互平面图，选择你感兴趣的浏览路径!")
    st.write(f"👍点击查看具体的店铺信息~")
    st.write(f"🙌使用滚轮可以放大缩小地体~")
    # 要嵌入的网址
    src_url = "http://111.231.19.111:8080/"
    # 要显示的部分的尺寸和位置
    position = {"top": -112, "left": 0, "width": 1600, "height": 700}

    # 使用streamlit的html组件嵌入iframe
    st.components.v1.html(f'''
        <div style="border: none; overflow: hidden; width: {position["width"]+30}px; height: {position["height"]+30}px;">
            <iframe
                src="{src_url}"
                width="{position["width"] + abs(position["left"])}px"
                height="{position["height"] + abs(position["top"])}px"
                frameborder="0"
                style="transform:translate({position["left"]}px, {position["top"]}px);"
                >
            </iframe>
        </div>
        ''', height=position["height"]-10, width=position["width"]-10)
    
def render_shopping_page():
     
    st.sidebar.title(f"欢迎学号为{st.session_state.student_id}的同学，来到我们的商场！")
    render_floor_sidebar()
    render_floor_sidebar2()
    render_floor_page()


##############################################
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False


def button_clicked():
    st.session_state.button_clicked = True


def render_rec_sidebar():       
    with st.sidebar:
        st.title("问卷调查")
        model_choice_acc = st.selectbox("哪个模型的推荐列表更加匹配你此刻的逛店意图和需求？", ["模型A", "模型B"])
        model_choice_sup = st.selectbox("哪个模型的推荐列表让你感觉更加出乎意料？", ["模型A", "模型B"])
        rating_A = st.slider("给模型A给个主观评分，你会打几分?", 1, 5)
        rating_B = st.slider("给模型B给个主观评分，你会打几分?", 1, 5)
        recommendations_1 = []
        recommendations_2 = []
        recommendations_1 = st.selectbox(
            "根据A模型要你选择下一个逛的店铺，你会选择：",
            ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","无"]
        )
        recommendations_2 = st.selectbox(
            "根据B模型要你选择下一个逛的店铺，你会选择：",
            ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","无"]
        )
        feedback = st.text_area("请填写其他的建议或者评价(选填)：")

        if not st.session_state.button_clicked:
            button = st.button("完成")
            if button:
                if recommendations_1 == [] or recommendations_2 == []:
                    st.sidebar.error("未完成必填项目！")
                else:
                #链接数据库并导入
                    st.session_state.timeFinish = gettime()
                    try:
                        engine = create_engine(DATABASE_URL)
                        with engine.connect() as conn:
                            x = f"""INSERT INTO final (student_id, timeBegin, timeFinish, interests, purpose, selected_shops, model_choice_acc, model_choice_sup, rating_A, rating_B, recommendations_1, recommendations_2, feedback)
                                VALUES (
                                    {st.session_state.student_id},
                                    '{st.session_state.timeBegin}',
                                    '{st.session_state.timeFinish}',
                                    '{', '.join(st.session_state.interests)}',
                                    '{st.session_state.purpose}',
                                    '{', '.join(st.session_state.selected_shops)}',
                                    '{model_choice_acc}',
                                    '{model_choice_sup}',
                                    {rating_A},
                                    {rating_B},
                                    '{recommendations_1}',
                                    '{recommendations_2}',
                                    '{feedback}'
                                );"""
                            query = text(x)
                            result = conn.execute(query)  # 执行新建
                            if result:
                                st.sidebar.success("数据库记录成功!")
                            else:
                                st.sidebar.error("未能检索数据，连接失败。")
                    except Exception as e:
                        st.sidebar.error(f"连接到数据库失败: {e}")
                        st.sidebar.error(f"连接到数据库失败: {e}")
                    button_clicked()
                            
        else:
             st.sidebar.success("恭喜你完成本次实验！")     
            


def render_result_page():
    st.markdown(f"## 学号为{st.session_state.student_id}的同学，您留下的逛店信息如下：")# {st.session_state.student_id}
    st.markdown(f"__逛店目标__：{st.session_state.purpose}")# {st.session_state.purpose}
    st.markdown(f"__感兴趣的类目__：{st.session_state.selected_category}")# {st.session_state.selected_category}
    st.markdown("__逛店轨迹__："+"-> ".join(st.session_state.selected_shops))# +"-> ".join(st.session_state.selected_shops)
    st.markdown("---")
    st.markdown("## 模型推荐对比")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 模型A的推荐结果")
        st.markdown("")
        st.markdown("__1.推荐店铺1__")
        st.markdown("__楼层__：1楼 __区域__：zoom1")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__2.推荐店铺2__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__3.推荐店铺3__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__4.推荐店铺4__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__4.推荐店铺5__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
    with col2:
        st.markdown("### 模型B的推荐结果")
        st.markdown("")
        st.markdown("__1.推荐店铺1__")
        st.markdown("__楼层__：1楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__2.推荐店铺2__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__3.推荐店铺3__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__4.推荐店铺4__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")
        st.markdown("__4.推荐店铺5__")
        st.markdown("__楼层__：2楼 __区域__：zoom3")
        st.markdown("__品类信息__：服装服饰🧥")
        st.markdown("")


def render_rec_page():
    render_rec_sidebar()
    render_result_page()


###########
#定义全局框架
    # 初始化或获取session_state中的页面状态

if st.session_state.page == 'welcome':
    st.session_state.timeBegin = gettime()
    render_welcome_page()
elif st.session_state.page == 'shopping_page':
    render_shopping_page()       
elif st.session_state.page == 'rec_page':
    render_rec_page() 

