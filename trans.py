import streamlit as st
from data_pre import Category,new_data as data

#input =  ['Gant', 'GUESS', 'Armani Exchange', 'Evisu', 'G-STAR'] #填写的输出（3~5个），可以直接转成idxlist；展示的输入
#output = [73,37,130,23,6]  #模型的输入与输出，输入为3~5个

def get_storename(idx):
    for item in range(len(data)) :
        if data["idx_x"][item] == idx:
            store_name = data['StoreName'][item]
            return store_name 
def get_storelist(output):
    storelist =[]
    for idx in output:
        storelist.append(get_storename(idx))
    return storelist

def get_idx(storename):
    for item in range(len(data)) :
        if data["StoreName"][item] == storename:
            idx = data['idx_x'][item]
            return idx
def get_idxlist(input):
    idxlist =[]
    for storename in input:
        idxlist.append(get_idx(storename))
    return idxlist

def get_cat(idx):
    for item in range(len(data)) :
        if data["idx_x"][item] == idx:
            cat = data['new_category'][item]
            return cat
def get_catlist(output):
    catlist =[]
    for idx in output:
        catlist.append(get_cat(idx))
    return catlist

def get_t(idx):
    for item in range(len(data)) :
        if data["idx_x"][item] == idx:
            t = data['shoptime'][item]
            return t
def get_tlist(output):
    tlist =[]
    for idx in output:
        tlist.append(get_t(idx))
    return tlist


#generate_result(output)
#print("对应的店铺名：", get_storelist(output))
#print("对应的idx：", get_idxlist(input))