import os
import pandas as pd
import streamlit as st
from pathlib import Path
import time
import numpy as np
from PIL import Image
from img_manager import ImageDirManager

st.title('微博图片打分系统')

img_dir = '/data/users/libo/QA/MetaIQA-master/weibo_images'
options = np.arange(0.5, 5.5, 0.5).tolist()
options = [-1] + options


def previous_image():
    image_index = st.session_state['image_index']
    if image_index > 0:
        st.session_state['image_index'] -= 1
        st.session_state['score'] = -1
        st.session_state['annot_info'].drop(labels=st.session_state['files'][image_index], axis=0, inplace=True)     # 跳到上一张则删除当前图片的标注
    else:
        st.warning('This is the first image.')


def next_image():
    image_index = st.session_state['image_index']
    if image_index < len(st.session_state['files']) - 1:
        st.session_state['image_index'] += 1
        st.session_state['score'] = -1         # 重置单选框
    else:
        st.warning('This is the last image.')


def resizing_img(img, max_height=700, max_width=700):
    resized_img = img.copy()
    if resized_img.height > max_height:
        ratio = max_height / resized_img.height
        resized_img = resized_img.resize(
            (int(resized_img.width*ratio), int(resized_img.height*ratio))
        )
    if resized_img.width > max_width:
        ratio = max_width / resized_img.width
        resized_img = resized_img.resize(
            (int(resized_img.width*ratio), int(resized_img.height*ratio))
        )

    return resized_img


def save_annotation_info():
    annot_info = st.session_state['annot_info']
    annot_info.to_excel(st.session_state['annot_file'])


def after_submit(name):        # 第一次点击提交后初始化一些状态信息
    st.session_state['submitted'] = True  # 登陆后的后续操作继续保持为True的状态
    annot_file = './{}.xlsx'.format(name)
    idm = ImageDirManager(img_dir, annot_file)  # 后续被销毁
    st.session_state['annot_file'] = annot_file
    st.session_state['annot_info'] = idm.get_exist_annotation_info()
    st.session_state['files'] = idm.get_all_files()
    if len(st.session_state['annot_info']) < len(st.session_state['files']):
        st.session_state["image_index"] = len(st.session_state['annot_info'])
    else:
        st.session_state["image_index"] = len(st.session_state['files']) - 1


with st.sidebar:
    with st.form('my_form'):
        name = st.text_input('登录:')
        submitted = st.form_submit_button('提交')
        if submitted:      # 只在第一次点击提交按钮时为True, 执行一次
            after_submit(name)
        if 'submitted' not in st.session_state:
            st.session_state['submitted'] = False

    score = st.radio('选择分数:', options=options, key='score', disabled=not st.session_state['submitted'])
    if st.session_state['submitted']:
        img_file_name = st.session_state['files'][st.session_state['image_index']]
        st.session_state['annot_info'].loc[img_file_name] = {'score': score}

    col1, col2 = st.columns(2)
    col1.button('上一张', on_click=previous_image, disabled=not st.session_state['submitted'])
    col2.button('下一张', on_click=next_image, disabled=not st.session_state['submitted'])
    saved = st.button('保存', on_click=save_annotation_info, disabled=not st.session_state['submitted'])
    if st.session_state['submitted']:
        st.progress(1.0 * (st.session_state['image_index']+1) / len(st.session_state['files']), text='标注进度')
    else:
        st.progress(0.0, text='标注进度')

if st.session_state['submitted']:       # 如果为已登录状态
    img_path = os.path.join(img_dir, img_file_name)
    st.image(resizing_img(Image.open(img_path)))
if saved and len(st.session_state['files']) == len(st.session_state['annot_info']):
    st.balloons()
