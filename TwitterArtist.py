#_*_coding=utf-8_*_
# coding:utf-8
# python 3.7
# kotori  QQ:450072402   微信：WLJ_450072402
# Twitter爬虫

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from requests import Session
import time
import os
import re
from queue import Queue
import json
import jsonlines
import logging  #保证session.get()  verify=False条件下不报警告
import sys

logging.captureWarnings(True)
# os.environ['NO_PROXY'] = 'stackoverflow.com'  # 解决requests.exceptions.ProxyError:


global driver, se, time_min, time_wait, ranges, download_path, is_over, next_page_exist, google_data_path, download_fluency_control, times,download_path_art,proxies
global url_dic, pic_list, retry, twitter_url, scroll_sum, img_list1, img_list2, time_out, time_out_add, headless, loop_times, load_img, handles, twitter_handle
global clear_handle, xpath_div
se = Session()
# se.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
# se.trust_env = False
se.keep_alive = False
proxies = {"http": "coffee.dynamic.138576.xyz:30080", "https": "coffee.dynamic.138576.xyz:30080"}
#全局变量初始化
ranges = 2  #存放页面下翻次数
time_wait = 1
time_min = 1
retry = 1
scroll_sum = 0
times = 1
headless = False
# download_path = "E:\\多媒体\\konachan"
is_over = False  #标记当次img是否已经查询完
next_page_exist = 0
# google_data_path = "C:\\Users\\Mimikko\\AppData\\Local\\Google\\Chrome\\User Data"
download_fluency_control = 0
twitter_url = ''
img_list2 = []
img_list1 = []
time_out = 10
time_out_add = 0.33
loop_times = 0
load_img = True
handles = None
twitter_handle = None
clear_handle = None
likes_values = 500
auto_break = True  # 自动跳出下载
auto_break_picNum_exist = 10  # 100个下载记录退出下载
break_num_rec = 0
xpath_div="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-1mi0q7o"  # twitter爬取字符串

url_dic = {'img_url_que': Queue(maxsize=0), 'img_url_list': [], 'format_pic': Queue(maxsize=0), 'artist_name': Queue(maxsize=0),'name_pic': Queue(maxsize=0)}
pic_list = []

headers = {
            'Referer': 'https://twitter.com/yuemengxi/likes?',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Connection':'close'  #1.防服务器报错一：：：：防止服务器443错误， 超过允许连接数量  貌似无效
        }

def Google_Driver(twitter_url = '', refresh=False, First=False):
    #配置谷歌路径信息，免登录
    global driver, headless, handles, twitter_handle, clear_handle
    if refresh == False:
        if First == True:  # 首次启动
            chrome_options = webdriver.ChromeOptions()
            # 解决selenium timeout连接
            chrome_options.add_argument("service_args=['–ignore-ssl-errors=true', '–ssl-protocol=TLSv1']")
            # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            # print("headless=", headless)
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
            chrome_options.add_argument("user-data-dir=" + google_data_path)
            try:
                driver = webdriver.Chrome(chrome_options=chrome_options)  #这里配合登录谷歌
            except:
                print("请求失败，请检查chrome是否关闭！\n")
        driver.get(twitter_url)  #"chrome://settings/clearBrowserData"
        while True:
            if not driver.title == "twitter.com":
                break
            # time.sleep(10)
            driver.refresh()
            time.sleep(time_wait / 2)
            print("标题：", driver.title)
        # return driver
    else:  # 处理加载后无数据的情形
        print("处理加载后无数据的情形...")
        while True:
            driver.refresh()
            time.sleep(time_wait)
            if not driver.title == "twitter.com":
                break

