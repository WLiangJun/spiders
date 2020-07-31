#!/user/bin/env python3
# -*- coding: utf-8 -*-
# python 3.7
# kotori  QQ:450072402   微信：WLJ_450072402
# Danbooru爬虫   标签爬虫

from selenium import webdriver
from lxml import etree
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from requests import session
import json
from requests.cookies import RequestsCookieJar
import os
import sys
import re
from queue import Queue
import gc   #garba collector 内存管理
import logging  #保证session.get()  verify=False条件下不报警告

logging.captureWarnings(True) #忽略警告
# reload(sys)
# sys.setdefaultencoding('utf8')

se = session()
se.keep_alive = False  #防止访问数量过多，服务器关闭请求  SSL443错误方法3：：：貌似有效
global jpg_success_num, png_success_num, fail_num, driver_exsit, C_Path
global driver, time_scroll,time_wait, time_out, time_out_add, range_num, retry_que, load_img, headless, retry_num
jpg_success_num = 0
png_success_num = 0
fail_num = 0
driver_exsit = False
C_Path = ''  #用于存放当前py所在路径   SSL报错解决方法二：：：失败
time_scroll = 1
time_wait = 2
time_out = 0.5
time_out_add = 1
range_num = 2
retry_que = 0
headless = False
load_img = True
retry_num = 5
auto_break = True
auto_break_picNum_exist = 10
break_num_rec = 0
pic_list = []

"""设置爬虫代理"""  # https://blog.csdn.net/haeasringnar/article/details/82558760
proxies = {  # https://mp.weixin.qq.com/s?src=3&timestamp=1595471991&ver=1&signature=n-gp1aFxXkxgaaHVj7qOHu0LC1V6FdlHikIV25sEAVxEfNZlYifnn2iGqhPeMc3-qTSlAdqtKXPTKmk5uEInnH8slYcWEpXlYLH7dQahIL76dpr1zbfbHUrKyo91eO8zNEXhcW1flyXgdZ1LoE1npdDVPJslobITvJnnyAiXAPE=
  "http": "http://127.0.0.1:3128",
  "https": "http://127.0.0.1:2080",
}

