#!/user/bin/env python3
# -*- coding: utf-8 -*-
# python 3.7
# kotori  QQ:450072402   微信：WLJ_450072402
# pixiv爬虫

# Html5动图： http://i.pximg.net/img-zip-ugoira/img/2015/02/10/00/26/26/48656912_ugoira1920x1080.zip
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
from queue import Queue
import gc   #garba collector 内存管理
import logging  #保证session.get()  verify=False条件下不报警告
import re

logging.captureWarnings(True) #忽略警告
# reload(sys)
# sys.setdefaultencoding('utf8')

se = session()
se.keep_alive = False  #防止访问数量过多，服务器关闭请求  SSL443错误方法3：：：貌似有效
global jpg_success_num, png_success_num, fail_num, driver_exsit, C_Path
global driver, time_scroll,time_wait, time_out, time_out_add, range_num, retry_que, load_img, headless, history_pages
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
history_pages = 0
auto_break = True
auto_break_picNum_exist = 888
break_num_rec = 0

class Pixiv():
    artist_num = 0
    def __init__(self, dir = '', google_dir = '', ID ='', collection_url=''):
        """
        Pixiv对象初始化，并初始化Google浏览器路径，下载根路径，和个人收藏url
        :param dir: 下载路径
        :param google_dir: 谷歌数据路径
        :param ID: 这里没有用
        :param collection_url: 收藏url
        """
        self.profile_dir = google_dir            #r'C:\Users\Mimikko\AppData\Local\Google\Chrome\User Data'  # Google数据保存地址  #谷歌路径
        # 设置Google数据位置，方便调用密码数据，避免登陆等
        self.base_url = 'https://www.pixiv.net'  #这里是很多超链接的前缀
        self.download_path = dir  #r'E:\多媒体\pyspider'
        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection':'close'  #1.防服务器报错一：：：：防止服务器443错误， 超过允许连接数量  貌似无效
        }
        self.artist_ID = ID  #后通过循环进行赋值
        self.next_page_exist = True   #默认存在下一页
        self.target_url = collection_url
        self.pages = 1
        self.page_main = ''
        self.artistor_title = ''   #用于创建画集文件夹
        self.current_dir = ''
        self.url_dic = {'img_url_que': Queue(maxsize=0), 'Referer_url_que': Queue(maxsize=0), 'Page_num_que': Queue(maxsize=0), 'Page_num_list': [], 'artist_name_que': Queue(maxsize=0)}
        if self.artist_num == 0:
            self.root_path()
            print("支持Google浏览器78版本及以上！！！\n")
            # print("\t测试全局变量：long_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
        self.picture_size = 0
        self.artist_num += 1
        self.picture_list = []
        self.failure_list = []
        self.share_pages = 0
        self.hide_pages = 0
        self.retry_que = []  # 标记下载后失败的图片，避免死循环


    def get_art_url(self):
        self.target_url = r"https://www.pixiv.net/member_illust.php?id=" + self.artist_ID

    def root_path(self):
        self.current_dir = os.getcwd()  #获取执行路径
        if not os.path.exists(self.download_path): # 不存在则创建下载路径
            os.makedirs(self.download_path)
        os.chdir(self.download_path)
        print("图片下载目录:{0}...".format(self.download_path))
        print("配置文件存放地址：{}...".format(self.current_dir))

    def change_down_path(self, sub_dir):
        path_dir = self.download_path + "\\" + sub_dir
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
            print("{0} 存放路径创建成功...".format(path_dir))
        os.chdir(path_dir)

    def config_requests(self):
        #从Google获取cookies配置requests
        cookies = driver.get_cookies()
        # print("从se获取改变前的cookies:\n", se.cookies)
        with open(C_Path + "\\Pixiv" + r'\cookies.json', 'w') as fp:
            json.dump(cookies, fp)
        # try:
        #     with open(C_Path +"\\Pixiv" + r'\cookies.json', 'w') as fp:
        #         json.dump(cookies, fp)
        # except:
        #     print("从chrome cookies存放失败！\n")
        #这里用cookies对象进行处理
        jar = RequestsCookieJar()
        with open(C_Path + "\\Pixiv" + r'\cookies.json', 'r') as fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
        # try:
        #     jar = RequestsCookieJar()
        #     with open(C_Path +"\\Pixiv" + r'\cookies.json', 'r') as fp:
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
        # self.target_url = 'https://www.pixiv.net/bookmark.php'  # 个人收藏网址
        while True:
            try:
                driver.get(self.target_url)  # 绕过有人机检查  anmi: https://www.pixiv.net/member_illust.php?id=212801   Hiten: 'https://www.pixiv.net/member_illust.php?id=490219'
                # self.pages += 1
                time.sleep(time_scroll)
                self.page_main = driver.current_url
                self.artistor_title = re.sub('[/\:,*?"<>|]', '', driver.title.strip(" - pixiv"))
                if driver_exsit == False:
                    self.config_requests()
                    driver_exsit == True  #待cookies数据获得后将状态置为True：表浏览器已创建成功
            except:
                print("网页打开失败！\n")
            if driver.title != "www.pixiv.net":
                break
        print("解析主页title：\t{0}".format(self.artistor_title))
        # print("当前解析主页网址：\t{0}\n".format(self.page_main))  #将每位画师的首页存放在page_main中

    def get_big_img(self, img_source):
        if ('150x150' in img_source) == True:
            # date_id = id.strip("https://i.pximg.net/c/250x250_80_a2/img-master")  # 头字符串切除
            # date_id = date_id.strip('_square1200.jpg')  #去尾
            # 原图url拼接 字符串替换
            # img_url = 'https://i.pximg.net/img-original' + date_id + '.jpg'  # 不能直接下载,还要考虑不是jpg格式的图
            print("原url：\t", img_source)
            if ('/img-master/' in img_source):
                img_url = str(img_source).replace("https://i.pximg.net/c/150x150/img-master",
                                                  "https://i.pximg.net/img-original")
                if "master" in img_url:
                    img_url = img_url.replace("_master1200.jpg", ".jpg")  # 默认转换成
                elif "square" in img_url:
                    img_url = img_url.replace("_square1200.jpg", ".jpg")  # 默认转换成
            else:  # ('custom-thumb/' in img_source)
                img_url = str(img_source).replace("https://i.pximg.net/c/150x150/custom-thumb",
                                                  "https://i.pximg.net/img-original")
                img_url = img_url.replace("_custom1200.jpg", ".jpg")  # 默认转换成
            self.url_dic['img_url_que'].put(img_url)
            # print("原url：\t",img_source)
            # print("截取后字符串：\t", date_id)
            print("拼接img_url:\t{0}".format(img_url))
        else:
            self.url_dic['img_url_que'].put("https://i.pximg.net/")
            print(img_source)
            print("请检查转换函数，原图网址并未转换...")

    def get_img_ref_pageNum(self, num=0, li_null=False):
        """获取网页下载图片的链接"""
        #打印检查 html = etree.HTML(text)
        # s = etree.tostring(html).decode()
        global driver
        # print("num1=",num)
        while True:
            # print("li_null=", li_null)
            if (driver.title == "www.pixiv.net") or (li_null == True):
                driver.refresh()
                time.sleep(time_wait)
                # self.page_scroll(range_num, time_scroll)
                page_scroll(range_num, time_scroll)
                # print("num2=", num)
                li_null = False # 避免陷入死循环
            else:
                break
        # all_xml = dom.xpath("//ul[@class='_2WwRD0o _2WyzEUZ']")
        # li_list = driver.find_elements_by_xpath("//ul[@class='_image-items js-legacy-mark-unmark-list']//li")
        li_list = driver.find_elements_by_xpath("//ul[@class='_image-items js-legacy-mark-unmark-list']//li[@class='image-item']")
        print("li_list.__len__(): ", li_list.__len__())
        print('')
        for element in li_list:
            # print("作者：", element.find_element_by_xpath(".//a[@class='user ui-profile-popup']").text)
            try:  # 获取作者名称
                artist_name = str(element.find_element_by_xpath(".//a[@class='user ui-profile-popup']").text)
                artist_name = re.sub('[/\:,*?"<>|.]', '', artist_name)
                print("作者：", artist_name)
                self.url_dic['artist_name_que'].put(artist_name)
            except:
                self.url_dic['artist_name_que'].put("null")
                print("该li节点没有作者 null 入队 artist_name_que ...")
            # print("获取原图地址:", element.find_element_by_xpath(".//img[@src]").get_attribute('src'))
            try:  # 获取原图地址
                img_url = element.find_element_by_xpath(".//img[@src]").get_attribute('src')
                # print("获取原图地址:", img_url)
                self.get_big_img(img_url)
            except:
                self.url_dic['img_url_que'].put("https://i.pximg.net/c/")
                print("该li节点没有img_url :https://i.pximg.net/c/入队...")
            try:  # 获取referer url
                referer_url = element.find_element_by_xpath(".//a[@style='display:block']").get_attribute('href')   #好家伙居然把sc-fzXfQp bNPARF换掉了
                self.url_dic['Referer_url_que'].put(referer_url)  #入队列
                print("referer_url: ", referer_url)
            except:
                self.url_dic['Referer_url_que'].put("https://i.pximg.net/c/")  # 入队列
                print("该li节点没有referer_url...")
            try: # 获取图片数量
                pic_num = element.find_element_by_xpath(".//div[@class='page-count']//span").text
                self.url_dic['Page_num_que'].put(int(pic_num))
                self.url_dic['Page_num_list'].append(int(pic_num))
                print("pic_num:\t{0}\n".format(pic_num))
            except:
                self.url_dic['Page_num_que'].put(1)
                self.url_dic['Page_num_list'].append(1)
                print("该作品为单图集...\n")
                pass
        # print("num3=", num)
        print("artist, img, referer, pic_number 四个队列长度::", self.url_dic['artist_name_que'].qsize(), self.url_dic['img_url_que'].qsize(), self.url_dic['Referer_url_que'].qsize(), self.url_dic['Page_num_que'].qsize())
        ref_que_size = self.url_dic['Referer_url_que'].qsize()
        img_que_size = self.url_dic['img_url_que'].qsize()
        print("ref_que_size :{0}, img_que_size :{1}\n".format(ref_que_size, img_que_size))
        if (li_list.__len__() == 0) or (ref_que_size ==0) or (img_que_size == 0):
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

    def get_pagesource(self):
        #用xpath解析
        """
        获取全页面待下载的大图打开链接  即：referer链接, 解析大图链接
        :return:
        """
        page = driver.page_source
        # print(page)  # y用xpath helper获取的img  url：//img[contains(@src,"")]/@src
        dom = etree.HTML(page)
        # self.get_img_ref_pageNum(dom)
        dom.xpath('//img[contains(@src,"")]/@src')
        img_urls = dom.xpath('//img[contains(@src,"")]/@src')
        print("获取图片数量：", len(img_urls))
        hrefs = driver.find_elements_by_xpath("//a[@class='sc-fzXfQp bNPARF']")  #灵机一动，好像可以作为图片的名字，啊哈哈
        # img_url_que = driver.find_elements_by_xpath("//div[@class='sc-fzXfPI fRnFme']")
        img_url_que = self.get_big_img(img_urls)
        # for img_ in img_url_que:
        #     print("driver.find_element_by_xpath获取元素referers：{0}\n".format(img_.text))
        for href in hrefs:
            href_url = href.get_attribute('href')
            self.url_dic['Referer_url_que'].put(href_url)
            # print("全局href_url-{0}：\n".format(i), href_url)
        # for img in img_url_que:
        #     img_url = img.find_element_by_xpath("//img[@*]").get_attribute('src')
        #     self.url_dic['img_url_que'].append(img_url)
        for num in range(self.url_dic['Referer_url_que'].__len__()):
            print("第{0}个referer网址：\t{1}".format(num, (self.url_dic['Referer_url_que'][num]).strip()))
            print("第{0}个img网址：\t{1}\n".format(num, (self.url_dic['img_url_que'][num]).strip()))
        if hrefs.__len__() == 0:
            self.next_page_exist = False
        else:
            self.pages += 1
        print("referer网址数: {0}， img_url网址数： {1}"
              .format(self.url_dic['Referer_url_que'].__len__(), self.url_dic['img_url_que'].__len__()))
        return hrefs

    def next_page(self):
        # print("页面跳转检查：\t{0}\n".format(self.pages))
        global history_pages
        next_url = self.page_main + '&p=' + str(self.pages + history_pages)
        # print("next_url:\t ", next_url)
        print("正在解析第 {0} 页...:".format(self.pages + history_pages), next_url)
        driver.get(next_url)
        # self.pages += 1

    def url_full_page(self, pixiv):
        """获取链接进行下载"""
        if self.pages == 1:
            self.get_html()  #访问首页
            if os.path.exists("{0}\\collection_list.txt".format(self.download_path)):  # 为提高效率，统一存放至根目录
                with open("{0}\\collection_list.txt".format(self.download_path), 'r', encoding='utf8') as pic_list_read:
                    for line in pic_list_read:
                        self.picture_list.append(line.strip())  # 读取pictur_list
                print("图片下载列表读取成功...\n")
            else:
                print("图片下载列表为空...\n",self.picture_list)
                # print("读取列表：\n", self.picture_list)
        page_scroll(range_num, time_scroll)
        # self.get_pagesource()
        self.get_img_ref_pageNum()
        self.img_download_req(self.url_dic)  # 可开启多线程进行下载
        # self.get_img_url(self.get_pagesource())

    def get_multi_img(self, img_url, referer_url, pic_num, pic_name, suffix, artist_name):
        """
        1、jpg格式     2、png   3、master1200.jpg    4、master1200.png    5、下载完成、失败
        :param img_url:
        :param referer_url:
        :param pic_num:
        :param pic_name:
        :return:
        """
        global jpg_success_num, png_success_num, break_num_rec
        for num in range(pic_num):  #默认jpg下载
            img_url = str(img_url)
            if not num == 0:
                if ".jpg" in img_url:
                    img_url = img_url.replace("_p{0}.jpg".format(num - 1), "_p{0}.jpg".format(num))
                elif ".png" in img_url:
                    img_url = img_url.replace("_p{0}.png".format(num - 1), "_p{0}.jpg".format(num))
            suffix = "jpg"
            print("\t尝试jpg文件下载...")
            print("Requests：{0}".format(img_url))
            img_url_source = img_url  #暂时保存jpg  url供master1200下载使用
            # print("for循环编号测试：{0}_p{1}.{2}".format(pic_name, num, suffix))
            pic_tem_list = []
            pic_tem_list.append("{0}_p{1}.{2}".format(pic_name, num, 'jpg'))
            pic_tem_list.append("{0}_p{1}.{2}".format(pic_name, num, "png"))
            pic_tem_list.append("{0}_p{1}.{2}".format(pic_name + "_master1200", num, "jpg"))
            pic_tem_list.append("{0}_p{1}.{2}".format(pic_name + "_master1200", num, "png"))
            if (pic_tem_list[0] in self.picture_list) | (pic_tem_list[1] in self.picture_list) | (pic_tem_list[2] in self.picture_list) | (pic_tem_list[3] in self.picture_list):
                print("{0}_p{1}.{2} or png 文件存在在picture_list已有下载记录，跳过下载...\n".format(pic_name, num, suffix))
                break_num_rec = break_num_rec + 1
                continue
            elif self.pic_exist(pic_name, num, suffix, artist_name=artist_name):
                with open("{0}\\collection_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_list_write:
                    pic_list_write.write("{0}_p{1}.{2}\n".format(pic_name, num, suffix))
                    break_num_rec = break_num_rec + 1
                    print("{0}_p{1}.{2}写入成功...\n".format(pic_name, num, suffix))
                continue
            else:
                break_num_rec = 0
                try:
                    response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))  #加verify防止SSL报错2:::有效，谨慎删除
                    print("\tresponse 状态：", response.status_code)
                    # if not response.status_code == 200:
                    #     raise IndexError
                except:
                        print("{0}_p{1}--->服务器请求失败，将重试{2}次请求...".format(pic_name,num, retry_num))
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
                    self.download_only(response, img_url=img_url, referer_url=referer_url, pic_num=pic_num, pic_name=pic_name, suffix=suffix, num=num, artist_name=artist_name)  #启动下载
                else:
                    print("\tjpg格式下载错误，尝试png...")
                    img_url = str(img_url).strip(".jpg") + ".png"
                    suffix = "png"
                    # print("for循环编号测试：{0}_p{1}.{2}".format(pic_name, num, suffix))
                    if "{0}_p{1}.{2}".format(pic_name, num, suffix) in self.picture_list:
                        print("{0}_p{1}.{2} 文件存在在picture_list已有下载记录，跳过下载...".format(pic_name, num, suffix))
                        continue
                    elif self.pic_exist(pic_name, num, suffix,artist_name=artist_name):
                        with open("{0}\\collection_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_list_write:
                            pic_list_write.write("{0}_p{1}.{2}\n".format(pic_name, num, suffix))
                            print("{0}_p{1}.{2}写入成功...\n".format(pic_name, num, suffix))
                        continue
                    else:
                        try:
                            response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))  #加verify防止SSL报错2:::有效，谨慎删除
                            print("\tresponse 状态：", response.status_code)
                            # if not response.status_code == 200:
                            #     raise IndexError
                        except:
                            print("{0}_p{1}--->服务器请求失败，将重试{2}次请求...".format(pic_name,num, retry_num))
                            for i in range(retry_num):
                                time.sleep(0.3)
                                try:
                                    response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))
                                    if response.status_code == 200:
                                        break
                                except:
                                    pass
                        try:
                            statu_code_tem = int(response.status_code)
                        except:
                            statu_code_tem = 555  # 手动设置异常
                        if statu_code_tem == 200:  # 网页正常打开
                            png_success_num += 1
                            # img = response.content
                            self.download_only(response, img_url=img_url, referer_url=referer_url, pic_num=pic_num, pic_name=pic_name, suffix="png", num=num, artist_name=artist_name)  # 启动下载
                        else:  # self, img_url, pic_name, num
                            self.download_retry(img_url=img_url_source, pic_name=pic_name, num=num, referer_url=referer_url, pic_num=pic_num, artist_name=artist_name)  # 打开失败，尝试其它情况

    def download_only(self, response, img_url, referer_url, pic_num, pic_name, suffix, num, artist_name):
        #仅提供图片保存功能，即写入磁盘
        # 文件不存在，创建文件开始下载图片
        global fail_num, retry_que
        print("{0}下载：{1} \n{2}".format(suffix, referer_url, img_url))
        chunk_size = 1024 #每次最大请求字节数
        content_size = int(response.headers['content-length']) #获得最大请求字节
        data_count = 0
        self.change_down_path(artist_name)
        with open('{0}\\{1}\\{2}_p{3}.{4}'.format(self.download_path, artist_name, pic_name, num, suffix), 'ab') as f:
            try:
                number_stream = 0
                for data in response.iter_content(chunk_size=chunk_size):  #一块一块下载
                    f.write(data)
                    f.flush()
                    data_count = data_count + len(data)
                    now = int(35*data_count / content_size)  #计算下载进度
                    sys.stdout.write("\r[%s%s] %d%%" % ('⬛' * now, ' ' * (35 - now), 100 * data_count / content_size))
                    sys.stdout.flush()
                    number_stream += 1
                    # print("\r\t%s：：%s下载进度： %d%%(%.2f/%.2f)" % (self.artistor_title,'{0}_p{1}.{2}'.format(pic_name, num, suffix),
                    #                                                now, data_count / 1024, content_size / 1024), end=" ")  #\r是防止多次打印
                if now == 35:
                    with open("{0}\\collection_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_list_write:
                        pic_list_write.write("{0}_p{1}.{2}\n".format(pic_name, num, suffix))   #将图片信息写入文件
                else:
                    print("下载流不完整不写入下载历史...")
                print(" ")
                # print("number_stream:", now)
                print("{0}\t下载成功...".format(img_url))
                print("\t已下载   {0} jpg\t {1} png \t失败：{2} \t retry_que: {3}\n".format(jpg_success_num, png_success_num, fail_num, retry_que))
            except:  #self.url_dic = {'img_url_que': Queue(maxsize=0), 'Referer_url_que': Queue(maxsize=0), 'Page_num_que': Queue(maxsize=0), 'Page_num_list': []}
                fail_num += 1
                retry_que += 1
                self.failure_list.append("{0}_p{1}".format(pic_name, num))
                self.failure_list.append(referer_url)
                if os.path.exists("{0}\\{1}\\{2}_p{3}.{4}".format(self.download_path, artist_name, pic_name, num, suffix)):
                    f.close()
                    os.remove("{0}\\{1}\\{2}_p{3}.{4}".format(self.download_path, artist_name, pic_name, num, suffix))
                    print(" ")
                    print("已删除破损文件：\t{0}_p{1}.{2}".format(pic_name, num, suffix))
                if ".png" in str(img_url):  # 将png重置默认为jpg
                    print("原url： {0}...".format(img_url))
                    img_url = str(img_url).replace(".png", ".jpg")
                    print("将 {0} 重置默认为jpg...".format(img_url))
                if not(img_url in self.retry_que):
                    self.retry_que.append(img_url)
                    self.url_dic['img_url_que'].put(img_url)
                    self.url_dic['Referer_url_que'].put(referer_url)
                    self.url_dic['Page_num_que'].put(pic_num)
                    self.url_dic['artist_name_que'].put(artist_name)
                    print("下载失败，stream consume异常...")
                    print("再次加入下载队列次数：  {0}\n".format(retry_que))


    def pic_exist(self, pic_name, num, suffix, master = "", artist_name=''):  #存在则跳过向服务器申请  pic_name, num, "_master1200", "jpg"
        if not master == '':
            pic_name = str(pic_name) + master
        if os.path.exists('{0}//{1}//{2}_p{3}.{4}'.format(self.download_path, artist_name, pic_name, num, suffix)):  # 开始下载
            print("文件存在，跳过\t{0}_p{1}.{2}\t下载...".format(pic_name, num, suffix))
            return True
        else:
            return False

    def download_retry(self, img_url, pic_name, num, referer_url, pic_num, artist_name):
        """
        这种下载针对最后一种master1200，最大分辨率为1200的图片
        :return:
        """
        global jpg_success_num, png_success_num, fail_num
        print("\t尝试master1200.jpg下载...")
        img_url = str(img_url).replace("https://i.pximg.net/img-original", "https://i.pximg.net/img-master")  #换头
        img_url = img_url.replace(".jpg", "_master1200.jpg")
        if "{0}_p{1}.{2}".format(pic_name + "_master1200", num, "jpg") in self.picture_list:
            print("{0}_p{1}.{2} 文件存在在picture_list已有下载记录，跳过下载...".format(pic_name + "_master1200", num, "jpg"))
            pass
        elif self.pic_exist(pic_name, num, "jpg", "_master1200", artist_name=artist_name):
            with open("{0}\\collection_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_list_write:
                pic_list_write.write("{0}_p{1}.{2}\n".format(pic_name + "_master1200", num, "jpg"))
            pass
        else:
            try:
                response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))  #加verify防止SSL报错2:::有效，谨慎删除  timeout::connect 和 read
            except:
                        print("{0}_p{1}--->服务器请求失败，将重试{2}次请求...".format(pic_name,num, retry_num))
                        for i in range(retry_num):
                            time.sleep(0.3)
                            try:
                                response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))
                                if response.status_code == 200:
                                    break
                            except:
                                pass
            try:
                statu_code_tem = int(response.status_code)
            except:
                statu_code_tem = 555  # 手动设置异常
            if statu_code_tem == 200:  # 网页正常打开
                jpg_success_num += 1
                # img = response.content
                self.download_only(response, img_url=img_url, referer_url=referer_url, pic_num=pic_num, pic_name=pic_name + "_master1200", suffix="jpg", num=num, artist_name=artist_name)  # 启动下载
            else:
                print("尝试master1200.png下载...")
                img_url = img_url.replace("_master1200.jpg", "_master1200.png")
                if "{0}_p{1}.{2}".format(pic_name + "_master1200", num, "png") in self.picture_list:
                    print("{0}_p{1}.{2} 文件存在在picture_list已有下载记录，跳过下载...".format(pic_name + "_master1200", num, "png"))
                elif self.pic_exist(pic_name, num, "png", "_master1200", artist_name=artist_name):
                    with open("{0}\\collection_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_list_write: # 添加进下载记录
                        pic_list_write.write("{0}_p{1}.{2}\n".format(pic_name + "_master1200", num, "png"))
                else:
                    try:
                        response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))  #加verify防止SSL报错2:::有效，谨慎删除
                        print("\tresponse 状态：", response.status_code)
                        # if not response.status_code == 200:
                        #     raise IndexError
                    except:
                        print("{0}:{1}_p{2}--->服务器请求失败，将重试{3}次请求...".format(self.artistor_title, pic_name, num, retry_num))
                        for i in range(retry_num):
                            time.sleep(0.3)
                            try:
                                response = se.get(img_url, headers=self.headers, stream=True, verify=False, timeout=(time_out,time_out_add))
                                if response.status_code == 200:
                                    break
                            except:
                                pass
                    try:
                        statu_code_tem = int(response.status_code)
                    except:
                        statu_code_tem = 555  # 手动设置异常
                    if statu_code_tem == 200:  # 网页正常打开
                        png_success_num += 1
                        # img = response.content
                        self.download_only(response, img_url=img_url, referer_url=referer_url, pic_num=pic_num, pic_name=pic_name + "_master1200", suffix="png", num=num, artist_name=artist_name)  # 启动下载
                    else:
                        fail_num += 1  #失败次数自加1
                        self.failure_list.append("{0}_p{1}".format(pic_name, num))
                        self.failure_list.append(referer_url)
                        print("四种方法均下载失败...┭┮﹏┭┮")

    def img_download_req(self, url_dic):  #self.url_dic = {'img_url_que': [], 'Referer_url_que': [], 'Page_num_que': []}
        # self.change_down_path(r'\\' + self.artistor_title)  #创建画师文件夹
        sum = 0
        pic_num = 1 # 默认图片数量为1 ， 解决下载队列图片数量不对称问题
        for i in self.url_dic['Page_num_list']: #统计图片总数
            sum += i
        # with open("{0}_当前总p数.txt".format(self.artistor_title), 'w', encoding='utf8') as op:
        #     op.write("截至下载时间，已上传p站{0}张图\n包括所有单图集和多图集...\n{1}ID：{2}".format(sum, self.artistor_title, self.artist_ID))
        # print("画师 {0} 图集下载dir：\t{1}".format(self.artistor_title, os.getcwd()))  #存放路径
        print("\t开始下载...")
        while True:
            ref_empty = url_dic['Referer_url_que'].empty()
            img_empty = url_dic['img_url_que'].empty()
            if ref_empty and img_empty:  # 解决下载队列不对称问题
                print("下载队列为空，结束下载...\n")
                break
            elif ref_empty or img_empty:
                print("存在一个下载队列为空，结束下载...\n")
                break
            # print("Referer_url_que, img_url_que是否空： ", url_dic['Referer_url_que'].empty(), url_dic['img_url_que'].empty())
            referer_url = url_dic['Referer_url_que'].get()
            pic_name = str(referer_url).strip(r"https://www.pixiv.net/artworks/")  #图片命名
            self.headers['Referer'] = referer_url  #无论哪种下载方式，referer都不变
            img_url = url_dic['img_url_que'].get()
            pic_num = url_dic['Page_num_que'].get()
            artist_name = url_dic['artist_name_que'].get()
            img_id = str(referer_url).replace('https://www.pixiv.net/artworks/', '')  # 获取图片id
            if img_id in img_url:  # referer id 和 img url id匹配才下载，避免死循环
                # print("debug标记1...")
                self.get_multi_img(img_url, referer_url, pic_num, pic_name, 'jpg', artist_name=artist_name)
            else:
                print("referer id 和 img_url id不匹配，避免死循环，跳过下载...\n")

    def Pixiv_Go(self, pixiv):
        global driver_exsit, fail_num, break_num_rec, auto_break, auto_break_picNum_exist
        self.url_full_page(pixiv)
        fail_list = []  # 存放失败记录的链表
        try:
            with open("{0}\\collection_failure_list.txt".format(self.download_path), 'r', encoding='utf8') as pic_fail_r:
                for line in pic_fail_r:
                    fail_list.append(str(line))
                print("collection_failure_list.txt读取成功...")
        except:
            pass
        while self.next_page_exist:
            # print("存在下一页...")
            if (break_num_rec >= auto_break_picNum_exist and auto_break):
                print("已自动识别并认为下载到上一次下载位，退出下载......")
                break
            try:
                # print("切换下一页...")
                self.next_page()  #切换下一页面
                self.url_full_page(pixiv)
            except:
                print("遍历了 {0} 页,切换下一页失败...".format(self.pages))
            if not self.failure_list.__len__() == 0:  # 追加
                with open("{0}\\collection_failure_list.txt".format(self.download_path), 'a', encoding='utf8') as pic_fail_w:
                    for line in self.failure_list:  #将失败的文件列表存入文件
                        if not(line in fail_list):
                            pic_fail_w.write(line + '\n')  # 将失败图片信息写入列表
                self.failure_list.clear()
                print("\t图片下载失败列表写入成功...")
            print("已连续已下载图片数量：：：",break_num_rec)

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
    url_list = []
    try:
        with open(c_path + "\\Pixiv" + "\\collection_config.json", 'r', encoding='utf8') as conf:
            dic = json.load(conf)
            print(dic)
    except:
        print("collection_config.json 文件打开失败，请确认文件是否存在...")
    try:
        with open(c_path + "\\Pixiv" + "\\collection_url.txt", 'r', encoding='utf8') as ID_f:
            for line in ID_f:
                lines = str(line.strip())
                try:
                    url_list.append(lines)  # 收藏和私密收藏
                except:
                    pass
    except:
        print("collection_url.txt 文件打开失败，请确认文件是否存在...")
    return dic, url_list

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