def clear_cache():
    # js = "window.open('http://www.sogou.com', encoding='utf8')"
    # driver.execute_script(js)
    # time.sleep(1.5)
    # twitter_handle = driver.current_window_handle  # 获取clear窗口句柄
    # # driver.find_elment_by_css_selector("body").sendKeys(Keys.CONTROL + "t");
    # driver.find_element_by_css_selector('body').send_keys(Keys.CONTROL, 't')
    # time.sleep(1.5)
    # handles = driver.window_handles  # 获取所有窗口 列表
    # print("获取twitter_handle、clear_handle窗口句柄:", handles)
    # driver.switch_to.window(handles[1])
    # driver.get("chrome://settings/clearBrowserData")
    # print("twitter窗口句柄：", twitter_handle)
    # # print("clear窗口句柄：", clear_handle)
    # time.sleep(time_wait)
    # # 点击清除数据
    # # clear_button = driver.find_element_by_id('clearBrowsingDataConfirm')
    # button = driver.find_elements_by_xpath(".//div[@slot='button-container']")
    # for clear_b in button:
    #     print(".......................")
    #     print("button text:", clear_b.text)
    #     clear_button = clear_b.find_elements_by_xpath(".//cr-button[@id='clearBrowsingDataConfirm']")
    #     clear_button.click()
    #     try:
    #         print("button text:", clear_b.text)
    #         clear_button = clear_b.find_elements_by_xpath(".//cr-button[@id='clearBrowsingDataConfirm']")
    #         clear_button.click()
    #     except:
    #         pass
    #
    # driver.close()  # 关闭清除内存窗口
    # driver.switch_to.window(twitter_handle)  # 切换回twitter窗口
    # time.sleep(10)
    pass