class Pixiv():
    artist_num = 0
    def __init__(self, dir = '', google_dir = '', ID =''):
        self.profile_dir = google_dir            #r'C:\Users\Mimikko\AppData\Local\Google\Chrome\User Data'  # Google数据保存地址  #谷歌路径
        # 设置Google数据位置，方便调用密码数据，避免登陆等
        self.base_url = 'https://www.pixiv.net'  #这里是很多超链接的前缀
        self.download_path = dir  #r'E:\多媒体\pyspider'
        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': 'close'  #1.防服务器报错一：：：：防止服务器443错误， 超过允许连接数量  貌似无效
        }
        self.tag_name = ID  #后通过循环进行赋值
        self.next_page_exist = True   #默认存在下一页
        self.target_url = ''
        self.pages = 1
        self.page_main = ''
        self.artistor_title = ''   #用于创建画集文件夹
        self.current_dir = ''
        self.url_dic = {'img_url_que': Queue(maxsize=0), 'Referer_url_que': Queue(maxsize=0), 'Page_num_que': Queue(maxsize=0), 'Page_num_list': []}
        if self.artist_num == 0:
            self.root_path()
            print("支持Google浏览器78版本及以上！！！\n")
            # print("\t测试全局变量：long_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
        self.picture_size = 0
        self.artist_num += 1
        self.picture_list = []
        self.failure_list = []
        self.retry_que = []  # 标记下载后失败的图片，避免死循环

    def get_art_url(self):
        self.target_url = r"https://www.pixiv.net/member_illust.php?id=" + self.tag_name

    def root_path(self):
        self.current_dir = os.getcwd()  #获取执行路径
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        os.chdir(self.download_path)
        print("图片下载目录:{0}...".format(self.download_path))
        print("配置文件存放地址：{}...".format(self.current_dir))

    def change_down_path(self, sub_dir):
        sub_dir = re.sub('[/\:,*?"<>|]', '', sub_dir)
        path_dir = self.download_path + "\\" + sub_dir
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
            print("{0} 存放路径创建成功...".format(path_dir))
        os.chdir(path_dir)

    def config_requests(self):
        #从Google获取cookies配置requests
        cookies = driver.get_cookies()
        # print("从se获取改变前的cookies:\n", se.cookies)
        with open(C_Path + "\\Danbooru" + r'\cookies.json', 'w') as fp:
            json.dump(cookies, fp)
        # try:
        #     with open(C_Path +"\\Danbooru" + r'\cookies.json', 'w') as fp:
        #         json.dump(cookies, fp)
        # except:
        #     print("从chrome cookies存放失败！\n")
        #这里用cookies对象进行处理
        jar = RequestsCookieJar()
        with open(C_Path + "\\Danbooru" + r'\cookies.json', 'r') as fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
        # try:
        #     jar = RequestsCookieJar()
        #     with open(C_Path +"\\Danbooru" + r'\cookies.json', 'r') as fp:
        #         cookies = json.load(fp)
        #         for cookie in cookies:
        #             jar.set(cookie['name'], cookie['value'])
        # except:
        #     print("cookies读取失败！\n")
        se.cookies = jar  #配置session
        # print("从se获取改变后的cookies:\n", se.cookies)

    def get_html(self):
        #获取第一页
        global driver
        if ":" in self.tag_name:  # 个人收藏标签
            self.target_url = "https://danbooru.donmai.us/posts?page=" + "1&tags=" + str(self.tag_name).replace(":", "%3A")
        else:
            self.target_url = "https://danbooru.donmai.us/posts?page=" + "1&tags=" + str(self.tag_name)
        while True:
            try:
                driver.get(self.target_url)  # 绕过有人机检查  anmi: https://www.pixiv.net/member_illust.php?id=212801   Hiten: 'https://www.pixiv.net/member_illust.php?id=490219'
                # self.pages += 1
                time.sleep(time_scroll)
                self.page_main = "https://danbooru.donmai.us/posts?page="
                if self.tag_name == "ordfav:surfur":
                    self.artistor_title = "我的收藏"
                else:
                    self.artistor_title = self.tag_name
                # self.artistor_title = re.sub('[/\:,*?"<>|]', '', driver.title.strip(" Art  Danbooru"))
                # print("driver.title", driver.title)
                if driver_exsit == False:
                    self.config_requests()
                    driver_exsit == True  #待cookies数据获得后将状态置为True：表浏览器已创建成功
            except:
                print("网页打开失败！\n")
            if driver.title != "danbooru.donmai.us":
                break
        print("解析主页title：\t{0}".format(self.artistor_title))
        # print("当前解析主页网址：\t{0}\n".format(self.page_main))  #将每位画师的首页存放在page_main中

    def get_img_ref_pageNum(self, num = 0, li_null = False):
        #打印检查 html = etree.HTML(text)
        # s = etree.tostring(html).decode()
        global driver
        # print("num1=",num)
        while True:
            # print("li_null=", li_null)
            if (driver.title == "https://danbooru.donmai.us/") or (li_null == True):
                driver.refresh()
                time.sleep(time_wait)
                # self.page_scroll(range_num, time_scroll)
                page_scroll(range_num, time_scroll)
                # print("num2=", num)
                li_null = False # 避免陷入死循环
            else:
                break
        # all_xml = dom.xpath("//ul[@class='_2WwRD0o _2WyzEUZ']")
        li_list = driver.find_elements_by_xpath("//div[@id='posts-container']//article")
        print("li_list.__len__(): ", li_list.__len__())
        for element in li_list:
            # print("li... \t", element.text)
            try:
                referer_url = element.find_element_by_xpath(".//a").get_attribute('href')   #好家伙居然把sc-fzXfQp bNPARF换掉了
                self.url_dic['Referer_url_que'].put(referer_url)  #入队列
                print("referer_url入队: ", referer_url)
            except:
                self.url_dic['Referer_url_que'].put("https://danbooru.donmai.us/")  # 入队列
                print("该li节点没有referer_url...")
                pass
        # print("num3=", num)
        ref_que_size = self.url_dic['Referer_url_que'].qsize()
        img_que_size = self.url_dic['img_url_que'].qsize()
        print("ref_que_size :{0}, img_que_size :{1}".format(ref_que_size, img_que_size))
        if (li_list.__len__() == 0) or (ref_que_size ==0):
            num += 1   # 获取为空，或不相等
            if num <= 5:
                print("页面没有抓取到信息、队列大小为0，进行{0}重新抓取".format(num))
                self.get_img_ref_pageNum(num=num, li_null=True)
        else:
            self.pages += 1
            # print("更改后的页数：\t{0}\n".format(self.pages))
        if num == 5:
            self.next_page_exist = False
            print("5次未获取到信息,默认没有下一页...")

        # print("all_xml_ul:\n", all_xml)

    def next_page(self):
        # print("页面跳转检查：\t{0}\n".format(self.pages))
        next_url = self.page_main + str(self.pages) + "&tags=" + (self.tag_name).replace(":", "%3A")
        # print("next_url:\t ", next_url)
        print("正在解析第 {0} 页...:".format(self.pages), next_url)
        driver.get(next_url)
        # self.pages += 1

    def url_full_page(self, pixiv):
        # print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun/PixivSpider")
        if self.pages == 1:
            self.get_html()  #访问首页
            artistor_title = re.sub('[/\:,*?"<>|]', '', self.artistor_title)
            if os.path.exists("{0}\\{1}\\{2}_picture_list.txt".format(self.download_path, artistor_title,
                                                                      artistor_title)):
                with open("{0}\\{1}\\{2}_picture_list.txt".format(self.download_path, artistor_title,
                                                                  artistor_title), 'r', encoding='utf8') as pic_list_read:
                    for line in pic_list_read:
                        self.picture_list.append(line.strip())  # 读取pictur_list
                print("图片下载列表读取成功...\n")
            else:
                print("图片下载列表为空...\n", self.picture_list)
                # print("读取列表：\n", self.picture_list)
        page_scroll(range_num, time_scroll)
        # self.get_pagesource()
        self.get_img_ref_pageNum()
        self.img_download_req(self.url_dic)  # 可开启多线程进行下载
        # self.get_img_url(self.get_pagesource())

    def get_multi_img(self, img_url, referer_url, pic_name):
        """通过第一步获取原图子页面，获取原图链接"""
        global jpg_success_num, png_success_num, retry_que, fail_num, break_num_rec
        img_url = str(img_url)
        img_url_source = img_url  #暂时保存jpg  url供master1200下载使用
        exsit_pic = False
        print("referer_url:", referer_url)
        # print("img_url:", img_url)
        if (referer_url in self.picture_list):
            exsit_pic = True
            # break_num_rec = break_num_rec + 1
            print("{0} 文件存在在picture_list已有下载记录，跳过下载...\n".format(pic_name))
        else:
            while True:
                try:
                    response = se.get(referer_url, headers=self.headers, stream=True, verify=False,
                                      timeout=(time_out, time_out_add))  # timeout=(time_out, time_out_add)
                    selector = etree.HTML(response.text)  # 将text转化成lxml
                    img_url = selector.xpath('//li[@id="post-info-size"]//a/@href')[0]
                    print("原图请求成功...")
                    break
                except:
                    print("原图请求失败，尝试再次请求...", referer_url)
            print("img_url 002", img_url)

            retry_res_num = 0
            break_num_rec = 0
            while True:  # 获取大图地址
                try:
                    response = se.get(referer_url, headers=self.headers, stream=True, verify=False,
                                      timeout=(time_out, time_out_add))  # timeout=(time_out, time_out_add)
                    selector = etree.HTML(response.text)  # 将text转化成lxml
                    img_url = selector.xpath('//li[@id="post-info-size"]//a/@href')[0]
                    print("原图请求成功，跳出循环...")
                    break
                except:
                    retry_res_num+=1
                    if retry_res_num >= 5:
                        img_url = "https://danbooru.donmai.us/"
                        if not (referer_url in self.retry_que):
                            self.retry_que.append(referer_url)
                            self.url_dic['Referer_url_que'].put(referer_url)
                            print("重新加入下载队列000：", referer_url)
                        print("原图请求50次失败，跳出循环...", referer_url)
                        break
                    print("原图请求失败，尝试再次请求...", referer_url)

            # try:  # 获取大图地址
            #     print("referer_url 001", referer_url)
            #     retry_res_num = 0
            #     while True:
            #         response = se.get(referer_url, headers=self.headers, stream=True, verify=False, timeout=(time_out, time_out_add))  # timeout=(time_out, time_out_add)
            #         if (response.status_code == 200) or (retry_res_num >= 5):
            #             break
            #         retry_res_num += 1
            #     selector = etree.HTML(response.text)  # 将text转化成lxml
            #     img_url = selector.xpath('//li[@id="post-info-size"]//a/@href')[0]
            #     print("img_url 002", img_url)
            #     # self.url_dic['img_url_que'].put(img_url)
            # except:
            #     # self.url_dic['img_url_que'].put("https://i.pximg.net/c/")
            #     print("该li节点没有img_url :https://danbooru.donmai.us/入队...")
            #     img_url = "https://danbooru.donmai.us/"
            #     if not(referer_url in self.retry_que):
            #         self.retry_que.append(referer_url)
            #         self.url_dic['Referer_url_que'].put(referer_url)
            print("\t尝试jpg文件下载...")
            print("Requests：{0}".format(img_url))
            if "https://cdn.donmai.us/original/" in img_url:
                pic_name = str(img_url).lstrip(r"https://cdn.donmai.us/original/")  # 图片命名 包括格式
            else:
                pic_name = str(img_url).lstrip(r"https://danbooru.donmai.us/data/")  # 图片命名 包括格式
            print("pic_name1 =", pic_name)
            pic_name = pic_name.replace(r"/", r"_")
            print("pic_name2 =", pic_name)
            artistor_title = re.sub('[/\:,*?"<>|]', '', self.artistor_title)
            if "{0}".format(referer_url) in pic_list:
                # break_num_rec = break_num_rec + 1
                print("{0}文件存在在picture_list已有下载记录，跳过下载...\n{1}".format(pic_name, referer_url))
            elif self.pic_exist(pic_name):
                with open("{0}\\{1}\\{2}_picture_list.txt".format(self.download_path, artistor_title, artistor_title), 'a', encoding='utf8') as pic_list_write:
                    if exsit_pic == False:
                        break_num_rec = break_num_rec + 1
                        pic_list_write.write("{0}\n".format(referer_url))
                        print("{0}写入成功...\n".format(referer_url))
            elif (img_url != "https://danbooru.donmai.us/"):
                try:
                    response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out, time_out_add))  #加verify防止SSL报错2:::有效，谨慎删除
                    print("\tresponse 状态：", response.status_code)
                    # if not response.status_code == 200:
                    #     raise IndexError
                except:
                        print("{0}--->服务器请求失败，将重试{1}次请求...".format(pic_name, retry_num))
                        for i in range(retry_num):
                            time.sleep(0.1)
                            try:
                                response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))
                                if response.status_code == 200:
                                    break
                            except:
                                pass
                # with closing(se.get(img_url, headers=self.headers, stream=True, verify=False)) as response:
                try:
                    statu_code_tem = int(response.status_code)
                except:
                    statu_code_tem = 555  #手动设置异常
                if statu_code_tem == 200:  # 网页正常打开
                    jpg_success_num += 1
                    # img = response.content
                    down_re = self.download_only(response, img_url=img_url, referer_url=referer_url, pic_name=pic_name)
                    # print("down_re = ", down_re)
                    if down_re == False:  # 启动下载
                        for i in range(5):  # 尝试重下30次
                            retry_que += 1
                            print("第{0}次重新下载...".format(i + 1))
                            try:
                                response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out, time_out_add))
                                if response.status_code == 200:
                                    if self.download_only(response, img_url=img_url, referer_url=referer_url, pic_name=pic_name) == True:
                                        break
                                else:
                                    continue
                            except:
                                pass
                            # if ((i+1) == 5):
                            #     self.url_dic['Referer_url_que'].put(referer_url)
                            #     print("重新加入下载队列001：", referer_url)
                        if i == 4:
                            fail_num += 1

    def download_only(self, response, img_url, referer_url, pic_name):
        #仅提供图片保存功能，即写入磁盘
        # 文件不存在，创建文件开始下载图片
        global fail_num, retry_que
        artistor_title = re.sub('[/\:,*?"<>|]', '', self.artistor_title)
        print("response.status_code", response.status_code)
        chunk_size = 1024 #每次最大请求字节数
        for i in range(10):
            try:
                content_size = int(response.headers['content-length']) #获得最大请求字节
                print("获取content size成功：", content_size)
                break
            except:
                print("获取content size失败...")
        data_count = 0
        try:
            with open('{0}'.format(pic_name), 'ab') as f:
                number_stream = 0
                for data in response.iter_content(chunk_size=chunk_size):  # 一块一块下载
                    f.write(data)
                    f.flush()
                    data_count = data_count + len(data)
                    now = int(35 * data_count / content_size)  # 计算下载进度
                    sys.stdout.write("\r[%s%s] %d%%" % ('⬛' * now, ' ' * (35 - now), 100 * data_count / content_size))
                    sys.stdout.flush()
                    number_stream += 1
                if now == 35:
                    with open("{0}\\{1}\\{2}_picture_list.txt".format(self.download_path, artistor_title, artistor_title), 'a', encoding='utf8') as pic_list_write:
                        pic_list_write.write("{0}\n".format(referer_url))  # 将图片信息写入文件
                else:
                    print("下载流不完整不写入下载历史...")
                    if os.path.exists("{0}\\{1}\\{2}".format(self.download_path, artistor_title, pic_name)):
                        f.close()
                        os.remove("{0}\\{1}\\{2}".format(self.download_path, artistor_title, pic_name))
                        # self.url_dic['Referer_url_que'].put(referer_url)
                        # print("重新加入下载队列002：", referer_url)
                        print("已删除破损文件：\t{0}".format(pic_name))
                    return False
                print(" ")
                # print("number_stream:", now)
                print("{0}\t下载成功...".format(img_url))
                print(referer_url)
                print("\t已下载   {0} jpg\t {1} png \t失败：{2} \t retry_que: {3}\n".format(jpg_success_num, png_success_num, fail_num, retry_que))
                return True

        except:  #self.url_dic = {'img_url_que': Queue(maxsize=0), 'Referer_url_que': Queue(maxsize=0), 'Page_num_que': Queue(maxsize=0), 'Page_num_list': []}
            print("下载失败，stream consume异常：：", referer_url)
            # self.url_dic['Referer_url_que'].put(referer_url)
            # print("重新加入下载队列003：", referer_url)
            if os.path.exists("{0}\\{1}\\{2}".format(self.download_path, artistor_title, pic_name)):
                f.close()
                os.remove("{0}\\{1}\\{2}".format(self.download_path, artistor_title, pic_name))
                print("已删除破损文件：\t{0}".format(pic_name))
            return False

    def pic_exist(self, pic_name):  #存在则跳过向服务器申请  pic_name, num, "_master1200", "jpg"
        if os.path.exists('{0}'.format(pic_name)):  # 开始下载
            print("文件存在，跳过\t{0}\t下载...".format(pic_name))
            return True
        else:
            return False


    def img_download_req(self, url_dic):  #self.url_dic = {'img_url_que': [], 'Referer_url_que': [], 'Page_num_que': []}
        """获取原图下载地址"""
        global pic_list, break_num_rec
        self.change_down_path(self.artistor_title)  #创建画师文件夹
        print("画师 {0} 图集下载dir：\t{1}".format(self.artistor_title, os.getcwd()))  #存放路径
        print("\t开始下载...")
        while True:
            ref_empty = url_dic['Referer_url_que'].empty()
            if ref_empty:  # 解决下载队列不对称问题
                print("下载队列为空，结束下载...\n")
                break
            # print("Referer_url_que, img_url_que是否空： ", url_dic['Referer_url_que'].empty(), url_dic['img_url_que'].empty())
            referer_url = url_dic['Referer_url_que'].get()
            if "{0}".format(referer_url) in pic_list:
                break_num_rec = break_num_rec + 1
                print("{0}\n文件存在在picture_list已有下载记录，跳过下载...".format(referer_url))
            else:
                self.headers['Referer'] = referer_url  #无论哪种下载方式，referer都不变
                img_url = ''
                pic_name = ""
                self.get_multi_img(img_url, referer_url, pic_name)

    def Pixiv_Go(self, pixiv):
        global driver_exsit, fail_num, auto_break_picNum_exist, auto_break, break_num_rec
        self.url_full_page(pixiv)
        while self.next_page_exist:
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("break_num_rec=",break_num_rec)
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            # print("存在下一页...")
            try:
                # print("切换下一页...")
                self.next_page()  # 切换下一页面
                down_tag = True
                pass
            except:
                down_tag = False
                print("遍历了 {0} 页,切换下一页失败...".format(self.pages))
            if down_tag:
                self.url_full_page(pixiv)
        if not self.failure_list.__len__() == 0:
            with open("{0}\\{1}\\{2}_failure_list.txt".format(self.download_path, self.artistor_title,
                                                              self.artistor_title), 'w', encoding='utf8') as pic_fail_w:
                for line in self.failure_list:  #将失败的文件列表存入文件
                    pic_fail_w.write(line + '\n')  # 将失败图片信息写入列表
                print("\t{0} 图片下载失败列表写入成功...".format(self.artistor_title))
        print("遍历{0} {1} 页，已到页末...\n".format(self.artistor_title, self.pages))
        #检查总的数量是否对应
        print("referer网址数:\t{0}， img_url网址数：\t{1}，多图作品集数量：\t{2}\n"
              .format(self.url_dic['Referer_url_que']._qsize(), self.url_dic['img_url_que']._qsize(),
                      not_zero_num(self.url_dic['Page_num_list'])))
        print("\t{0} 已全部下载完成".format(self.artistor_title))
        print("\t已下载   {0} jpg\t {1} png \t失败：{2}\n".format(jpg_success_num, png_success_num, fail_num))
        print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun/PixivSpider")
        print("\t剩余referer网址数:\t{0}\t， 剩余img_url网址数：\t{1}\t\n"
              .format(self.url_dic['Referer_url_que']._qsize(), self.url_dic['img_url_que']._qsize()))

