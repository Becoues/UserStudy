from queue import Full
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
from data_pre import SiteID,new_data as data
from datetime import datetime
import plotly.express as px 
from sqlalchemy import create_engine, text
import pymysql
from scoreforfeedback import score_for_feedback 

import json
from sqlalchemy.exc import SQLAlchemyError
import m 
import trans
import torch
import random
import time

# 启用 wide mode
st.set_page_config(layout="wide")
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
    st.session_state.page = ""
    st.session_state.page = 'welcome'
    #st.session_state.page = 'rec_page'

   

floor_images = {
    1: '1f.png',
    2: '2f.png',
    3: '3f.png',
    4: '4f.png'
}

####################################################
Category = [
    '女装',
    '男装',
    '男女集合',
    '运动休闲',
    '餐饮美食',
    '快餐饮品',
    '配饰珠宝',
    '鞋品箱包',
    '杂品集合',
    '美妆护肤',
    '数码电子',
    '家居家用',
    '亲子',
    '体验业态'
]


category_mapping = {
    "买衣服": 0,  
    "买配饰化妆品": 6, 
    "买数码产品": 10,  
    "买居家产品": 11, 
    "吃饭聚餐": 5,  
    "遛娃": 12,  
}
def botton_c ():
    # if st.session_state.student_id == "" or st.session_state.nickname == "" or st.session_state.purpose== "":
    #     st.session_state.page = 'welcome'
    # else: st.session_state.page = 'shopping_page' 
    if st.session_state.student_id == "" or st.session_state.nickname == "" or not st.session_state.purpose or st.session_state.gender == None or st.session_state.age == None or st.session_state.grade == None:
        st.sidebar.error("请填写完整信息")
    else : 
        st.session_state.timeBegin_2 = gettime()
        st.session_state.page = 'shopping_page' 



def render_welcome_sidebar():
    with st.sidebar:
        st.markdown("## 请在下方填写对应信息并提交：😊")
        st.session_state.student_id = ""
        st.session_state.nickname = ""
        st.session_state.purpose = [0]
        st.session_state.gender = ""
        st.session_state.age = ""
        st.session_state.grade = ""
        default_option_index = None
        st.session_state.student_id = st.text_input("学号:",placeholder="请输入您的学号")
        st.session_state.nickname = st.text_input("昵称:",placeholder="我们可以怎么称呼您呢")
        st.session_state.gender = st.selectbox("性别:",["男","女"],default_option_index)
        st.session_state.age = st.selectbox("年龄:",["17岁及以下","18~22岁","23~25岁","26~30岁","31岁及以上"],default_option_index)
        st.session_state.grade = st.selectbox("年级:",["大一","大二","大三","大四","硕士生","博士生","其他"],default_option_index) 
        categories =list(category_mapping.keys())
        st.session_state.purpose = st.sidebar.multiselect("你可以预想一下你逛商场的目的:", categories)      

def rebder_welcom_botton():
        st.session_state.submit = False
        submit = st.sidebar.button("提交",on_click= botton_c)
        
def render_welcome_main():
    st.markdown("## 欢迎来到我们的商场推荐系统实验项目！💕")
    #col1, col2, col3 = st.columns([1,8,1]) # 调整比例以达到视觉上的居中
    #with col2: # 使用中间的列来显示图片
    image = Image.open("title.jpg")
    st.image(image, width=1000) # 动态调整图片宽度以适应列宽
    st.write("""<span style="font-size:28px;font-weight:bold;">请尽量模拟您的真实逛店想法，输入您的初始逛店序列，以便为您推荐最佳逛店体验。</span>""", unsafe_allow_html=True)
    #st.write("""<span style="font-size:28px;font-weight:bold;padding-left:60px;">     输入您的初始逛店序列，</span>""", unsafe_allow_html=True)
    #st.write("""<span style="font-size:28px;font-weight:bold;padding-left:120px;">     以便为您推荐最佳逛店体验。</span>""", unsafe_allow_html=True)
def render_welcome_page():
    render_welcome_sidebar()
    rebder_welcom_botton()
    render_welcome_main()
            