def scroll(div_list = [], refresh = False, speed = False):
    global driver,xpath_div
    global ranges, scroll_sum, download_path, next_page_exist, loop_times, break_num_rec, times
    print("break_num_rec=",break_num_rec)
    # 模拟页面滚动
    # if range_num == 0:
    if (speed == True) and not(pic_list.__len__() == 0):   # 快速定位到之前下载的位置， 结合之后添加的自动判断后续内容已下载
        num = 0
        print("正在快速更新下载位置请耐心等待...")
        while True:
            temp_list = []
            try:
                div_list = driver.find_elements_by_xpath(
                    ".//div[@class='{0}']".format(xpath_div))  #'css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-5f2r5o r-1mi0q7o'
                for div in div_list:
                    url = div.find_elements_by_xpath(".//img[@alt='图像']")
                    for img in url:
                        img_url = img.get_attribute('src')
                        if "format=png&name=" in img_url:
                            head, sep, tail = img_url.partition("format=png&name=")
                        if "format=jpg&name=" in img_url:
                            head, sep, tail = img_url.partition("format=jpg&name=")
                        img_url = head + sep + "4096x4096"
                        temp_list.append(img_url)
                        # print("再检查img_url:", img_url)
                        if not (img_url == '') and not (img_url in pic_list):
                            print("下载链接未在历史列表：", img_url)
                            print("刷新成功，跳出scroll...")
                            for i in range(8):  # 往上翻页模拟点击重试  再下翻，模拟重试
                                ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
                            time.sleep(time_wait)
                            return  # 跳出下拉函数
                if temp_list.__len__() == 0:  # 说明加载成功但没有成功加载内容
                    print("说明加载成功但没有成功加载内容...")
                    Google_Driver(refresh=True)
            except:
                pass

            loop_times += 1
            if not (loop_times == 0) and (loop_times % 2 == 0):  # 清理缓存
                clear_cache()

            if num and (num % 10 == 0):  # 10次page_up预防页面卡死
                print("正在快速更新下载位置，请耐心等待...")
                for k in range(3): # 往上翻页模拟点击重试  再下翻，模拟重试
                    ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
                    time.sleep(0.3)
                for i in range(8):  # 往上翻页模拟点击重试  再下翻，模拟重试
                    ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(0.3)
                time.sleep(1.5)
            for i in range(8):
                ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                # print("ranges=", ranges)
            time.sleep(1.5)  # 下拉等待刷新时间
            num += 1  #每10次page_up
    elif refresh == False:  # 正常下拉页面
        for i in range(ranges):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            # print("ranges=", ranges)
        time.sleep(time_wait)  # 下拉等待刷新时间
        loop_times += 1
        if not (loop_times == 0) and (loop_times % 2 == 0):  # 清理缓存
            clear_cache()
    else:
        print("再请求失败，即将重试下拉刷新...")
        # print("刷新前的队列：",div_list)  # chrome://settings/clearBrowserData
        if url_dic["img_url_list"].__len__() == 0:
            Google_Driver(refresh=True)
        num = 0
        fail_num = 0
        while True:
            for i in range(3):  # 往上翻页模拟点击重试  再下翻，模拟重试
                ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
            time.sleep(0.3)
            for i in range(6):  # 往上翻页模拟点击重试  再下翻，模拟重试
                ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(time_wait)

            num += 1
            print("完成{0}模拟操作...".format(num))
            # if (num >= 3):
            #     print("模拟操作超过阈值，退出...", times)
            #     return
            # try:
            div_list = driver.find_elements_by_xpath(".//div[@class='{0}']".format(xpath_div))   #'css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-5f2r5o r-1mi0q7o'
            for div in div_list:
                url = div.find_elements_by_xpath(".//img[@alt='图像']")
                print(".//img[@alt='图像", url)
                if url == [] or url.__len__() == 0:  # times次模拟自动退出
                    print("url为空......., url:", url)
                    fail_num += 1
                    if fail_num == 20:
                        print("fail_num 001:", fail_num)
                        return
                for img in url:
                    img_url = img.get_attribute('src')
                    if "format=png&name=" in img_url:
                        head, sep, tail = img_url.partition("format=png&name=")
                    if "format=jpg&name=" in img_url:
                        head, sep, tail = img_url.partition("format=jpg&name=")
                    img_url = head + sep + "4096x4096"
                    print("再检查img_url:", img_url)
                    if not(img_url == '') and not(img_url in url_dic["img_url_list"]):
                        print("未在列表的下载链接：", img_url)
                        print("刷新成功，跳出scroll...")
                        return #跳出下拉函数
                    else:  # 防止结束后无限循环
                        fail_num += 1
                        if fail_num == 10:
                            print("fail_num 002:", fail_num)
                            return
            # except:
            #     fail_num += 1
            #     if fail_num == 20:
            #         print("fail_num 003:", fail_num)
            #         return
            #     print("")
            #     pass

