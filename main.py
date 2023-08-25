''' 
这是一个使用 Eel、Pandas 和其他一些 Python 库进行 CSV 文件处理的程序。
Eel 是一个用于制作简单 Electron-like 桌面应用的 Python 库，其中前端使用 HTML/CSS/JS，后端使用 Python。
'''
import numpy as np
import eel
import os
import csv
import glob
import tkinter as tk
import pandas as pd
from tkinter import filedialog
import chardet

eel.init('web')  # 初始化Eel，设置web文件夹为前端文件位置

@eel.expose  # 使用此装饰器暴露Python函数给JavaScript
def open_directory_dialog(): # 打开文件夹选择对话框
    root = tk.Tk()  
    root.withdraw()  # 隐藏Tk窗口
    directory_path = filedialog.askdirectory()  # 打开文件夹选择对话框
    eel.receive_directory(directory_path)  # 将选择的路径传递给前端
    load_csv_files(directory_path)  # 加载选定文件夹的CSV文件

@eel.expose
def load_current_directory():   # 加载当前工作目录的CSV文件
    path = os.getcwd()  # 获取当前工作目录路径
    eel.receive_directory(path)
    load_csv_files(path)

@eel.expose
def query_csv_files(query_words,query_files):   # 读取CSV文件内容
    print(query_words)
    for csv_file in query_files:
        if('rows' in csv_file and 'query' in csv_file and csv_file['query'] == query_words): 
            continue
        df = pd.read_csv(csv_file['path'],encoding=csv_file['encoding'])  # 读取CSV文件
        df = df.replace(np.nan, '', regex=True)  # 替换NaN值为空字符串
        rows = df[df['REPKCode'] == query_words].to_dict(orient='records')  # 查询特定的行
        print(rows)
        csv_file['rows'] = rows
        csv_file['query'] = query_words
    eel.receive_csv_query_files(query_files)  # 将查询结果传递给前端

def get_encoding(file): # 获取文件编码  
    with open(file, 'rb') as f:  
        result = chardet.detect(f.read())  # 使用chardet检测文件编码
    return result['encoding']

def load_csv_files(path):   # 读取CSV文件头
    csv_files = glob.glob(os.path.join(path, '*.csv'))  # 获取文件夹中所有CSV文件路径

    total_files = len(csv_files)
    current_file_number = 0

    result = []

    for csv_file in csv_files:
        encoding = get_encoding(csv_file)  # 获取文件编码
        current_file_number += 1
        eel.update_progress(current_file_number,total_files, os.path.basename(csv_file))  # 更新前端进度条
        with open(csv_file, 'r',encoding=encoding) as f:
            reader = csv.reader(f)
            headers = next(reader)  # 读取CSV文件头

        file_info = {
            'id': current_file_number-1,
            'name': os.path.basename(csv_file),
            'path': csv_file,
            'encoding':encoding,
            'headers': headers
        }
        result.append(file_info)

    eel.receive_csv_files(total_files,result)  # 将文件信息传递给前端

eel.start('index.html',port=0,size=(1000, 600))  # 启动Eel，设置初始页面和窗口大小