##############################################   
def display_cat_by_floor(query_dict, max_num=3):
    # lines = []
    # for floor, arr in query_dict.items():
    #     tmp = (f'{floor}楼（{len(arr)}家）'.center(25, '='))
    #     lines.append(f'__{tmp}__')
    #     if len(arr) > max_num:
    #         lines.append('、'.join(arr[:max_num]) + '……')
    #     else:
    #         lines.append('、'.join(arr))
    # return '  \n'.join(lines)
    category_emoji_dict = {
    "配饰珠宝": "💍",  # 表示配饰及珠宝
    "运动休闲": "🏃‍♂️",  # 表示与运动和休闲相关的
    "杂品集合": "🧺",  # 表示各类杂项商品集合
    "男装": "👔",  # 表示男性服装
    "男女集合": "🕶",  # 表示潮流和时尚类目
    "家居家用": "🏡",  # 表示家居及家用商品
    "女装": "👗",  # 表示女性服装
    "快餐饮品": "🍔",  # 表示休闲快餐和饮品
    "数码电子": "📱",  # 表示数码产品和电子设备
    "美妆护肤": "💄",  # 表示美妆和护肤产品
    "鞋品箱包": "👜",  # 表示鞋类和箱包
    "亲子": "👨‍👩‍👦",  # 表示亲子相关的商品或活动
    "体验业态": "🎨",  # 表示体验和活动，如艺术、手工等
    "餐饮美食": "🍽️",  # 表示食物或餐饮
}
    emoji = category_emoji_dict.get(st.session_state.selected_category)
    for floor, arr in query_dict.items():
        #title = f'{floor}楼({len(arr)}家)'
        st.sidebar.write(
            "<div style='border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; "
            f"text-align:center;'><b>{floor}楼</b>({len(arr)}家)</div>",
            unsafe_allow_html=True)
        for idx, store in enumerate(arr):
            if idx >= max_num:
                st.sidebar.write(f"""
                <div style="line-height: 1.4;padding-left:65px;">
                    ...
                </div>
                """, unsafe_allow_html=True)
                break
            st.sidebar.write(f"""
        <div style="line-height: 1.4;padding-left:40px;font-size:14px;">
            {emoji}&nbsp{store}
        </div>
        """, unsafe_allow_html=True)
    st.write("<div style='border-top: 1px solid #ddd;'></div>", unsafe_allow_html=True)


def render_floor_sidebar():
    try:
        st.session_state.cat = category_mapping[st.session_state.purpose[-1]]
    except:
        st.session_state.cat = 0
    st.session_state.selected_category = st.sidebar.selectbox('根据品类查询楼层和top3店铺分布:',options=Category,index=st.session_state.cat,key="select0")
    with open('cat_pop.json', 'r', encoding='utf-8') as f:
        cat_pop = json.load(f)
    display_cat_by_floor(cat_pop[st.session_state.selected_category])
    # filtered_data = data[data['new_category'] == st.session_state.selected_category]
    # category_count = filtered_data['floor'].value_counts().sort_index()

    #饼图展示
    # fig = px.pie(values=category_count.values, 
    #             names=category_count.index.map(str), 
    #             color_discrete_sequence=["#f58231", "#d495e0", "#ffd8b1", '#8475c5'],
    #             title=f"{st.session_state.selected_category}各楼层分布")
    # fig.update_layout(margin=dict(t=40, b=0))
    
    # 显示图表
    # fig.update_layout(width=400, height=200)
    # fig.update_traces(textinfo='label+value', textfont_size=14)
    # st.sidebar.plotly_chart(fig)
    # 设置自定义样式
    custom_style = """
    <style>
    .divider {
        margin-top: 1px;
        margin-bottom: 5px;
    }
    </style>
    """
    # 使用 st.markdown() 和自定义样式来绘制分割线
    st.markdown(custom_style, unsafe_allow_html=True)
    st.sidebar.markdown('<hr class="divider">', unsafe_allow_html=True)

def gettime():
    t = datetime.now()
    return t

def sidebarclick():
    #时间检测
    # time_end = gettime()
    # time_to_compare = timedelta(seconds=2)#改时间
    # delta = time_end - st.session_state.time_s
    # if delta > time_to_compare:
    #     st.session_state.selected_shops.append(st.session_state.selected_store)
    #     st.session_state.sidebar_input = str(int(st.session_state.sidebar_input)+1)
    # else : st.sidebar.error('时间间隔过短，请稍2s后再试')

    #位置检测
    if st.session_state.selected_store == None or st.session_state.selected_store == '' or st.session_state.site== None or st.session_state.site=='':
        st.session_state.erro2 = True
    else:
        if st.session_state.site == st.session_state.ture_site:
            st.session_state.position = data.loc[data['StoreName'] == st.session_state.selected_store,'idx_x'].squeeze()
            st.session_state.selected_shops.append(st.session_state.selected_store)
            st.session_state.shop_list.remove(st.session_state.selected_store)
            st.session_state.timechoice.append(str(gettime())) 
            st.session_state.erro = False
            st.session_state.erro2 = False
            st.session_state.sidebar_input = str(int(st.session_state.sidebar_input)+1)
        else : st.session_state.erro = True
            