def get_large_img_url(tag_str = '', Artist=''):
    """获取下载图片原始链接和作者名"""
    global next_page_exist, scroll_sum, img_list1, img_list2, xpath_div
    global driver, likeTable, like_num
    print("Artist:", Artist)
    #解析页面资源，得到图片id和large_img网址
    #查找元素后返回一个Webelement对象
    img_list_temp = []  #用于页面刷新后的恢复  css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-1mi0q7o
    div_list = driver.find_elements_by_xpath(".//div[@class='{0}']".format(xpath_div))  # 每次失效后改这里就行
    for div in div_list:
        #  re.sub('[/\:,*?"<>|]', '', driver.title.strip(" - pixiv"))
        # try:
        artistDiv = div.find_element_by_xpath(".//div[@class='css-901oao css-bfa6kz r-111h2gw r-18u37iz r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-qvutc0']")
        artist = artistDiv.find_element_by_xpath(
            ".//span[@class='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0']").text  # 获取该推文的作者
        artist = re.sub('[/\:,*?"<>|@]', '', artist.strip().replace("\n", ""))  # 防止建文件夹失败
        if artist == '':
            artist = Artist
        print("作者：--->{0}<---".format(artist))  # 已验证是统一整体
        url = div.find_elements_by_xpath(".//img[@alt='图像']")
        likeDiv = div.find_element_by_xpath(".//div[@class='css-1dbjc4n r-18u37iz r-1wtj0ep r-156q2ks r-1mdbhws']")
        likeDivs = likeDiv.find_elements_by_xpath(
            ".//span[@class='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0']")
        areLike = False
        likeTable = likeDiv.get_attribute("aria-label").split(",")
        print("aria-label:::", likeTable)
        # if "已喜欢" in likeTable:
        #     areLike = True
        #     print("该推特已经加入likes")
        i = 0
        for ele in likeTable:
            if ("喜欢" in ele) and (not "已喜欢" in ele):
                likes_number_str = str(ele).replace(" ", "").replace("喜欢", "")
                like_num = int(likes_number_str)
                print("点赞喜欢数值：", like_num)
            if "已喜欢" in ele:
                areLike = True
                print("该推特已经加入likes")
        print("like table:aria-label:", likeTable)
        # for likeEle in likeDivs:
        #     if i == 2:
        #         like_num_str = str(likeEle.text).replace(',', '')
        #     i += 1
        # if '万' in like_num_str:
        #     like_num_str = like_num_str.replace('万', '')
        #     like_num = int(float(like_num_str) * 10000)
        # else:
        #     like_num = int(like_num_str)
        print("likes number：", like_num)

        #     pass
        # except:
        #     print("未找到推文...")
        #     pass
        format_pic = ''
        # try:
        for img in url:
            img_url = img.get_attribute('src')  #url_dic = {'img_url_que': Queue(maxsize=0), 'img_url_list': [], 'id_que': Queue(maxsize=0), 'artist_name': Queue(maxsize=0)}
            if "format=png&name=" in img_url:
                head, sep, tail = img_url.partition("format=png&name=")
                format_pic = 'png'
            if "format=jpg&name=" in img_url:
                head, sep, tail = img_url.partition("format=jpg&name=")
                format_pic = 'jpg'
            img_url = head + sep + "4096x4096"
            if (like_num >= likes_values) or (areLike==True):
                if not img_url in url_dic["img_url_list"]:
                    url_dic["img_url_que"].put(img_url)
                    url_dic["img_url_list"].append(img_url)
                    url_dic["artist_name"].put(artist)
                    url_dic["format_pic"].put(format_pic)
                    name_pic = re.sub('[/\:,*?"<>|]', '', head.strip().replace("https://pbs.twimg.com/media/", ""))
                    url_dic["name_pic"].put(name_pic)
                    img_list_temp.append(img_url)
                    # print("are like  ？", areLike)
                    print("imag_url:", img_url)
                    print("图片格式：{0} 图片名称：{1}".format(format_pic, name_pic))
        # except:
        #     print("图像解析错误...")
        #     pass
    if not img_list_temp.__len__() == 0:
        img_list1 = img_list2
        img_list2 = img_list_temp
        next_page_exist = 0
        print("重置下载队列更新数据： 0")
        # print("img_list1", img_list1)
        # print("img_list2", img_list2)
    else:
        next_page_exist += 1
        print("下载队列已连续{0}次未更新下载队列...".format(next_page_exist))
    if next_page_exist > retry:  #False代表入队列的元素数量为0,自动刷新页面
        scroll(div_list=img_list1, refresh=True)
    if img_list_temp.__len__():
        print("\tCoder::星纪弥航::github-->https://github.com/WLiangJun\n")

def set_download_path(download_path = '', sub_dir = ''):
    if not os.path.exists(download_path):
        os.makedirs(download_path)  #创建konachan的下载根目录
    path_dir = download_path + "\\" + sub_dir
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
        print("{0}下载路径创建成功".format(path_dir))
    print("图片下载路径：", path_dir)
    os.chdir(path_dir)

def set_twitter_path(download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)  #创建konachan的下载根目录
    os.chdir(download_path)   #切换至twitter根路径