def not_zero_num(list):
    num = 0
    print('pic_numss: ', list)
    for i in range(list.__len__()):
        if list[i] != 1:
            num += 1
    return num

def ini_config_read(c_path):
    dic = {}
    ID = []
    try:
        with open(c_path +"\\Danbooru"+ "\\config_danbooru.json", 'r', encoding='utf8') as conf:
            dic = json.load(conf)
            print(dic)
    except:
        print("collection_config.json 文件打开失败，请确认文件是否存在...")
    try:
        with open(c_path + "\\Danbooru"+ "\\danbooru_标签.txt", 'r', encoding='utf8') as ID_f:
            for line in ID_f:
                lines = str(line.strip()).split()
                try:
                    ID.append(lines[0])  # 读取标签
                except:
                    pass
    except:
        print("collection_url.txt 文件打开失败，请确认文件是否存在...")
    return dic, ID

def page_scroll(ranges, Time):
    # 模拟滚动条到底部  模拟pagedown
    global driver
    for i in range(ranges):
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(Time)
    time.sleep(time_wait)

def Driver(profile_dir):
    #配置一次就行
    # driver = webdriver.Chrome()
    # prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.download_path}
    global driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=" + profile_dir)  # +os.path.abspath(profile_dir)  也行
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
        driver = webdriver.Chrome(chrome_options=chrome_options)
    except:
        print("请求失败，请检查chrome是否关闭！\n")