def render_floor_sidebar2(): 
    default_option_index = None
    st.session_state.selected_store = ''
    if "sidebar_input" not in st.session_state:
        st.session_state.erro = False
        st.session_state.erro2 = False
        st.session_state.timechoice = []
        st.session_state.sidebar_input = "1"
        st.session_state.selected_shops = []
        st.session_state.shop_list = []
        st.session_state.site = ''
        st.session_state.ture_site = ''
        st.session_state.position = None
        st.session_state.len =False
    if st.session_state.sidebar_input == "1":
        st.session_state.time_s = gettime()
        st.sidebar.markdown("请点击右侧平面图跳转至对应楼层进行浏览：")
        st.session_state.shop_list= sorted(data['StoreName'].unique().tolist())
        st.session_state.selected_store=st.sidebar.selectbox("选择您第一个逛的商铺：",st.session_state.shop_list,default_option_index,key="select1")
        #st.sidebar.markdown(f"位置：{data.loc[data['StoreName'] == st.session_state.selected_store, 'floor'].squeeze()}{ data.loc[data['StoreName'] == st.session_state.selected_store, 'zoom'].squeeze()}")
        if st.session_state.selected_store == None or st.session_state.selected_store == '':
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check1")
        else:
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check1")
        st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
        if st.session_state.erro:
            st.sidebar.error('位置与店铺不匹配，请重新填写')
            st.session_state.erro = False
        if st.session_state.erro2:
            st.sidebar.error('请填写完整信息')
            st.session_state.erro2 = False
        st.sidebar.button("选第二个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "2":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + " &rarr;  ".join(st.session_state.selected_shops)
        st.sidebar.markdown(selected_info)
        st.session_state.selected_store=st.sidebar.selectbox(f"选择您第二个逛的商铺：",st.session_state.shop_list,default_option_index,key="select2")
        if st.session_state.selected_store == None or st.session_state.selected_store == '':
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check2")
        else:
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check2")
        #st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check2")
        st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
        if st.session_state.erro:
            st.sidebar.error('位置与店铺不匹配，请重新填写')
            st.session_state.erro = False
        if st.session_state.erro2:
            st.sidebar.error('请填写完整信息')
            st.session_state.erro2 = False
        if st.session_state.len:
            st.sidebar.error('至少要逛两个店铺')
            st.session_state.len = False
        with st.sidebar:
            col1, col2 = st.sidebar.columns(2) 
            with col1:
                 st.button("选第三个", on_click=sidebarclick)
            with col2:
                 st.button('开始推荐',on_click= go_to_page_rec)
    if st.session_state.sidebar_input == "3":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + " &rarr;  ".join(st.session_state.selected_shops)
        st.sidebar.markdown(selected_info)
        st.session_state.selected_store=st.sidebar.selectbox(f"选择您第三个逛的商铺：",st.session_state.shop_list,default_option_index,key="select3")
        if st.session_state.selected_store == None or st.session_state.selected_store == '':
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check3")
        else:
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check3")
        #st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check3")
        st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
        if st.session_state.erro:
            st.sidebar.error('位置与店铺不匹配，请重新填写')
            st.session_state.erro = False
        if st.session_state.erro2:
            st.sidebar.error('请填写完整信息')
            st.session_state.erro2 = False
        with st.sidebar:
            col1, col2 = st.sidebar.columns(2) 
            with col1:
                 st.button("选第四个", on_click=sidebarclick)
            with col2:
                 st.button('开始推荐',on_click= go_to_page_rec)
    if st.session_state.sidebar_input == "4":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + " &rarr;  ".join(st.session_state.selected_shops)   
        st.sidebar.markdown(selected_info)
        st.session_state.selected_store=st.sidebar.selectbox(f"请选择您第四个逛的商铺：",st.session_state.shop_list,default_option_index,key="select4")
        if st.session_state.selected_store == None or st.session_state.selected_store == '':
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check4")
        else:
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check4")
        #st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check4")
        st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
        if st.session_state.erro:
            st.sidebar.error('位置与店铺不匹配，请重新填写')
            st.session_state.erro = False
        if st.session_state.erro2:
            st.sidebar.error('请填写完整信息')
            st.session_state.erro2 = False
        st.sidebar.button('开始推荐',on_click= go_to_page_rec)
    # if st.session_state.sidebar_input == "5":
    #     selected_info = "👌您选择的商铺是：" + " &rarr;  ".join(st.session_state.selected_shops)   
    #     st.sidebar.markdown(selected_info)
    #     st.sidebar.button('开始推荐！',on_click= go_to_page_rec)

        #st.sidebar.button("选第五个", on_click=sidebarclick)
    # if st.session_state.sidebar_input == "5":
    #     st.session_state.time_s = gettime()
    #     selected_info = "👌您选择的商铺是：" + " &rarr;  ".join(st.session_state.selected_shops)   
    #     st.sidebar.markdown(selected_info)
    #     st.session_state.selected_store=st.sidebar.selectbox(f"请选择您第五个逛的商铺：",st.session_state.shop_list,default_option_index,key="select5")
    #     if st.session_state.selected_store == None or st.session_state.selected_store == '':
    #         st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
    #     else:
    #         st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
    #     #st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
    #     st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
    #     if st.session_state.erro:
    #         st.sidebar.error('位置与店铺不匹配，请重新填写')
    #         st.session_state.erro = False
    #     if st.session_state.erro2:
    #         st.sidebar.error('请填写完整信息')
    #         st.session_state.erro2 = False
    #     st.sidebar.button('我选好了，开始推荐！！',on_click= go_to_page_rec)     


def go_to_page_rec():
    if  int(st.session_state.sidebar_input) == 2 and st.session_state.selected_store == None and st.session_state.site== None:
        st.session_state.len =True
    else:
        if st.session_state.selected_store == None or st.session_state.selected_store == '' or st.session_state.site== None or st.session_state.site=='':
            st.session_state.erro2 = True
        else:
            if st.session_state.site == st.session_state.ture_site:
                st.session_state.position = data.loc[data['StoreName'] == st.session_state.selected_store,'idx_x'].squeeze()
                st.session_state.selected_shops.append(st.session_state.selected_store)
                st.session_state.timeBegin_3 = gettime()
                st.session_state.top = True
                st.session_state.page = 'rec_page'
            else : st.session_state.erro = True
    if int(st.session_state.sidebar_input) > 2 and st.session_state.selected_store == None and st.session_state.site== None:
        st.session_state.timeBegin_3 = gettime()
        st.session_state.top = True
        st.session_state.page = 'rec_page'
    



        
def render_floor_page():
    st.markdown("## 请沉浸浏览该商场交互平面图，输入感兴趣的逛店序列")
    st.write(f"👍点击查看具体的店铺信息~")
    st.write(f"🙌使用滚轮可以放大缩小平面图~")
    # 要嵌入的网址
    if st.session_state.position == None:
        src_url = "https://storerecommend.cn:8080"
    else:
        src_url = f"https://storerecommend.cn:8080/?storeIdx={st.session_state.position}"
    #src_url = "http://localhost:8080"
    # 要显示的部分的尺寸和位置
    position = {"top": -112, "left": 0, "width": 1600, "height": 800}

    # 使用streamlit的html组件嵌入iframe
    # st.components.v1.html(f'''
    #     <div style="border: none; overflow: hidden; width: {position["width"]+30}px; height: {position["height"]+30}px;">
    #         <iframe
    #             src="{src_url}"
    #             width="{position["width"] + abs(position["left"])}px"
    #             height="{position["height"] + abs(position["top"])}px"
    #             frameborder="0"
    #             style="transform:translate({position["left"]}px, {position["top"]}px);"
    #             >
    #         </iframe>
    #     </div>
    #     ''', height=position["height"]-10, width=position["width"]-10)
    st.components.v1.html(f'''
        <div style="position: relative; overflow: hidden; width: 100%; aspect-ratio: {position["width"]/position["height"]};">
            <iframe
                src="{src_url}"
                width="100%"
                height="100%"
                frameborder="0"
                style="transform:translate({position["left"]}px, {position["top"]}px);"
                >
            </iframe>
        </div>
        ''', height=position["height"], width=position["width"])
    
def render_shopping_page():
     
    st.sidebar.title(f"欢迎{st.session_state.nickname}同学，来到我们的商场！")
    random.seed(int(time.time()))
    st.session_state.random = 0
    st.session_state.random = random.randint(1, 2)
    render_floor_sidebar()
    render_floor_sidebar2()
    render_floor_page()


##############################################
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
    st.session_state.sqlerro = False 


def button_clicked():
    if st.session_state.intrestmatch == "" or \
       st.session_state.pathconvenience == "" or \
       st.session_state.timelimit == "" or \
       st.session_state.pathvariety == "" or \
       st.session_state.feedback1 == "" or \
        st.session_state.feedback2 == "" or \
        st.session_state.feedback3 == "" or \
        st.session_state.feedback4 == "" or \
        st.session_state.feedback5 == "" or \
       st.session_state.boredom == "":
         st.session_state.sqlerro = True
    else:
        #补丁
        adjusted_selected_shops = []
        for name in st.session_state.selected_shops:
            # 如果店铺名称包含单引号，则进行替换处理
            if "'" in name:
                # 将单引号替换为两个单引号
                adjusted_name = name.replace("'", "''")
                # 添加调整后的店铺名称到新列表中
                adjusted_selected_shops .append(adjusted_name)
            else:
                # 如果店铺名称不包含单引号，则直接添加到新列表中
                adjusted_selected_shops .append(name)
        adjusted_output_a = []
        for name in st.session_state.output_a:
            # 如果店铺名称包含单引号，则进行替换处理
            if "'" in name:
                # 将单引号替换为两个单引号
                adjusted_name = name.replace("'", "''")
                # 添加调整后的店铺名称到新列表中
                adjusted_output_a.append(adjusted_name)
            else:
                # 如果店铺名称不包含单引号，则直接添加到新列表中
                adjusted_output_a.append(name)
        adjusted_output_b = []
        for name in st.session_state.output_b:
            # 如果店铺名称包含单引号，则进行替换处理
            if "'" in name:
                # 将单引号替换为两个单引号
                adjusted_name = name.replace("'", "''")
                # 添加调整后的店铺名称到新列表中
                adjusted_output_b.append(adjusted_name)
            else:
                # 如果店铺名称不包含单引号，则直接添加到新列表中
                adjusted_output_b.append(name)
        if "'" in st.session_state.feedback1:
            adjusted_fd1 = st.session_state.feedback1.replace("'", "''")
        if "'" in st.session_state.feedback2:
            adjusted_fd2 = st.session_state.feedback2.replace("'", "''")
        if "'" in st.session_state.feedback3:
            adjusted_fd3 = st.session_state.feedback3.replace("'", "''")
        if "'" in st.session_state.feedback4:
            adjusted_fd4 = st.session_state.feedback4.replace("'", "''")
        if "'" in st.session_state.feedback5:
            adjusted_fd5 = st.session_state.feedback5.replace("'", "''")
        #链接数据库并导入
        st.session_state.sqlerro = False
        st.session_state.timeFinish = gettime()
        try:
                    # 创建数据库引擎
                    engine = create_engine(DATABASE_URL)
                    # 执行SQL插入操作
                    with engine.connect() as conn:
                        x = f"""INSERT INTO casestudy (
                                        student_id,
                                        selected_category,
                                        purpose,
                                        selected_shops,
                                        output_a,
                                        output_b,
                                        timechoice,
                                        intrestmatch,
                                        feedback1,
                                        pathconvenience,
                                        feedback2,
                                        timelimit,
                                        feedback3,
                                        pathvariety,
                                        feedback4,
                                        boredom,
                                        feedback5,
                                        rating_A,
                                        rating_B,
                                        random,
                                        timeBegin,
                                        timeFinish,
                                        timeBegin_2,
                                        timeBegin_3,
                                        likelihood,
                                        gender,
                                        age,
                                        grade,
                                        money,
                                        nickname
                                        ) 
                            VALUES (
                                {st.session_state.student_id},
                                '{st.session_state.selected_category}',
                                '{','.join(st.session_state.purpose)}',
                                '{','.join(adjusted_selected_shops)}',
                                '{','.join(adjusted_output_a)}',
                                '{','.join(adjusted_output_b)}',
                                '{','.join(st.session_state.timechoice)}',
                                '{st.session_state.intrestmatch}',
                                '{adjusted_fd1}',       
                                '{st.session_state.pathconvenience}',
                                '{adjusted_fd2}', 
                                '{st.session_state.timelimit}',
                                '{adjusted_fd3}', 
                                '{st.session_state.pathvariety}',
                                '{adjusted_fd4}',     
                                '{st.session_state.boredom}',
                                '{adjusted_fd5}', 
                                {st.session_state.rating_A},
                                {st.session_state.rating_B},
                                '{st.session_state.random}',
                                '{st.session_state.timeBegin}',
                                '{st.session_state.timeFinish}',
                                '{st.session_state.timeBegin_2}',
                                '{st.session_state.timeBegin_3}',
                                '{st.session_state.likelihood}',
                                '{st.session_state.gender}',
                                '{st.session_state.age}',
                                '{st.session_state.grade}',
                                '{st.session_state.money}',
                                '{st.session_state.nickname}'
                            );"""
                        query = text(x)
                        result = conn.execute(query)  # 执行插入
                        if result:
                            conn.commit()  # 提交事务
                            st.session_state.button_clicked = True 
                        else:
                            st.sidebar.error("未能检索数据，连接失败。")
        except SQLAlchemyError as e:
                    st.sidebar.error(f"连接到数据库失败: {e}")
   


def render_rec_sidebar():      
    with st.sidebar:
        st.title("问卷调查")
        st.markdown("请认真完成所有内容的填写，这可能会影响你最终的得分。")
        default_option_index = None
        st.session_state.rating_A = 0
        st.session_state.rating_B = 0
        st.session_state.feedback1 = ""
        st.session_state.feedback2 = ""
        st.session_state.feedback3 = ""
        st.session_state.feedback4 = ""
        st.session_state.feedback5 = ""

        #兴趣匹配度
        st.session_state.intrestmatch = ""
        st.session_state.intrestmatch = st.sidebar.selectbox("__1.兴趣匹配度：__ 哪个模型推荐的行程能更好地匹配你的逛店需求和兴趣、较少包含兴趣无关的店铺？",["模型A","模型B","二者接近","均无"],default_option_index)
        st.session_state.feedback1 = st.text_area("请说明理由：",key="str1")
        #路径便利性
        st.session_state.pathconvenience = ""
        st.session_state.pathconvenience = st.sidebar.selectbox("__2.路径便利性：__ 哪个模型推荐的行程更符合人们的步行移动习惯，少有绕路、来回跳转的现象？可结合右侧的路径展示图进行判断。",["模型A","模型B","二者接近","均无"],default_option_index)
        st.session_state.feedback2 = st.text_area("请结合平面图的店铺分布给出绕路的行程段：",key="str2")
        #时间/精力限制
        st.session_state.timelimit = ""
        st.session_state.timelimit = st.sidebar.selectbox("__3.时间/精力限制：__ 哪个模型推荐的行程就长度和店铺构成而言更符合你的时间和体力限制，不会反复推荐耗时、费体力的店铺？可结合右侧平均停留时间判断。",["模型A","模型B","二者接近","均无"],default_option_index)
        st.session_state.feedback3 = st.text_area("请给出不符合时间/精力限制的行程段：",key="str3")
        #行程多样性
        st.session_state.pathvariety = ""
        st.session_state.pathvariety = st.sidebar.selectbox("__4.行程多样性：__ 哪个模型推荐的行程更能满足你实际逛店情境中多样化的逛店需求（即包含多个逛店类别且匹配你的实际偏好）？可结合右侧店铺类别信息判断。",["模型A","模型B","二者接近","均无"],default_option_index)
        st.session_state.feedback4 = st.text_area("请说明理由：",key="str4")
        #乏味感
        st.session_state.boredom = ""
        st.session_state.boredom = st.sidebar.selectbox("__5.乏味感：__ 哪个模型推荐的行程会重复推荐类似店铺的情况，超出你的需求范围，让你感到乏味、无趣？",["模型A","模型B","均有","均无"],default_option_index)
        st.session_state.feedback5 = st.text_area("请给出重复推荐、让你感到乏味的行程段：",key="str5")
        st.markdown("__整体评估__：")
        st.session_state.rating_A = st.slider("综合多个维度，模型A推荐的行程你打几分？(5分为最佳)", 1, 5)
        st.session_state.rating_B = st.slider("综合多个维度，模型B推荐的行程你打几分？(5分为最佳)", 1, 5)

        feedbacks = [
            st.session_state.feedback1,
            st.session_state.feedback2,
            st.session_state.feedback3,
            st.session_state.feedback4,
            st.session_state.feedback5,
        ]
        basemoney = 30
        score_str = score_for_feedback(feedbacks,st.session_state.pathconvenience,st.session_state.timelimit,st.session_state.boredom)
        score_trace  = (-m.model_get_likelihood(trans.get_idxlist(st.session_state.selected_shops))-20)/10  
        st.session_state.likelihood = m.model_get_likelihood(trans.get_idxlist(st.session_state.selected_shops))
        st.session_state.money = basemoney+ score_trace +score_str
        formatted_money = "{:.1f}".format(st.session_state.money)
        formatted_score = "{:.1f}".format(float(score_trace))
        if st.session_state.sqlerro:
            st.sidebar.error('请填写完整信息')
        if not st.session_state.button_clicked:
                button = st.button("完成",on_click=button_clicked)
        #（其中问卷部分为：{score_str}, 路径实验部分为：{formatted_score}）
        else:st.sidebar.success(f"恭喜完成本次实验! 您的实验收益为：{formatted_money}元") 
        # 老版本问卷
        # st.session_state.recommendations_1 = []
        # st.session_state.recommendations_2 = []
        # st.session_state.model_choice_ac = ""
        # st.session_state.model_choice_sup = ""

        # st.session_state.feedback = ""
        # default_option_index = None
        # st.session_state.recommendations_1 = st.selectbox(
        #     "根据模型 A推荐结果，选择你感兴趣访问的下一个店铺:",
        #     ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","推荐结果6", "推荐结果7", "推荐结果8", "推荐结果9", "推荐结果10","无"],default_option_index
        # )
        # st.session_state.recommendations_2 = st.selectbox(
        #     "根据模型 B推荐结果，选择你感兴趣访问的下一个店铺:",
        #     ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","推荐结果6", "推荐结果7", "推荐结果8", "推荐结果9", "推荐结果10","无"],default_option_index
        # )
        # if st.session_state.recommendations_1 == None or st.session_state.recommendations_2 == None:
        #     st.session_state.recstate = False 
        # else: st.session_state.recstate = True
        # if st.session_state.recstate:
        #     st.session_state.model_choice_acc = st.selectbox("推荐准确性：哪个模型的推荐列表更加匹配你此刻的逛店意图和需求?", ["模型A", "模型B"],default_option_index)
        #     st.session_state.model_choice_sup = st.selectbox("推荐新颖性：哪个模型的推荐列表让你感觉更加出乎意料?", ["模型A", "模型B"],default_option_index)
        #     st.session_state.rating_A = st.slider("给模型A给个主观评分，你会打几分?(5分为最佳)", 1, 5)
        #     st.session_state.rating_B = st.slider("给模型B给个主观评分，你会打几分?(5分为最佳)", 1, 5)
        #     st.session_state.feedback = st.text_area("请填写其他的建议或者评价(选填)：")
     
                
            

def generate_markdown(i,idx):
    for item in range(len(data)) :
        if data["StoreName"][item] == idx:
            #store_markdown = f"{i}\t __{data['StoreName'][item]}__，{data['floor'][item]}{data['zoom'][item]}，{data['new_category'][item]}\n"
            store_markdown_1 = f'<span style="display: inline-block;font-size:18px;margin-top: 10px; margin-bottom: -10px;">{i} __{data["StoreName"][item]}__  </span>'
            store_markdown_2 = f'<span style="display: inline-block;font-size:14px;margin-top: 10px; margin-bottom: -10px;">，{data["floor"][item]}，{data["new_category"][item]}</span>'
    return store_markdown_1 + store_markdown_2
def generate_image(idx):
    for item in range(len(data)) :
        if data["StoreName"][item] == idx:
            store_image = f"store/{data['StoreName'][item]}.jpg"
            return store_image
def toggle_content1():
    st.session_state.content1 = not st.session_state.content1
def toggle_content2():
    st.session_state.content2 = not st.session_state.content2

def scroll_to_top():
    # 使用 Streamlit 的 html 功能加载自定义 JavaScript
    st.write(
        """
        <script type="text/javascript">
            // 通过 JavaScript 强制滚动到顶部
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

def render_result_page():
    if st.session_state.top:
        scroll_to_top()
        st.session_state.top = False
    if 'content1' not in st.session_state:
        st.session_state.content1 = False
    if 'content2' not in st.session_state:
        st.session_state.content2 = False
    
    st.markdown("## 推荐模型对比与评估")

    #st.markdown(f"## {st.session_state.nickname}同学，您的逛店信息与模型推荐路径如下，请仔细浏览后完成左侧的问卷：")# {st.session_state.nickname}
    # st.markdown(f"__逛店目标__："+"，".join(st.session_state.purpose)) # {st.session_state.purpose}
    st.markdown("__输入序列__："+" &rarr;  ".join(st.session_state.selected_shops))# +" &rarr;  ".join(st.session_state.selected_shops)
    input_idx = trans.get_idxlist(st.session_state.selected_shops)
    output_idx_0 = m.model_ddsm(input_idx)
    output_idx_1 = m.model_ddsmds(input_idx)
    if st.session_state.random == 2: #1不变，2交换
        i = output_idx_0
        output_idx_0 = output_idx_1
        output_idx_1 = i
    output_store_0 =trans.get_storelist(output_idx_0)
    output_store_1 =trans.get_storelist(output_idx_1)

    st.session_state.output_a = output_store_0
    st.session_state.output_b = output_store_1
    #position = {"top": -112, "left": 0, "width": 1000, "height": 600}
    #if st.session_state.random == 1: #blindseed为1 则 A为ddms
    st.markdown("__模型A__："+" &rarr;  ".join(output_store_0))
    st.markdown("__模型B__："+" &rarr;  ".join(output_store_1))
    st.markdown(" ")
    st.markdown("请对于模型A、B的推荐结果进行评价，完成左侧问卷。下方展示了推荐行程对应的路径演示、所含类别和停留时间信息，为你的评估决策提供参考。")
    custom_css = """
    <style>
    .horizontal-line {
        margin-top: 0px; /* 上间距 */
        margin-bottom: 5px; /* 下间距 */
        border-top: 1px solid #D3D3D3; /* 横线样式，浅灰色 */
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)
    st.markdown("__推荐行程的路径展示__（请先选择模型）")
    trace1 = "-".join(str(num) for num in input_idx)
    trace2 = "-".join(str(num) for num in output_idx_0)
    trace3 = "-".join(str(num) for num in output_idx_1)
    url_trace = f"https://storerecommend.cn:8080/track.html?seq={trace1}&path-a={trace2}&path-b={trace3}"
    position = {"top": -150, "left": 0, "width": 1150, "height": 625}
    st.components.v1.html(f'''
    <div style="position: relative; overflow: hidden; width: {position["width"]}px; height: {position["height"]}px;">
        <iframe
            src="{url_trace}"
            frameborder="0"
            style="
                position: absolute;
                top: {position["top"]}px; 
                left: {position["left"]}px; 
                width: {position["width"]}px; 
                height: {position["height"]}px;
                overflow: hidden;
            "
            ></iframe>
    </div>
    ''', height=position["height"]-150, width=position["width"])
    # st.components.v1.html(f'''
    # <div style="position: relative; overflow: hidden; width: 100%; aspect-ratio: {position["width"]/position["height"]};">
    #     <iframe
    #         src="{url_trace}"
    #         width="100%"
    #         height="100%"
    #         frameborder="0"
    #         style="transform:translate({position["left"]}px, {position["top"]}px);"
    #         >
    #     </iframe>
    # </div>
    # ''', height=position["height"], width=position["width"])
    # else:
    #     st.markdown("__模型A__："+" &rarr;  ".join(output_store_1))
    #     st.markdown("__模型B__："+" &rarr;  ".join(output_store_0))
    #st.markdown("---")
    st.markdown("__逛店行程中店铺的对应类别：__")
    st.markdown("__输入序列__："+" &rarr; ".join(trans.get_catlist(input_idx)))
    st.markdown("__模型A__："+" &rarr;  ".join(trans.get_catlist(output_idx_0)))
    st.markdown("__模型B__："+" &rarr;  ".join(trans.get_catlist(output_idx_1)))
    st.markdown("__推荐行程中店铺的平均停留时间(单位：分钟)：__")
    sum0 = int(sum(trans.get_tlist(output_idx_0)))
    sum1 = int(sum(trans.get_tlist(output_idx_1)))
    shop_names0 = trans.get_storelist(output_idx_0)
    time_spent0= [str(int(num)) for num in trans.get_tlist(output_idx_0)]
    combined_list0 = zip(shop_names0, time_spent0)
    formatted_list0 = [f"{name} ({time})" for name, time in combined_list0]
    formatted_output0 = " &rarr; ".join(formatted_list0)
    st.markdown(f"__模型A__：{formatted_output0}（行程总计：{sum0}分钟）")
    shop_names1 = trans.get_storelist(output_idx_1)
    time_spent1= [str(int(num)) for num in trans.get_tlist(output_idx_1)]
    combined_list1 = zip(shop_names1, time_spent1)
    formatted_list1 = [f"{name} ({time})" for name, time in combined_list1]
    formatted_output1 = " &rarr; ".join(formatted_list1)
    st.markdown(f"__模型B__：{formatted_output1}（行程总计：{sum1}分钟）")



    # 打分
    # st.session_state.likelihood = m.model_get_likelihood(input_idx)
    # st.session_state.percentile = m.get_percentile(st.session_state.likelihood, len(input_idx_0)) 
    # st.markdown(f"测试内容：路径打分：likelihood打分：{st.session_state.likelihood:.3f}")
    # st.markdown(f"分位数打分在三种scale下的打分："+",".join(st.session_state.percentile))
    # st.markdown(f"__当前所在位置__：{ data.loc[data['StoreName'] == st.session_state.selected_store, 'floor'].squeeze()}")
    # src_url2 = f"https://storerecommend.cn:8080/?storeIdx={st.session_state.position}"
    # st.markdown(f'<a href="{src_url2}" target="_blank">点击查看地图</a>', unsafe_allow_html=True)
    #st.button("显示地图",on_click=go_to_map)
    # st.markdown("---")
    # col1, col2 = st.columns([1, 1])
    # if st.session_state.random == 1:
    #     with col1: 
    #         st.markdown("### 模型A的推荐结果")
    #         #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
    #         input_idx = trans.get_idxlist(st.session_state.selected_shops)
    #         #input_idx = trans.get_idxlist(input_test)
    #         output_idx = m.model_ddsm(input_idx)
    #         output_store =trans.get_storelist(output_idx)
    #         i = 1
    #         st.markdown("")
    #         for idx in output_store:
    #             markdown = generate_markdown(i,idx)
    #             i +=1 
    #             st.write(markdown,unsafe_allow_html=True)
    #             store_image=generate_image(idx)
    #             st.image(store_image, width=200)
    #             if i == 6: break
    #         st.button("展开/收回 更多推荐结果", on_click=toggle_content1, key="button1")
    #         if st.session_state.content1:
    #             for idx in output_store[5:10]:
    #                 markdown = generate_markdown(i,idx)
    #                 i +=1 
    #                 st.write(markdown,unsafe_allow_html=True)
    #                 store_image=generate_image(idx)
    #                 st.image(store_image, width=200)


    #     with col2:
    #         st.markdown("### 模型B的推荐结果")
    #         #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
    #         input_idx_1 = trans.get_idxlist(st.session_state.selected_shops)
    #         #input_idx = trans.get_idxlist(input_test)
    #         output_idx_1 = m.model_ddsmds(input_idx_1)
    #         output_store_1 =trans.get_storelist(output_idx_1)
    #         i = 1
    #         st.markdown("")
    #         for idx in output_store_1:
    #             markdown_1 = generate_markdown(i,idx)
    #             i +=1 
    #             st.write(markdown_1,unsafe_allow_html=True)
    #             store_image=generate_image(idx)
    #             st.image(store_image, width=200)
    #             if i == 6: break
    #         st.button("展开/收回 更多推荐结果", on_click=toggle_content2, key="button2")
    #         if st.session_state.content2:
    #             for idx in output_store_1[5:10]:
    #                 markdown_1 = generate_markdown(i,idx)
    #                 i +=1 
    #                 st.write(markdown_1,unsafe_allow_html=True)
    #                 store_image=generate_image(idx)
    #                 st.image(store_image, width=200)
    # else: 
    #     with col2:
    #         st.markdown("### 模型B的推荐结果")
    #         #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
    #         input_idx_3 = trans.get_idxlist(st.session_state.selected_shops)
    #         #input_idx = trans.get_idxlist(input_test)
    #         output_idx_3 = m.model_ddsm(input_idx_3)
    #         output_store_3 =trans.get_storelist(output_idx_3)
    #         i = 1
    #         st.markdown("")
    #         for idx in output_store_3:
    #             markdown_3 = generate_markdown(i,idx)
    #             i +=1 
    #             st.write(markdown_3,unsafe_allow_html=True)
    #             store_image=generate_image(idx)
    #             st.image(store_image, width=200)            
    #             if i == 6: break
    #         st.button("展开/收回 更多推荐结果", on_click=toggle_content2, key="button2")
    #         if st.session_state.content2:
    #             # 显示更多内容
    #             for idx in output_store_3[5:10]:
    #                 markdown_3 = generate_markdown(i,idx)
    #                 i +=1 
    #                 st.write(markdown_3,unsafe_allow_html=True)
    #                 store_image=generate_image(idx)
    #                 st.image(store_image, width=200)

    #     with col1:
    #         st.markdown("### 模型A的推荐结果")
    #         #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
    #         input_idx_2 = trans.get_idxlist(st.session_state.selected_shops)
    #         #input_idx = trans.get_idxlist(input_test)
    #         output_idx_2 = m.model_ddsmds(input_idx_2)
    #         output_store_2 =trans.get_storelist(output_idx_2)
    #         i = 1
    #         st.markdown("")
    #         for idx in output_store_2:
    #             markdown_2 = generate_markdown(i,idx)
    #             i +=1 
    #             st.write(markdown_2,unsafe_allow_html=True)
    #             store_image=generate_image(idx)
    #             st.image(store_image, width=200)            
    #             if i == 6: break
    #         st.button("展开/收回 更多推荐结果", on_click=toggle_content1, key="button1")
    #         if st.session_state.content1:
    #             for idx in output_store_2[5:10]:
    #                 markdown_2 = generate_markdown(i,idx)
    #                 i +=1 
    #                 st.write(markdown_2,unsafe_allow_html=True)
    #                 store_image=generate_image(idx)
    #                 st.image(store_image, width=200)


def render_rec_page():
    render_rec_sidebar()
    render_result_page()


###########
#定义全局框架
if st.session_state.page == 'welcome':
    st.session_state.timeBegin = gettime()
    render_welcome_page()
elif st.session_state.page == 'shopping_page':
    render_shopping_page()       
elif st.session_state.page == 'rec_page':
    render_rec_page() 