def Pixiv_main():
    """个人收藏：P42页"""
    global collection_tag, time_scroll, time_wait, retry_num,time_out, time_out_add, range_num,headless, load_img, history_pages, auto_break, auto_break_picNum_exist, break_num_rec, jpg_success_num, png_success_num, driver
    # print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun\n")
    C_Path = os.getcwd()
    print(C_Path)
    dic_dir, url_list = ini_config_read(C_Path)
    collection_tag = 'https://www.pixiv.net/bookmark.php'
    # print(dic_dir)
    # print(ID)MN？
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
    # history_pages = int(input("请输入上次下载的页数： "))-2
    if history_pages <= 0:
        history_pages = 0
    print("history_pages: ", history_pages)
    if dic_dir["headless"] == "True":
        headless = True
    if dic_dir["load_img"] == "False":  # 不加载图
        load_img = False
    # print("\tlong_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
    Driver(dic_dir["google_dir"])
    pixiv = Pixiv(dic_dir["collection_download_dir"], dic_dir["google_dir"])
    for url in url_list:
        if "show" in url:
            download_path = dic_dir["collection_download_dir"] # secret_download_dir
        elif "hide" in url:
            history_pages = int(input("请输入上次hide下载的页数： ")) - 2
            download_path = dic_dir["secret_download_dir"]  # secret_download_dir
        pixiv.__init__(download_path, dic_dir["google_dir"], str(id), collection_url=url)  #用户自定义下载路径，下载画师id，以及Google数据路径
        pixiv.Pixiv_Go(pixiv)
    print("\njpg成功总数:\t{0}\tpng成功总数：\t{1}".format(jpg_success_num, png_success_num))
    driver.quit()
    # esc = input("--Q--退出...:")
    # del pixiv, driver, se, jpg_success_num, png_success_num
    # gc.collect()  #可单独写内存清理函数  https://blog.csdn.net/jiangjiang_jian/article/details/79140742


