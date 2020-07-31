#_*_coding=utf-8_*_
# python 3.7
# kotori  QQ:450072402   微信：WLJ_450072402
# kanachan爬虫

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from requests import Session
import time
import os
from queue import Queue
import json
import sys
import re
import logging  #保证session.get()  verify=False条件下不报警告

logging.captureWarnings(True)


global driver, se, time_min, time_max, ranges, download_path, is_over, next_page_exist, google_data_path, download_fluency_control
global headless, load_img
se = Session()
se.keep_alive = False
#全局变量初始化
ranges = 2  #存放页面下翻次数
time_max = 1
time_min = 1
# download_path = "E:\\多媒体\\konachan"
is_over = False  #标记当次img是否已经查询完
next_page_exist = 0
# google_data_path = "C:\\Users\\Mimikko\\AppData\\Local\\Google\\Chrome\\User Data"
download_fluency_control = 0
auto_break = True
auto_break_picNum_exist = 10
break_num_rec = 0
headless = False
load_img = True

url_dic = {'img_url_due': Queue(maxsize=0), 'id_que': Queue(maxsize=0), 'tag_name': Queue(maxsize=0)}

def Google_Driver():
    #配置谷歌路径信息，免登录
    global driver, headless, load_img
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=" + google_data_path)
    if headless == True:  # 使用headless无界面浏览器模式
        print("开启无头浏览器...")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    if load_img == False:  # 不加载图片，减少资源消耗
        print("禁止网页加载图像...")
        prefs = {'profile.managed_default_content_settings.images': 2}
    else:
        prefs = {'profile.managed_default_content_settings.images': 1}
    chrome_options.add_experimental_option('prefs', prefs)
    try:
        driver = webdriver.Chrome(chrome_options=chrome_options)  #这里配合登录谷歌
    except:
        print("请求失败，请检查chrome是否关闭！\n")
    # return driver

def get_large_img_url(page_url = '', tag_str = ''):
    global next_page_exist
    global driver
    page_url = page_url
    try:
        driver.get(page_url) #获取页面
        time.sleep(time_min)
        #模拟页面滚动
        for i in range(ranges):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(time_min)  #下拉等待刷新时间
        time.sleep(time_max)   #页底等待刷新时间
    except:
        print("网页打开失败！\n")
    #解析页面资源，得到图片id和large_img网址
    # page = driver.page_source
    # print(etree.parse(page.encode('utf-8', 'ignore'), etree.HTMLParser()))
    li_list = driver.find_elements_by_xpath(".//li[@style='width: 170px;']")
    # print(len(li_list))
    if len(li_list) == 0:
        next_page_exist += 1
    else:
        next_page_exist = 0
    for li in li_list:
        try:  #将大图原网址加入下载队列
            img_url = li.find_element_by_xpath(".//a[@class='directlink smallimg']").get_attribute('href')
            print("li_list", img_url)
            url_dic['img_url_due'].put(img_url)
        except:
            try:
                img_url = li.find_element_by_xpath(".//a[@class='directlink largeimg']").get_attribute('href')
                print("li_list", img_url)
                url_dic['img_url_due'].put(img_url)
            except:
                print("该元素没有图...")
        try:  #
            id_ = li.get_attribute('id')
            print("id: ", id_)
            url_dic['id_que'].put(id_)
            url_dic['tag_name'].put(tag_str)
        except:
            print("id不存在 ")
    print('解析页下载队列大小：{0}   {1}  {2}'.format(url_dic['img_url_due']._qsize(), url_dic['id_que']._qsize(), url_dic['tag_name']._qsize()))
    print("\t\t\tCoder::星纪弥航::github-->https://github.com/WLiangJun\n")

def set_path(download_path = '', sub_dir = ''):
    if "order:vote" in sub_dir:
        sub_dir = "我的收藏"
    if not os.path.exists(download_path):
        os.makedirs(download_path)  #创建konachan的下载根目录
    sub_dir = re.sub('[/\:,*?"<>|]', '', sub_dir)
    path_dir = download_path + "\\" + sub_dir
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
        print("{0}下载路径创建成功".format(path_dir))
    os.chdir(path_dir)

