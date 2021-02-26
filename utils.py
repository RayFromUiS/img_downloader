
import os
import re
import time
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
#     ori_df_imgs = ori_df['new_content'].apply(lambda x: BeautifulSoup(x).find_all('img'))
    ori_df_imgs = ori_df['new_content']
    for _id, title, imgs in zip(ori_df['id'].values, ori_df['title'].values, ori_df_imgs.values):
        #     print(_id,title,img,type(title),type(img))
        img_value = {}
        soup_imgs= BeautifulSoup(imgs,'lxml').find_all('img')
        
#         print(soup_imgs)
        content_img_urls = []
        if len(soup_imgs)>=1: ## has image tag
            
            for soup_img in soup_imgs: ## for each img tag 
                if soup_img and re.search('http',soup_img.attrs['src']):
                    content_img_urls.append(soup_img.attrs.get('src'))  #append all the content imgs    
#         img_value['title_img_url'] = content_img_urls ##save values
        
            if not content_imgs_urls.get(str(_id) + str(title)):
                    img_value['title_img_url'] = content_img_urls
                    not_down_content[str(_id) +'__'+ str(title)] = img_value
                
        if len(soup_imgs)==0:
#             img_value['title_img_url'] = None
            if not content_imgs_urls.get(str(_id) + str(title)):
                img_value['title_img_url'] = None
                not_down_content[str(_id) +'__'+str(title)] = img_value

    # print(not_down_content)
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
        if re.search(r'http',img):
            preview_img_urls.append(img)
            if not preview_imgs_urls.get(str(_id) + str(title)):
                img_value['preview_img_link'] = preview_img_urls
                not_down_previews[str(_id) + '__'+str(title)] = img_value
        elif img=='None':
            if not preview_imgs_urls.get(str(_id) + str(title)):
                img_value['preview_img_link'] = None
                not_down_previews[str(_id) +'__'+ str(title)] = img_value
#                 print(img_value)
#     print(not_down_previews)
    return not_down_previews


def download_imgs(img_urls,img_url_key,img_url_local_key,save_dir,table):
    '''download imgs
        img_url_key:'preview_img_link'
        img_url_local_key:'preview_img_local'
    '''
    
    imgs_downloaded = {}
    imgs_not_downloaded = {}
    
    for ks,vs in img_urls.items():
        ua = UserAgent()
        user_agent = ua.ie
        for img_key,img_links in vs.items(): #for each item inside 
            if isinstance(img_links,list): ## if there is imaget link
                for img_link in img_links:
    #                 print(img_link)
                    if img_link: ##if there is link from img element
                        if not os.path.exists(os.path.join(save_dir,table)):
                            os.mkdir(os.path.join(save_dir,table))
                        img_file = os.path.join(save_dir,table,ks+img_link.split('/')[-1])
                        if  not os.path.exists(img_file): #check file already downloaded
                            try: ## try to download the img file and save it
                                res = req.get(url=img_link,
                                              stream=True,
                                             headers ={'user-agent':user_agent})
                                time.sleep(3)
                                with open(img_file,'wb') as f:
                                    f.write(res.content)
                                imgs_downloaded[ks] = {img_url_key:img_link,
                                                      img_url_local_key:img_file}
    #                             print('finish downloading')
                            except: ## couldn't downloaded it
                                continue

                                imgs_not_downloaded[ks] = {img_url_key:img_link} #save the undownloaded img link
            # print(img_links)
            else: ## if img is None,save to avoid searching again
                # print(img_links)
                imgs_downloaded[ks] = {img_url_key:None,
                                      img_url_local_key:None}

    return imgs_downloaded,imgs_not_downloaded

def save_to_db(content_urls,preview_urls,img_table,engine):
    
    '''save downloaded content and preview to dataframe'''
#     preview_urls_con
    
#     preview_urls = {key:val for x in preview_urls_con for key,val in x.items()}
#     content_urls = {key:val for x in content_urls_con for key,val in x.items()}
    
    preview_df = pd.DataFrame(preview_urls).T.reset_index()
    content_df = pd.DataFrame(content_urls).T.reset_index()
    merged_df = pd.merge(content_df,preview_df,on='index')
    
    merged_df.columns = ['orig_id','title_img_url','title_img_local','preview_img_link','preview_img_local']
    merged_df.to_sql(img_table,engine,if_exists='append',index=False)
    