if __name__ == '__main__':
    """个人收藏：P42页"""
    # print("\tcoder::星纪弥航::github-->https://github.com/WLiangJun\n")
    C_Path = os.getcwd()
    print(C_Path)
    dic_dir, url_list = ini_config_read(C_Path)
    collection_tag = 'https://www.pixiv.net/bookmark.php'
    # print(dic_dir)
    # print(ID)MN？
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
    history_pages = int(input("请输入上次下载的页数： "))-2
    print("history_pages: ", history_pages)
    if dic_dir["headless"] == "True":
        headless = True
    if dic_dir["load_img"] == "False":  # 不加载图
        load_img = False
    # print("\tlong_wait_time: {0}\tshort_wait_time: {1}".format(time_wait, time_scroll))
    Driver(dic_dir["google_dir"])
    pixiv = Pixiv(dic_dir["collection_download_dir"], dic_dir["google_dir"])
    for url in url_list:
        if "show" in url:
            download_path = dic_dir["collection_download_dir"] # secret_download_dir
        elif "hide" in url:
            history_pages = int(input("请输入上次hide下载的页数： ")) - 2
            download_path = dic_dir["secret_download_dir"]  # secret_download_dir
        pixiv.__init__(download_path, dic_dir["google_dir"], str(id), collection_url=url)  #用户自定义下载路径，下载画师id，以及Google数据路径
        pixiv.Pixiv_Go(pixiv)
    print("\njpg成功总数:\t{0}\tpng成功总数：\t{1}".format(jpg_success_num, png_success_num))
    driver.quit()
    esc = input("--Q--退出...:")
    del pixiv, driver, se, jpg_success_num, png_success_num
    gc.collect()  #可单独写内存清理函数  https://blog.csdn.net/jiangjiang_jian/article/details/79140742