def download_large(thread = False):  #url_dic = {'img_url_que': Queue(maxsize=0), 'id_que': Queue(maxsize=0), 'tag_name': Queue(maxsize=0)}
    # print("进入多线程下载函数")
    # response = se.get(img_url, headers=self.headers, stream=True, verify=False, headers=headers, timeout=(time_out,time_out_add))
    # time.sleep(2*(time_min + time_wait))
    print("进行下载...")
    global se, time_min, time_wait, ranges, headers, time_out, time_out_add, url_dic, break_num_rec
    print("time_out = ", time_out)
    while not (url_dic['img_url_que'].empty()):
        # time.sleep(0.3)
        # url_dic = {'img_url_que': Queue(maxsize=0), 'img_url_list': [], 'format_pic': Queue(maxsize=0), 'artist_name': Queue(maxsize=0),'name_pic': Queue(maxsize=0)}
        tar_url = url_dic['img_url_que'].get()  #原图网址
        artist_name = url_dic['artist_name'].get()  #作者、图片名称，用于存放路径区分
        pic_name = url_dic['name_pic'].get()
        set_download_path(download_path)  #设置当前下载路径
        format_pic = url_dic['format_pic'].get()
        # print("队列中获取数据结束...")
        if tar_url in pic_list:  #检查该链接是否已经有过下载
            break_num_rec = break_num_rec + 1
            print("{0} 文件存在在picture_url_list已有下载记录，跳过下载...".format(tar_url))
        # elif os.path.exists("{0}\\{1}.{2}".format(artist_name, pic_name, format_pic)):   # 包含很多未下载完全的文件，因此暂时注释掉
        #     print("{0}.{1} 文件存在，跳过下载...".format(pic_name, format_pic))
        #     with open("{0}\\picture_url_list.txt".format(download_path_art), 'a', encoding='utf8') as pic_list_write:
        #         pic_list_write.write("{0}\n".format(tar_url))
        else:
            print("requests", tar_url)
            break_num_rec = 0
            print("识别以前未下载的图片：  break_num_rec = ", break_num_rec)
            # response = se.get(tar_url, stream=True, verify=False, headers=headers)  # 必须要有stream控制，才能显示下载流进度  , headers=headers
            # response = se.get(tar_url, stream=True, verify=False, headers=headers, timeout=time_out)
            # print("status: ", response.status_code)
            successRes = False
            try:
                # print("尝试请求服务器...")
                # response = se.get(tar_url, stream=True, verify=False, headers=headers)   # , timeout=(time_out, time_out_add), proxies=proxies 正常：：必须要有stream控制，才能显示下载流进度  , headers=headers
                response = se.get(tar_url, stream=True, verify=False, headers=headers, timeout=time_out)   # , timeout=(time_out, time_out_add), proxies=proxies 必须要有stream控制，才能显示下载流进度  , headers=headers
                successRes = True
                print("status: ", response.status_code)
            except:
                # print("requests失败...")
                print("requests失败，将再尝试{0}次请求...".format(retry))
                retry_num = 0
                while True:
                    try:
                        retry_num += 1
                        # response = se.get(tar_url, stream=True, verify=False, headers=headers)  # , proxies=proxies,timeout=(time_out, time_out_add)  正常：：必须要有stream控制，才能显示下载流进度  , headers=headers
                        response = se.get(tar_url, stream=True, verify=False, headers=headers, timeout=time_out)  # , proxies=proxies, timeout=(time_out, time_out_add)必须要有stream控制，才能显示下载流进度  , headers=headers
                        response_statu = response.status_code
                        successRes = True
                        time.sleep(2)
                        # print("try--->status:{0} retry_num: {1}".format(response_statu, retry_num))
                    except:
                        response_statu = 555
                        time.sleep(2)
                        # print("except--->status:{0} retry_num: {1}".format(response_statu, retry_num))
                    if response_statu == 200:
                        successRes = True
                        print("已请求成功... response status:{0}  {1}".format(response_statu, retry_num))
                        break
                    if retry_num == retry:   # retry次后都失败就压入下载队列，换个时间段继续下载
                        url_dic['img_url_que'].put(tar_url)  # 原图网址
                        url_dic['artist_name'].put(artist_name)  # 作者、图片名称，用于存放路径区分
                        url_dic['name_pic'].put(pic_name)
                        url_dic['format_pic'].put(format_pic)
                        print("{0}次服务器连接均失败...".format(retry_num))
                        break
            # print("response status: ", response.status_code)
            if successRes == True:
                chunk_size = 1024 #每次最大请求字节数
                content_size = float(response.headers['content-length']) #获得最大请求字节
                data_count = 0
                set_download_path(download_path=download_path, sub_dir=artist_name)
                # os.chdir(download_path + "\\" + artist_name)
                if os.path.exists("{0}.{1}".format(pic_name, format_pic)):
                    print("delete: {0}.{1}".format(pic_name, format_pic))
                    os.remove("{0}.{1}".format(pic_name, format_pic))
                print("当前下载路径：", os.getcwd())
                print("download_path={0}, sub_dir={1}".format(download_path, artist_name))
                with open("{0}.{1}".format(pic_name, format_pic), 'ab') as twitter_pic:
                    try:
                        for data in response.iter_content(chunk_size=chunk_size):  # 一块一块下载，后期考虑中途下载失败后的重试
                            twitter_pic.write(data)
                            twitter_pic.flush()
                            data_count = data_count + len(data)
                            #下载进度条显示
                            now = int(30*data_count / content_size)  # 计算下载进度
                            # print("当前进度",now)
                            sys.stdout.write("\r[%s%s] %d%%" % ('⬛' * now, ' '*(30 - now), 100 * data_count / content_size))
                            sys.stdout.flush()
                            # print("进度文件大小： {0}   当前下载大小： {1}".format(content_size, data_count))
                            # print("\r下载进度：： %d%%(%.2f/%.2f)" % (now, data_count / 1024, content_size / 1024), end="")  # \r是防止多次打印
                        print("\n下载成功::{0} \n".format(tar_url))
                        with open("{0}\\picture_url_list.txt".format(download_path_art), 'a',
                                  encoding='utf8') as pic_list_write:
                            pic_list_write.write("{0}\n".format(tar_url))
                    except:
                        print("下载流异常，可能由于服务器响应时间过长，重新加入下载队列...")
                        url_dic['img_url_que'].put(tar_url)  # 原图网址
                        url_dic['artist_name'].put(artist_name)  # 作者、图片名称，用于存放路径区分
                        url_dic['name_pic'].put(pic_name)
                        url_dic['format_pic'].put(format_pic)
                    print("文件大小： {0}   当前下载大小： {1}".format(content_size, data_count))
                if not download_fluency_control == 0:
                    time.sleep(download_fluency_control)   #控制服务器请求频率
        # print("下载队列是否为空： ", url_dic['img_url_que'].empty())
    print("下载队列长度： ", url_dic['img_url_list'].__len__())
    # print("该队列下载结束...")
    return False

