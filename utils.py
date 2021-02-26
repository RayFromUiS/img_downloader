
# from img_scraper.model import db_connect,create_table
import os
import re
import pandas as pd
from model import db_connect,create_table
from bs4 import Tag
from bs4 import BeautifulSoup
import requests as req
from fake_useragent import UserAgent


def grap_preview_imgs_urls(img_table, engine):
    '''
    get img - url pair from the model
    db_img_http: column name from the model,such as preview_img_link/title_img_url
    db_img_local:column name from the mode, such as preview_img_local/title_img_local
    '''
    ori_df = pd.read_sql_table(img_table, engine)
    preview_imgs_urls = {}
    for row in ori_df.itertuples():
        #         print(dir(row))
        img_url = {}
        prview_img_links = []
        preview_img_locals = []
        prview_img_links.append(row.preview_img_link)
        preview_img_locals.append(row.preview_img_local)
        img_url['preview_img_link'] = prview_img_links
        img_url['preview_img_local'] = preview_img_locals
        if not preview_imgs_urls.get(row.orig_id):
            preview_imgs_urls[row.orig_id] = img_url

    return preview_imgs_urls


def grap_content_imgs_urls(table, engine):
    '''
    get img - url pair from the model
    db_img_http: column name from the model,such as preview_img_link/title_img_url
    db_img_local:column name from the mode, such as preview_img_local/title_img_local
    '''
    ori_df = pd.read_sql_table(table, engine)
    content_imgs_urls = {}
    for row in ori_df.itertuples():
        #         print(dir(row))
        img_url = {}
        img_url['title_img_url'] = row.title_img_url
        img_url['title_img_local'] = row.title_img_local
        if not content_imgs_urls.get(row.orig_id):
            content_imgs_urls[row.orig_id] = img_url

    return content_imgs_urls


def get_content_imgs_url(table, engine, content_imgs_urls):
    ''' get imgs set from new content title
    '''
    not_down_content = {}
    ori_df = pd.read_sql_table(table, engine, columns=['id', 'title', 'new_content'])
    ori_df_imgs = ori_df['new_content'].apply(lambda x: BeautifulSoup(x).find_all('img'))
    for _id, title, imgs in zip(ori_df['id'].values, ori_df['title'].values, ori_df_imgs.values):
        #     print(_id,title,img,type(title),type(img))
        img_value = {}
        #         title_img_urls = []
        content_img_urls = []
        for img in imgs:
            if isinstance(img, Tag):
                content_img_url = img.attrs.get('src')
                if re.match(r'http', content_img_url):
                    #             print(title_img_url)
                    content_img_urls.append(content_img_url)
                    if not content_imgs_urls.get(str(_id) + str(title)):
                        img_value['title_img_url'] = content_img_urls
                        not_down_content[str(_id) + str(title)] = img_value

    return not_down_content


def get_preview_imgs_url(table, engine, preview_imgs_urls):
    ''' get imgs set from preview img links
    '''

    not_down_previews = {}
    ori_df = pd.read_sql_table(table, engine, columns=['id', 'title', 'preview_img_link'])
    ori_df_imgs = ori_df['preview_img_link']
    for _id, title, img in zip(ori_df['id'].values, ori_df['title'].values, ori_df_imgs.values):
        #     print(_id,title,img,type(title),type(img))
#         print(imgs)
        img_value = {}
        preview_img_urls = []
#         for img in imgs:
#             if re.match(r'http', img):
#                 #             print(title_img_url)
        preview_img_urls.append(img)
        if not preview_imgs_urls.get(str(_id) + str(title)):
            img_value['preview_img_link'] = preview_img_urls
            not_down_previews[str(_id) + str(title)] = img_value
    return not_down_previews


def download_imgs(img_urls,img_url_key,img_url_local_key,save_dir,table):
    '''download imgs
        img_url_key:'preview_img_link'
        img_url_local_key:'preview_img_local'
    '''
    
    imgs_downloaded = {}
    imgs_not_downloaded = {}
    
    for ks,vs in img_urls.items():
        
        for img_key,img_links in vs.items(): #for each item inside 
            for img_link in img_links:
#                 print(img_link)
                if img_link: ##if there is link from img element
                    if not os.path.exists(os.path.join(save_dir,table)):
                        os.mkdir(os.path.join(save_dir,table))
                    img_file = os.path.join(preview_save_dir,table,ks+'____'+img_link.split('/')[-1])
                    if  not os.path.exists(img_file): #check file already downloaded
                        try: ## try to download the img file and save it
                            res = req.get(url=img_link,
                                          stream=True,
                                         headers ={'user-agent':user_agent})
                            with open(img_file,'wb') as f:
                                f.write(res.content)
                            imgs_downloaded[ks] = {img_url_key:img_link,
                                                  img_url_local_key:img_file}
#                             print('finish downloading')
                        except: ## couldn't downloaded it
                            continue
                            
                            imgs_not_downloaded[ks] = {img_url_key:img_link} #save the undownloaded img link
                else: ## if img is None,save to avoid searching again
                    imgs_not_downloaded[ks] = {img_url_key:None}
                    
    return imgs_downloaded,imgs_not_downloaded
    