def Dan_main():
    # print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun\n")
    global auto_break_picNum_exist, auto_break, break_num_rec,time_scroll,time_wait,retry_num,time_out,time_out_add,range_num,load_img,headless, pic_list, jpg_success_num, png_success_num, driver
    C_Path = os.getcwd()
    # print(C_Path)
    dic_dir, ID = ini_config_read(C_Path)
    # print(dic_dir)
    # print(ID)
    time_scroll = int(dic_dir["time_scroll"])
    time_wait = int(dic_dir["time_wait"])
    retry_num = int(dic_dir['retry_num'])
    time_out = int(dic_dir['time_out'])
    time_out_add = int(dic_dir['time_out_add'])
    range_num = int(dic_dir['range_num'])  # 每页的下拉次数
    if str(dic_dir["auto_break"]) == "True":
        auto_break = True
    else:
        auto_break = False
    auto_break_picNum_exist = int(dic_dir["auto_break_picNum_exist"])
    print("auto_break:  ", auto_break)
    print("auto_break_picNum_exist:  ", auto_break_picNum_exist)
    if dic_dir["headless"] == "True":
        headless = True
    if dic_dir["load_img"] == "False":  # 不加载图
        load_img = False
    # print("\tlong_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
    Driver(dic_dir["google_dir"])
    pixiv = Pixiv(dic_dir["download_dir"], dic_dir["google_dir"])
    for id in ID:
        break_num_rec = 0
        art_file = id
        if "ordfav" in art_file:
            art_file = "我的收藏"
        pic_list = []
        if os.path.exists(
                "{0}\\{1}\\{2}_picture_list.txt".format(dic_dir["download_dir"], art_file, art_file)):  # 读取已下载的文件列表
            with open("{0}\\{1}\\{2}_picture_list.txt".format(dic_dir["download_dir"], art_file, art_file),
                      'r') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
        if not id == '':
            pixiv.__init__(dic_dir["download_dir"], dic_dir["google_dir"], str(id))  # 用户自定义下载路径，下载画师id，以及Google数据路径
            pixiv.Pixiv_Go(pixiv)
    print("\njpg成功总数:\t{0}\tpng成功总数：\t{1}".format(jpg_success_num, png_success_num))
    driver.quit()
    # esc = input("--Q--退出...:")
    # del pixiv, driver, se, jpg_success_num, png_success_num
    # gc.collect()  # 可单独写内存清理函数  https://blog.csdn.net/jiangjiang_jian/article/details/79140742