# driver.quit()

def ini_config_read():
    dic = {}
    ID = []
    try:
        with open(os.getcwd() + "\\Twitter" + "\\config.json", 'r', encoding='utf8') as conf:
            dic = json.load(conf)
    except:
        print("config.json 文件打开失败，请确认文件是否存在...")
    try:
        with open(os.getcwd() + "\\Twitter" + "\\tag_list.txt", 'r', encoding='utf8') as ID_f:
            for line in ID_f:
                lines = str(line.strip())
                try:
                    ID.append(lines)  #只选取画师id
                except:
                    pass
    except:
        print("画师ID.txt 文件打开失败，请确认文件是否存在...")

    return dic, ID

def load_pic_list(download_path_art=''):
    pic_list = []
    try:
        with open("{0}\\picture_url_list.txt".format(download_path_art), 'r', encoding='utf8') as pic_file:
            for line in pic_list:
                pic_list.append(line.strip())
    except:
        print("{0}\\picture_url_list.txt  文件不存在，您是否有下载历史...".format(download_path_art))
    return pic_list

def para_ini(con_dic):
    global download_path, google_data_path, twitter_url, ranges, times, time_min, scroll_sum, time_wait, retry, time_out, time_out_add
    global download_fluency_control, headless, load_img, auto_break, auto_break_picNum_exist, xpath_div
    download_path = con_dic['download_dir']
    google_data_path = con_dic['google_data_path']
    twitter_url = con_dic['twitter_url']  # 下载收藏网址
    ranges = int(con_dic['range_num'])
    time_wait = int(con_dic["time_wait"])
    time_min = int(con_dic["time_min"])
    retry = int(con_dic["retry"])
    times = int(con_dic["times"])
    time_out = int(con_dic["time_out"])
    time_out_add = time_out+int(con_dic["time_out_add"])
    download_fluency_control = int(con_dic["download_fluency_control"])
    xpath_div = con_dic['xpath_div']
    if (str(con_dic["auto_break"]) == "True"):
        auto_break = True
    else:
        auto_break = False
    auto_break_picNum_exist = int(con_dic["auto_break_picNum_exist"])
    print("auto_break:  ", auto_break)
    print("auto_break_picNum_exist:  ", auto_break_picNum_exist)
    if con_dic["headless"] == "True":
        headless = True
    if con_dic["load_img"] == "False":  # 不加载图
        load_img = False
    if os.path.exists("{0}\\poll_num.txt".format(download_path)):  # 读取下载过的文件列表
        with open("{0}\\poll_num.txt".format(download_path), 'r', encoding='utf8') as poll_file:
            for line in poll_file:
                scroll_sum = int(line.strip())