def download_large(pic_list = [], tag = ""):  #url_dic = {'img_url_due': Queue(maxsize=0), 'id_que': Queue(maxsize=0), 'tag_name': Queue(maxsize=0)}
    # print("进入多线程下载函数")
    # time.sleep(2*(time_min + time_max))
    global break_num_rec
    while not (url_dic['img_url_due'].empty()):
        # time.sleep(0.3)
        tar_url = url_dic['img_url_due'].get()
        pic_name = url_dic['id_que'].get()
        sub_dir = url_dic['tag_name'].get()
        # set_path(download_path, sub_dir)  #设置当前下载路径
        if ".jpg" in tar_url:
            format_pic = "jpg"
        else:
            format_pic = "png"
        # print("tag:", tag)
        if "order:vote" in tag:
            tag = "我的收藏"
        # if "order:vote" in tag:
        #     tag = "我的收藏"
        art_file = re.sub('[/\:,*?"<>|]', '', tag)
        if "{0}.{1}".format(pic_name, format_pic) in pic_list:
            break_num_rec = break_num_rec + 1
            print("{0}.{1} 文件存在在picture_list已有下载记录，跳过下载...".format(pic_name, format_pic))
        elif os.path.exists("{0}.{1}".format(pic_name, format_pic)):
            break_num_rec = break_num_rec + 1
            print("{0}.{1} 文件存在，跳过下载...".format(pic_name, format_pic))
            with open("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file), 'a') as pic_list_write:
                pic_list_write.write("{0}.{1}\n".format(pic_name, format_pic))
        else:
            break_num_rec = 0
            number = 0
            while True:
                try:
                    response = se.get(tar_url, stream=True, verify=False)   #必须要有stream控制，才能显示下载流进度
                    print("response status: ", response.status_code)
                    break
                except:
                    number += 1
                    if number == 50:
                        print("请求失败50次...")
                        break
                    print("请求失败...")
            chunk_size = 1024 #每次最大请求字节数
            content_size = int(response.headers['content-length']) #获得最大请求字节
            data_count = 0
            with open("{0}.{1}".format(pic_name, format_pic), 'ab') as konanchan_pic:
                try:
                    for data in response.iter_content(chunk_size=chunk_size):  # 一块一块下载
                        konanchan_pic.write(data)
                        konanchan_pic.flush()
                        data_count = data_count + len(data)
                        #下载进度条显示
                        now = int(50*data_count / content_size)  # 计算下载进度
                        # print("当前进度",now)
                        sys.stdout.write("\r[%s%s] %d%%" % ('⬛' * now, ' '*(50 - now), 100 * data_count / content_size))
                        sys.stdout.flush()
                        # print("\r下载进度：： %d%%(%.2f/%.2f)" % (now, data_count / 1024, content_size / 1024), end="")  # \r是防止多次打印
                    print("\n")
                    if now == 50:
                        # print("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file))
                        with open("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file), 'a') as pic_list_write:
                            pic_list_write.write("{0}.{1}\n".format(pic_name, format_pic))
                        print("\n下载成功::{0} ".format(tar_url))
                        print("文件名：\t{0}".format(pic_name))
                except:
                    print(" ")
                    print("下载流不完整不写入下载历史...")
                    print("number_stream:", now)
                    url_dic['img_url_due'].put(tar_url)
                    url_dic['id_que'].put(pic_name)
                    url_dic['tag_name'].put(sub_dir)
                    if os.path.exists("{0}.{1}".format(pic_name, format_pic)):
                        konanchan_pic.close()
                        os.remove("{0}.{1}".format(pic_name, format_pic))
                        print(" ")
                        print("已删除破损文件：\t{0}".format(pic_name))
            if not download_fluency_control == 0:
                time.sleep(download_fluency_control)   #控制服务器请求频率
# driver.quit()

def ini_config_read():
    dic = {}
    ID = []
    try:
        with open(os.getcwd() + "\\Kanachan" + "\\config.json", 'r',encoding='utf8') as conf:
            conf = conf.read().replace('\\', '\\\\')
            print("conf:", conf)
            dic = json.loads(conf)
    except:
        print("config.json 文件打开失败，请确认文件是否存在...")
    try:
        with open(os.getcwd() + "\\Kanachan" + "\\tag_list.txt", 'r') as ID_f:
            for line in ID_f:
                lines = str(line.strip())
                try:
                    ID.append(lines)  #只选取画师id
                except:
                    pass
    except:
        print("画师ID.txt 文件打开失败，请确认文件是否存在...")
    return dic, ID

def Kana_main():
    global auto_break, auto_break_picNum_exist, break_num_rec,download_fluency_control,google_data_path, auto_break_picNum_exist, auto_break, break_num_rec, download_path, next_page_exist, pic_list, driver
    global headless, load_img
    con_dic, tag_list = ini_config_read()
    download_fluency_control = con_dic['download_fluency_control']
    download_path = con_dic['download_dir']
    google_data_path = con_dic['google_data_path']
    if str(con_dic["auto_break"]) == "True":
        auto_break = True
    else:
        auto_break = False
    if con_dic["headless"] == "True":
        headless = True
    if con_dic["load_img"] == "False":  # 不加载图
        load_img = False
    auto_break_picNum_exist = int(con_dic["auto_break_picNum_exist"])
    print("auto_break:  ", auto_break)
    print("auto_break_picNum_exist:  ", auto_break_picNum_exist)
    Google_Driver()
    print("con_dic: ", con_dic)
    print("tags_list: ", tag_list)
    for tag in tag_list:
        break_num_rec = 0
        art_file = re.sub('[/\:,*?"<>|]', '', tag)
        if "ordervote" in art_file:
            art_file = "我的收藏"
        set_path(download_path, tag)
        next_page_exist = 0
        pic_list = []
        if os.path.exists("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file)):  # 读取下载过的文件列表
            with open("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file), 'r') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
                print("下载列表读取成功...")
        # thread_1 = threading.Thread(target=download_large())
        # thread_1.start()
        # while True:
        #     download_large()
        if con_dic['page_num'] > 1:
            i = con_dic['page_num'] - 1
        else:
            i = 0
        while next_page_exist <= 3:
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("break_num_rec=", break_num_rec)
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            if next_page_exist <= 3:
                i = i + 1
                print("正在解析 {0} 第 {1}页...".format(tag, i))  #
                url_page = "https://konachan.net/post?page=" + str(i) + "&tags=" + tag
                get_large_img_url(url_page, tag)
                download_large(pic_list, tag)
        # with open("{0}\\{1}\\{2}_picture_list_1.txt".format(download_path, tag, tag), 'w') as pic_list_write:
        #     for pic in pic_list:
        #         pic_list_write.write(pic+"\n")

    driver.quit()

if  __name__ == '__main__':
    # global auto_break, auto_break_picNum_exist, break_num_rec
    con_dic, tag_list = ini_config_read()
    download_fluency_control = con_dic['download_fluency_control']
    download_path = con_dic['download_dir']
    google_data_path = con_dic['google_data_path']
    if str(con_dic["auto_break"]) == "True":
        auto_break = True
    else:
        auto_break = False
    auto_break_picNum_exist = int(con_dic["auto_break_picNum_exist"])
    print("auto_break:  ", auto_break)
    print("auto_break_picNum_exist:  ", auto_break_picNum_exist)
    Google_Driver()
    print("con_dic: ", con_dic)
    print("tags_list: ", tag_list)
    for tag in tag_list:
        break_num_rec = 0
        art_file = re.sub('[/\:,*?"<>|]', '', tag)
        if "ordervote" in art_file:
            art_file = "我的收藏"
        set_path(download_path, tag)
        next_page_exist = 0
        pic_list = []
        if os.path.exists("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file)):  #读取下载过的文件列表
            with open("{0}\\{1}\\{2}_picture_list.txt".format(download_path, art_file, art_file), 'r') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
                print("下载列表读取成功...")
        # thread_1 = threading.Thread(target=download_large())
        # thread_1.start()
        # while True:
        #     download_large()
        if con_dic['page_num'] > 1:
            i = con_dic['page_num'] - 1
        else:
            i = 0
        while next_page_exist <= 3:
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("break_num_rec=", break_num_rec)
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            if next_page_exist <= 3:
                i = i + 1
                print("正在解析 {0} 第 {1}页...".format(tag, i))  #
                url_page = "https://konachan.net/post?page=" + str(i) + "&tags=" + tag
                get_large_img_url(url_page, tag)
                download_large(pic_list, tag)
        # with open("{0}\\{1}\\{2}_picture_list_1.txt".format(download_path, tag, tag), 'w') as pic_list_write:
        #     for pic in pic_list:
        #         pic_list_write.write(pic+"\n")

    driver.quit()