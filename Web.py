from queue import Full
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
from data_pre import Category,SiteID,new_data as data
from datetime import datetime
import plotly.express as px 
from sqlalchemy import create_engine, text
import pymysql

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
category_mapping = {
    "配饰珠宝": 0,  # 0表示配饰及珠宝
    "运动休闲": 1,  # 1表示与运动和休闲相关的
    "杂品集合": 2,  # 2表示各类杂项商品集合
    "男装": 3,  # 3表示男性服装
    "潮流时尚": 4,  # 4表示潮流和时尚类目
    "家居家用": 5,  # 5表示家居及家用商品
    "女装": 6,  # 6表示女性服装
    "休闲快餐与饮品": 7,  # 7表示休闲快餐和饮品
    "数码电子": 8,  # 8表示数码产品和电子设备
    "美妆护肤": 9,  # 9表示美妆和护肤产品
    "鞋品箱包": 10,  # 10表示鞋类和箱包
    "亲子": 11,  # 11表示亲子相关的商品或活动
    "体验业态": 12,  # 12表示体验和活动，如艺术、手工等
    "餐饮美食": 13,  # 13表示餐饮美食
}
def botton_c ():
    # if st.session_state.student_id == "" or st.session_state.nickname == "" or st.session_state.purpose== "":
    #     st.session_state.page = 'welcome'
    # else: st.session_state.page = 'shopping_page' 
    if st.session_state.student_id == "" or st.session_state.nickname == "" :
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
        st.session_state.student_id = st.text_input("学号:",placeholder="请输入您的学号")
        st.session_state.nickname = st.text_input("昵称:",placeholder="我们可以怎么称呼您呢")
        
        
        

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
    "潮流时尚": "🕶",  # 表示潮流和时尚类目
    "家居家用": "🏡",  # 表示家居及家用商品
    "女装": "👗",  # 表示女性服装
    "休闲快餐与饮品": "🍔",  # 表示休闲快餐和饮品
    "数码电子": "📱",  # 表示数码产品和电子设备
    "美妆护肤": "💄",  # 表示美妆和护肤产品
    "鞋品箱包": "👠👜",  # 表示鞋类和箱包
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
    categories =list(category_mapping.keys())
    st.session_state.purpose = st.sidebar.multiselect("你可以预想一下你逛商场的目的:", categories)
    try:
        st.session_state.cat = category_mapping[st.session_state.purpose[-1]]
    except:
        st.session_state.cat = 0
    st.session_state.selected_category = st.sidebar.selectbox('根据品类查询楼层和top3店铺分布:',options=data['new_category'].unique(),index=st.session_state.cat,key="select0")
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
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)
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
        st.sidebar.button("选第三个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "3":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)
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
        st.sidebar.button('我选好了，开始推荐！',on_click= go_to_page_rec)
        st.sidebar.button("选第四个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "4":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)   
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
        st.sidebar.button('我选好了，开始推荐！',on_click= go_to_page_rec)
        st.sidebar.button("选第五个", on_click=sidebarclick)
    if st.session_state.sidebar_input == "5":
        st.session_state.time_s = gettime()
        selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)   
        st.sidebar.markdown(selected_info)
        st.session_state.selected_store=st.sidebar.selectbox(f"请选择您第五个逛的商铺：",st.session_state.shop_list,default_option_index,key="select5")
        if st.session_state.selected_store == None or st.session_state.selected_store == '':
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击该店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
        else:
            st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
        #st.session_state.site = st.sidebar.selectbox(f"请在右侧平面图中点击{st.session_state.selected_store}店铺，输入店铺位置信息，并填入进行验证",SiteID,default_option_index,key="check5")
        st.session_state.ture_site = data.loc[data['StoreName'] == st.session_state.selected_store, 'PlazaUnitID'].squeeze()
        if st.session_state.erro:
            st.sidebar.error('位置与店铺不匹配，请重新填写')
            st.session_state.erro = False
        if st.session_state.erro2:
            st.sidebar.error('请填写完整信息')
            st.session_state.erro2 = False
        st.sidebar.button('我选好了，开始推荐！！',on_click= go_to_page_rec)     


def go_to_page_rec():
    if st.session_state.selected_store == None or st.session_state.selected_store == '' or st.session_state.site== None or st.session_state.site=='':
        st.session_state.erro2 = True
    else:
        if st.session_state.site == st.session_state.ture_site:
            st.session_state.position = data.loc[data['StoreName'] == st.session_state.selected_store,'idx_x'].squeeze()
            st.session_state.selected_shops.append(st.session_state.selected_store)
            st.session_state.timeBegin_3 = gettime()
            st.session_state.page = 'rec_page'
        else : st.session_state.erro = True


        
def render_floor_page():
    st.markdown("## 请沉浸浏览该商场交互平面图，输入感兴趣的逛店序列")
    st.write(f"👍点击查看具体的店铺信息~")
    st.write(f"🙌使用滚轮可以放大缩小平面图~")
    # 要嵌入的网址
    if st.session_state.position == None:
        src_url = "https://111.231.19.111:8080"
    else:
        src_url = f"https://111.231.19.111:8080/?storeIdx={st.session_state.position}"
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


def button_clicked():
    if st.session_state.model_choice_acc == "" or st.session_state.model_choice_sup == "" :
        st.sidebar.error("未完成必填项目！")
    else:
        #链接数据库并导入
            st.session_state.timeFinish = gettime()
            try:
                    # 创建数据库引擎
                    engine = create_engine(DATABASE_URL)
                    # 执行SQL插入操作
                    with engine.connect() as conn:
                        x = f"""INSERT INTO final (student_id, timeBegin, timeFinish, interests, purpose, selected_shops, model_choice_acc, model_choice_sup, rating_A, rating_B, recommendations_1, recommendations_2, feedback, blind_seed,timeBegin_2,timeBegin_3,timechoice,likelihood,percentile)
                            VALUES (
                                {st.session_state.student_id},
                                '{st.session_state.timeBegin}',
                                '{st.session_state.timeFinish}',
                                '{st.session_state.selected_category}',
                                '{','.join(st.session_state.purpose)}',
                                '{','.join(st.session_state.selected_shops)}',
                                '{st.session_state.model_choice_acc}',
                                '{st.session_state.model_choice_sup}',
                                {st.session_state.rating_A},
                                {st.session_state.rating_B},
                                '{st.session_state.recommendations_1}',
                                '{st.session_state.recommendations_2}',
                                '{st.session_state.feedback}',
                                '{st.session_state.random}',
                                '{st.session_state.timeBegin_2}',
                                '{st.session_state.timeBegin_3}',
                                '{','.join(st.session_state.timechoice)}',
                                '{st.session_state.likelihood}',
                                '{','.join(st.session_state.percentile)}'
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
    st.session_state.recstate = False       
    with st.sidebar:
        st.title("问卷调查")
        st.session_state.recommendations_1 = []
        st.session_state.recommendations_2 = []
        st.session_state.model_choice_ac = ""
        st.session_state.model_choice_sup = ""
        st.session_state.rating_A = 0
        st.session_state.rating_B = 0
        st.session_state.feedback = ""
        default_option_index = None
        st.session_state.recommendations_1 = st.selectbox(
            "根据模型 A推荐结果，选择你感兴趣访问的下一个店铺:",
            ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","推荐结果6", "推荐结果7", "推荐结果8", "推荐结果9", "推荐结果10","无"],default_option_index
        )
        st.session_state.recommendations_2 = st.selectbox(
            "根据模型 B推荐结果，选择你感兴趣访问的下一个店铺:",
            ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5","推荐结果6", "推荐结果7", "推荐结果8", "推荐结果9", "推荐结果10","无"],default_option_index
        )
        if st.session_state.recommendations_1 == None or st.session_state.recommendations_2 == None:
            st.session_state.recstate = False 
        else: st.session_state.recstate = True
        if st.session_state.recstate:
            st.session_state.model_choice_acc = st.selectbox("推荐准确性：哪个模型的推荐列表更加匹配你此刻的逛店意图和需求?", ["模型A", "模型B"],default_option_index)
            st.session_state.model_choice_sup = st.selectbox("推荐新颖性：哪个模型的推荐列表让你感觉更加出乎意料?", ["模型A", "模型B"],default_option_index)
            st.session_state.rating_A = st.slider("给模型A给个主观评分，你会打几分?(5分为最佳)", 1, 5)
            st.session_state.rating_B = st.slider("给模型B给个主观评分，你会打几分?(5分为最佳)", 1, 5)
            st.session_state.feedback = st.text_area("请填写其他的建议或者评价(选填)：")
            if not st.session_state.button_clicked:
                button = st.button("完成",on_click=button_clicked)
            else:st.sidebar.success("恭喜完成本次实验! 请关闭页面")        
                
            

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


def render_result_page():
    if 'content1' not in st.session_state:
        st.session_state.content1 = False
    if 'content2' not in st.session_state:
        st.session_state.content2 = False
    st.markdown(f"## {st.session_state.nickname}同学，您留下的逛店信息如下：")# {st.session_state.nickname}
    st.markdown(f"__逛店目标__："+"，".join(st.session_state.purpose)) # {st.session_state.purpose}
    st.markdown("__逛店序列__："+"-> ".join(st.session_state.selected_shops))# +"-> ".join(st.session_state.selected_shops)
    input_idx_0 = trans.get_idxlist(st.session_state.selected_shops)
    st.session_state.likelihood = m.model_get_likelihood(input_idx_0)
    st.session_state.percentile = m.get_percentile(st.session_state.likelihood, len(input_idx_0)) 
    st.markdown(f"测试内容：路径打分：likelihood打分：{st.session_state.likelihood:.3f}")
    st.markdown(f"分位数打分在三种scale下的打分："+",".join(st.session_state.percentile))
    st.markdown(f"__当前所在位置__：{ data.loc[data['StoreName'] == st.session_state.selected_store, 'floor'].squeeze()}")
    src_url2 = f"https://111.231.19.111:8080/?storeIdx={st.session_state.position}"
    st.markdown(f'<a href="{src_url2}" target="_blank">点击查看地图</a>', unsafe_allow_html=True)
    #st.button("显示地图",on_click=go_to_map)
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    if st.session_state.random == 1:
        with col1: 
            st.markdown("### 模型A的推荐结果")
            #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
            input_idx = trans.get_idxlist(st.session_state.selected_shops)
            #input_idx = trans.get_idxlist(input_test)
            output_idx = m.model_ddsm(input_idx)
            output_store =trans.get_storelist(output_idx)
            i = 1
            st.markdown("")
            for idx in output_store:
                markdown = generate_markdown(i,idx)
                i +=1 
                st.write(markdown,unsafe_allow_html=True)
                store_image=generate_image(idx)
                st.image(store_image, width=200)
                if i == 6: break
            st.button("展开/收回 更多推荐结果", on_click=toggle_content1, key="button1")
            if st.session_state.content1:
                for idx in output_store[5:10]:
                    markdown = generate_markdown(i,idx)
                    i +=1 
                    st.write(markdown,unsafe_allow_html=True)
                    store_image=generate_image(idx)
                    st.image(store_image, width=200)


        with col2:
            st.markdown("### 模型B的推荐结果")
            #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
            input_idx_1 = trans.get_idxlist(st.session_state.selected_shops)
            #input_idx = trans.get_idxlist(input_test)
            output_idx_1 = m.model_ddsmds(input_idx_1)
            output_store_1 =trans.get_storelist(output_idx_1)
            i = 1
            st.markdown("")
            for idx in output_store_1:
                markdown_1 = generate_markdown(i,idx)
                i +=1 
                st.write(markdown_1,unsafe_allow_html=True)
                store_image=generate_image(idx)
                st.image(store_image, width=200)
                if i == 6: break
            st.button("展开/收回 更多推荐结果", on_click=toggle_content2, key="button2")
            if st.session_state.content2:
                for idx in output_store_1[5:10]:
                    markdown_1 = generate_markdown(i,idx)
                    i +=1 
                    st.write(markdown_1,unsafe_allow_html=True)
                    store_image=generate_image(idx)
                    st.image(store_image, width=200)
    else: 
        with col2:
            st.markdown("### 模型B的推荐结果")
            #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
            input_idx_3 = trans.get_idxlist(st.session_state.selected_shops)
            #input_idx = trans.get_idxlist(input_test)
            output_idx_3 = m.model_ddsm(input_idx_3)
            output_store_3 =trans.get_storelist(output_idx_3)
            i = 1
            st.markdown("")
            for idx in output_store_3:
                markdown_3 = generate_markdown(i,idx)
                i +=1 
                st.write(markdown_3,unsafe_allow_html=True)
                store_image=generate_image(idx)
                st.image(store_image, width=200)            
                if i == 6: break
            st.button("展开/收回 更多推荐结果", on_click=toggle_content2, key="button2")
            if st.session_state.content2:
                # 显示更多内容
                for idx in output_store_3[5:10]:
                    markdown_3 = generate_markdown(i,idx)
                    i +=1 
                    st.write(markdown_3,unsafe_allow_html=True)
                    store_image=generate_image(idx)
                    st.image(store_image, width=200)

        with col1:
            st.markdown("### 模型A的推荐结果")
            #input_test =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] 
            input_idx_2 = trans.get_idxlist(st.session_state.selected_shops)
            #input_idx = trans.get_idxlist(input_test)
            output_idx_2 = m.model_ddsmds(input_idx_2)
            output_store_2 =trans.get_storelist(output_idx_2)
            i = 1
            st.markdown("")
            for idx in output_store_2:
                markdown_2 = generate_markdown(i,idx)
                i +=1 
                st.write(markdown_2,unsafe_allow_html=True)
                store_image=generate_image(idx)
                st.image(store_image, width=200)            
                if i == 6: break
            st.button("展开/收回 更多推荐结果", on_click=toggle_content1, key="button1")
            if st.session_state.content1:
                for idx in output_store_2[5:10]:
                    markdown_2 = generate_markdown(i,idx)
                    i +=1 
                    st.write(markdown_2,unsafe_allow_html=True)
                    store_image=generate_image(idx)
                    st.image(store_image, width=200)


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