def Twit_main():
    global download_path_art, artList, break_num_rec, next_page_exist, pic_list, auto_break_picNum_exist, auto_break, headless, load_img, likes_values, times, driver
    print("\tCoder1::星纪弥航::github-->https://github.com/WLiangJun\n")
    artList = []
    # a={"artist": "HitenKei", "likesNum": 1000}
    # b={"artist": "fuzichoco", "likesNum": 1000}
    # with jsonlines.open('Artist.json', 'w') as wF:
    #     jsonlines.Writer.write(wF, a)
    #     jsonlines.Writer.write(wF, b)
    #     wF.close()
    with open("Twitter\\"+'Artist.json', 'r', encoding='utf-8') as ArtistF:
        for art in jsonlines.Reader(ArtistF):
            artList.append(art)
        ArtistF.close()
    global driver
    con_dic, tag_list = ini_config_read()
    para_ini(con_dic)
    # pic_list = load_pic_list(download_path_art=download_path_art)  # 读取下载记录
    Google_Driver(twitter_url=twitter_url, First=True)
    time.sleep(3)
    # scroll(scroll_sum)
    # print("con_dic: ", con_dic)
    # print("tags_list: ", tag_list)

    # scroll(refresh=False)  # 滑屏操作
    for artist in artList:
        print("https://twitter.com/{0}/media".format(artist["artist"]))
        download_path_art = download_path + "\\" + str(artist["artist"])
        print(download_path_art)
    for artist in artList:
        break_num_rec = 0
        next_page_exist = 0  # 初始化
        download_path_art = download_path + "\\" + str(artist["artist"])
        if not os.path.isdir(download_path_art):
            os.mkdir(download_path_art)
            print("{0}  创建成功。".format(download_path_art))
        tag_list = "https://twitter.com/{0}/media".format(artist["artist"])
        print("爬取：", tag_list)
        headers['Referer'] = tag_list
        likes_values = int(artist["likesNum"])
        Google_Driver(tag_list, refresh=False)
        scroll(refresh=False, speed=False)  # 预先加载，滑屏操作加快速滑至历史下载页面
        print("画师media主页: ", tag_list)
        print("最低点赞次数: ", likes_values)
        if os.path.exists("{0}\\picture_url_list.txt".format(download_path_art)):  # 读取下载过的文件列表
            with open("{0}\\picture_url_list.txt".format(download_path_art), 'r', encoding='utf8') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
        while True:
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("break_num_rec=", break_num_rec)
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            if next_page_exist == times:  # 不断往下翻页, times次之后依然没有添加新下载，则下载完成
                print("已下载完成...")
                break
            get_large_img_url(Artist=artist["artist"])
            scroll(refresh=False)  # 滑屏操作
            while True:
                download = download_large()
                if download == False:  # 表示下载完
                    break
            print("break_num_rec=", break_num_rec)
        # input("按任意键爬取下一位画师...")
        print("爬取下一位画师...")
    print("连续 {0} 次之后下载队列依然未添加新元素，默认下载完成...".format(times))
    # input("请按任意键退出...:")
    driver.quit()

