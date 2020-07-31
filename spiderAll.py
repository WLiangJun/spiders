#!/user/bin/env python3
# -*- coding: utf-8 -*-
import Danbooru_singleThread as Danbooru
import KanachanSpider as Kanachan
import Pixivfavorite_singleThread as Pixiv
import TwitterArtist as Twitter
import yandeSpider as yande
import os
from selenium import webdriver

global localPath, driver

def loadImgDriver():
    # 配置谷歌路径信息，免登录
    global driver, localPath
    headless = False
    load_img=True
    dic_dir, ID = Danbooru.ini_config_read(localPath)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=" + dic_dir["google_dir"])  # +os.path.abspath(profile_dir)  也行
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
        driver.quit()
    except:
        print("请求失败，请检查chrome是否关闭！\n")
    print("google浏览器设置恢复成功...")


def spiderAll(model = 10):
    if model==1:
        Danbooru.Dan_main()
    if model==2:
        Kanachan.Kana_main()
    if model==3:
        Pixiv.Pixiv_main()
    if model==4:
        Twitter.Twit_main()
    if model==5:
        yande.Yan_main()
    if model==10:
        Danbooru.Dan_main()
        os.chdir(localPath)
        Kanachan.Kana_main()
        os.chdir(localPath)
        Twitter.Twit_main()
        os.chdir(localPath)
        yande.Yan_main()
        os.chdir(localPath)
        Pixiv.Pixiv_main()
    if model == 20:
        loadImgDriver()

if __name__=='__main__':
    print("Danbooru: 1\t Kanachan: 2\tpixiv: 3\tTwitter: 4\tyande: 5\tAll: 10\t还原谷歌设置： 20")
    localPath = os.getcwd()
    model = int(input("选择爬取网站：："))
    print("localPath = ", localPath)
    spiderAll(model)
    loadImgDriver()
    input("爬取完成，任意键退出...")
    pass