if __name__ == '__main__':
    # print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun\n")
    # global auto_break_picNum_exist, auto_break, break_num_rec
    C_Path = os.getcwd()
    # print(C_Path)
    dic_dir, ID = ini_config_read(C_Path)
    # print(dic_dir)
    # print(ID)
    time_scroll = int(dic_dir["time_scroll"])
    time_wait = int(dic_dir["time_wait"])
    retry_num = int(dic_dir['retry_num'])
    time_out = int(dic_dir['time_out'])
    time_out_add = int(dic_dir['time_out_add'])
    range_num = int(dic_dir['range_num'])  #每页的下拉次数
    if str(dic_dir["auto_break"]) == "True":
        auto_break = True
    else:
        auto_break = False
    auto_break_picNum_exist = int(dic_dir["auto_break_picNum_exist"])
    print("auto_break:  ", auto_break)
    print("auto_break_picNum_exist:  ", auto_break_picNum_exist)
    if dic_dir["headless"] == "True":
        headless = True
    if dic_dir["load_img"] == "False":  # 不加载图
        load_img = False
    # print("\tlong_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
    Driver(dic_dir["google_dir"])
    pixiv = Pixiv(dic_dir["download_dir"], dic_dir["google_dir"])
    for id in ID:
        break_num_rec = 0
        art_file = id
        if "ordfav" in art_file:
            art_file = "我的收藏"
        pic_list = []
        if os.path.exists("{0}\\{1}\\{2}_picture_list.txt".format(dic_dir["download_dir"], art_file, art_file)):  #读取已下载的文件列表
            with open("{0}\\{1}\\{2}_picture_list.txt".format(dic_dir["download_dir"], art_file, art_file), 'r') as pic_list_file:
                for line in pic_list_file:
                    pic_list.append(line.strip())
        if not id == '':
            pixiv.__init__(dic_dir["download_dir"], dic_dir["google_dir"], str(id))  #用户自定义下载路径，下载画师id，以及Google数据路径
            pixiv.Pixiv_Go(pixiv)
    print("\njpg成功总数:\t{0}\tpng成功总数：\t{1}".format(jpg_success_num, png_success_num))
    driver.quit()
    esc = input("--Q--退出...:")
    del pixiv, driver, se, jpg_success_num, png_success_num
    gc.collect()  #可单独写内存清理函数  https://blog.csdn.net/jiangjiang_jian/article/details/79140742