if  __name__ == '__main__':
    global download_path_art
    print("\tCoder1::星纪弥航::github-->https://github.com/WLiangJun\n")
    artList = []
    # a={"artist": "HitenKei", "likesNum": 1000}
    # b={"artist": "fuzichoco", "likesNum": 1000}
    # with jsonlines.open('Artist.json', 'w') as wF:
    #     jsonlines.Writer.write(wF, a)
    #     jsonlines.Writer.write(wF, b)
    #     wF.close()
    with open('Artist.json', 'r', encoding='utf-8') as ArtistF:
        for art in jsonlines.Reader(ArtistF):
            artList.append(art)
        ArtistF.close()
    global driver
    con_dic, tag_list = ini_config_read()
    para_ini(con_dic)
    # pic_list = load_pic_list(download_path_art=download_path_art)  # 读取下载记录
    Google_Driver(twitter_url=twitter_url,First=True)
    time.sleep(3)
    # scroll(scroll_sum)
    # print("con_dic: ", con_dic)
    # print("tags_list: ", tag_list)


    # scroll(refresh=False)  # 滑屏操作
    for artist in artList:
        print("https://twitter.com/{0}/media".format(artist["artist"]))
        download_path_art = download_path + "\\" + str(artist["artist"])
        print(download_path_art)
    for artist in artList:
        break_num_rec = 0
        next_page_exist = 0  # 初始化
        download_path_art = download_path + "\\" + str(artist["artist"])
        if not os.path.isdir(download_path_art):
            os.mkdir(download_path_art)
            print("{0}  创建成功。".format(download_path_art))
        tag_list = "https://twitter.com/{0}/media".format(artist["artist"])
        print("爬取：", tag_list)
        headers['Referer'] = tag_list
        likes_values = int(artist["likesNum"])
        Google_Driver(tag_list, refresh=False)
        scroll(refresh=False, speed=False)  # 预先加载，滑屏操作加快速滑至历史下载页面
        print("画师media主页: ", tag_list)
        print("最低点赞次数: ", likes_values)
        if os.path.exists("{0}\\picture_url_list.txt".format(download_path_art)):  # 读取下载过的文件列表
            with open("{0}\\picture_url_list.txt".format(download_path_art), 'r', encoding='utf8') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
        while True:
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("break_num_rec=",break_num_rec)
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            if next_page_exist == times:  #不断往下翻页, times次之后依然没有添加新下载，则下载完成
                print("已下载完成...")
                break
            get_large_img_url(Artist=artist["artist"])
            scroll(refresh=False)  # 滑屏操作
            while True:
                download = download_large()
                if download == False:  #表示下载完
                    break
        # input("按任意键爬取下一位画师...")
        print("爬取下一位画师...")
    print("连续 {0} 次之后下载队列依然未添加新元素，默认下载完成...".format(times))
    input("请按任意键退出...:")
    driver.quit()