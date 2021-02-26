

from model import db_connect,create_table
from utils import  grap_preview_imgs_urls,grap_content_imgs_urls,get_preview_imgs_url, \
                    get_content_imgs_url,download_imgs


if __name__=='__main__':
    
    uri = 'mysql+pymysql://root:jinzheng1706@139.198.191.224:3308/news_oil'
    engine = db_connect(uri)
    create_table(engine)
    preview_save_dir = '/mnt/img_dir/preview_imgs'
    content_save_dir = '/mnt/img_dir/content_imgs'
    img_table='imgs_location'
    content_urls_con = [] #list for saving all the table procssed content img
    content_urls_not_con = []
    preview_urls_con = [] # list for preview img url to 
    preview_urls_not_con = []
    preview_imgs_urls = grap_preview_imgs_urls(img_table, engine) #noprocessed preview urls
    content_imgs_urls = grap_content_imgs_urls(img_table, engine) #nonprocessed content url
    for table in table_name_pro:
#         ua = UserAgent()
#         user_agent = ua.ie
#         not_down_preview = get_preview_imgs_url(table, engine, preview_imgs_urls)
        imgs_downloaded,imgs_not_downloaded = download_imgs(not_down_preview,
                                                            'preview_img_link','preview_img_local',preview_save_dir,table)
#         preview_urls_con.append(imgs_downloaded)
#         preview_urls_not_con.append(imgs_not_downloaded)
        

        ua = UserAgent()
        user_agent = ua.ie
        not_down_content =  get_content_imgs_url(table, engine, content_imgs_urls)
        imgs_downloaded,imgs_not_downloaded = download_imgs(not_down_content,'title_img_url','title_img_local',
                                                           content_save_dir,table)
        content_urls_con.append(imgs_downloaded)
        content_urls_not_con.append(imgs_not_downloaded)
    
        
