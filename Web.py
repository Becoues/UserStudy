from queue import Full
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
import csv
import os
from data_pre import Category,new_data as data



if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

floor_images = {
    1: '1f.png',
    2: '2f.png',
    3: '3f.png',
    4: '4f.png'
}

####################################################

def render_welcome_page():
    with st.sidebar:
        st.markdown("# 请在下方填写对应信息并提交：😊")
        st.session_state.student_id = ""
        st.session_state.interests = ""
        st.session_state.student_id = st.text_input("学号:",placeholder="2023214419")
        st.session_state.interests = st.multiselect("选择你喜欢的方向:",Category,placeholder="可以选多个哦")
        st.session_state.purpose = st.selectbox("你来逛商场的目的:", ["购物", "吃饭", "休闲娱乐","随便逛逛"],placeholder=" ")
        submitted = st.button("提交")
    st.title("欢迎来到我们的商场推荐系统实验项目！💕")
    st.markdown("## 请在侧边栏填写对应信息并提交，并仔细阅读下方的注意事项，我们将为您推荐最适合您的商场体验！")
    st.markdown("### 注意事项：")
    st.markdown("1. 请仔细填写信息，请勿随便填写。")
    st.markdown("2. 请模拟您的真实逛店想法，以帮助我们实现更好的推荐效果。")
    st.markdown("3. 请在提交前仔细核对您的信息，提交后将无法更改。")
    if submitted:
        if st.session_state.student_id == "" or st.session_state.interests == "" :
            st.sidebar.error("请填写完整信息！")
        else:
            st.session_state.page = 'shopping_page'
            

##############################################   

def render_floor_sidebar():
    st.sidebar.title(f"欢迎学号为{st.session_state.student_id}的同学，来到我们的商场！")
    # 楼层选择
    floors = ['一楼', '二楼', '三楼', '四楼']
    selected_floor = st.sidebar.selectbox("请选择你想要前往的楼层",floors)
    st.session_state.floor = selected_floor

def go_to_page_rec():
    st.session_state.page = 'rec_page'
    
def render_store_sidebar():
    n_floor_data = data[ data['floor'] == st.session_state.floor][['StoreName']]
    st.session_state.shop_list= n_floor_data['StoreName'].unique().tolist()
    st.session_state.selected_shops = {}
    st.session_state.selected_shops = st.sidebar.multiselect(f"请选择您{st.session_state.floor}感兴趣的商铺：(请选择三个商铺)",st.session_state.shop_list)
    # 提交按钮
    if st.sidebar.button('我选好啦'):
        if len(st.session_state.selected_shops) != 3:
            st.sidebar.error("请选择三个商铺！")
        else:
            selected_info = "👌您选择的商铺是：" + "-> ".join(st.session_state.selected_shops)
            st.sidebar.markdown(selected_info)
            st.sidebar.button('确定，开始推荐！',on_click= go_to_page_rec)
        
def render_floor_page(i=1):
    st.title(f"欢迎来到{st.session_state.floor}!")
    st.write(f"👍可以写一点关于{st.session_state.floor}的介绍")
    st.write("这里是商场的平面图，您可以在下方查看商铺的具体信息。")
    image_path = floor_images.get(i)
    image = Image.open(image_path)
    image_array = np.array(image)
    fig = px.imshow(image_array)
    fig.update_layout(dragmode="pan",
                      xaxis_visible=False,  
                      yaxis_visible=False,  
                      xaxis_showticklabels=False, 
                      yaxis_showticklabels=False) 
    st.plotly_chart(fig, use_container_width=True)

    store_logo_list = []

    for store in st.session_state.shop_list:
        png_path = f"image/{store}-1.png"
        jpg_path = f"image/{store}-1.jpg"
        # 首先检查 png 文件是否存在
        if os.path.exists(png_path):
            store_logo_list.append([store, png_path])
        # 如果 png 文件不存在，则检查 jpg 文件
        elif os.path.exists(jpg_path):
            store_logo_list.append([store, jpg_path])
        # 如果 jpg 文件也不存在，则将路径设置为空字符串
        else:
            store_logo_list.append([store, ""])


    like_store = []
    like_store = data[data['CategoryName'].isin(st.session_state.interests)]
    store_names_list = like_store['StoreName'].tolist()
    # 创建8x6表格布局
    for i in range(0, len(store_logo_list), 6):
        cols = st.columns(6)  # 创建6列
        for col, (shop_name, shop_image) in zip(cols, store_logo_list[i:i+6]):
            with col:
                if shop_image!="":
                    if shop_name in store_names_list:
                        shop_name = f"❤️{shop_name}"
                    base_height = 100
                    img = Image.open(shop_image)
                    h_percent = (base_height / float(img.size[1]))
                    w_size = int((float(img.size[0]) * float(h_percent)))
                    img = img.resize((w_size, base_height))
                    st.image(img, caption=shop_name)
                else: continue
    
def render_shopping_page():
    render_floor_sidebar()
    if st.session_state.floor == "一楼":
        render_store_sidebar()
        render_floor_page(1)
    elif st.session_state.floor == "二楼":
        render_store_sidebar()
        render_floor_page(2)
    elif st.session_state.floor == "三楼":
        render_store_sidebar()
        render_floor_page(3)
    elif st.session_state.floor == "四楼":
        render_store_sidebar()
        render_floor_page(4)

##############################################
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

def button_clicked():
    st.session_state.button_clicked = True


def render_rec_sidebar():       
    with st.sidebar:
        st.title("问卷调查")
        model_choice = st.selectbox("请选择你觉得推荐效果更好的模型：", ["模型A", "模型B"])
        rating = st.slider("请根据这个推荐结果给予评价", 1, 5)
        recommendations = []
        recommendations = st.multiselect(
            "请选择你觉得不错的推荐结果：",
            ["推荐结果1", "推荐结果2", "推荐结果3", "推荐结果4", "推荐结果5"]
        )
        feedback = st.text_area("请填写其他的建议或者评价(选填)：")

        if not st.session_state.button_clicked:
            button = st.button("完成")
            if button:
                if recommendations == []:
                    st.sidebar.error("未完成必填项目！")
                else:
                    file_path = "feedback.csv"
                    file_exists = os.path.isfile(file_path)
                    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入头部
                        if not file_exists:
                            writer.writerow(["模型选择", "评价分数", "喜欢的推荐结果", "其他建议或评价"])
                        writer.writerow([st.session_state.student_id,", ".join(st.session_state.interests),st.session_state.purpose,", ".join(st.session_state.selected_shops),model_choice,rating, ", ".join(recommendations),feedback])
                    button_clicked()
                            
        else:
             st.success("恭喜你完成本次实验！")     
            


def render_result_page():
    st.title("模型推荐对比")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("模型A的推荐结果")
        st.write("这里展示模型A的推荐内容。")
    with col2:
        st.header("模型B的推荐结果")
        st.write("这里展示模型B的推荐内容。")


def render_rec_page():
    render_rec_sidebar()
    render_result_page()


###########
#定义全局框架
    # 初始化或获取session_state中的页面状态

if st.session_state.page == 'welcome':
    render_welcome_page()
elif st.session_state.page == 'shopping_page':
    render_shopping_page()       
elif st.session_state.page == 'rec_page':
    render_rec_page() 
