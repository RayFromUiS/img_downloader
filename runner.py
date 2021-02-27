

from model import db_connect,create_table
from utils import  grap_preview_imgs_urls,grap_content_imgs_urls,get_preview_imgs_url, \
                    get_content_imgs_url,download_imgs,save_to_db



if __name__=='__main__':
    
    table_name_pro =['in_en_storage_pro','news_oil_oe_pro','world_oil_pro','hart_energy_pro','cnpc_news_pro','oilfield_tech_pro',\
            'oil_and_gas_pro','jpt_latest_pro','energy_voice_pro','gulf_oil_gas_pro',\
            'energy_pedia_pro','up_stream_pro','oil_price_pro','inen_tech_pro','inen_newenergy_pro',\
            'drill_contractor_pro','rog_tech_pro','natural_gas_pro','rig_zone_pro','offshore_tech_pro',
                  'jwn_energy_pro',
            'energy_year_pro','energy_china_pro','china_five_pro','offshore_energy_pro','iran_oilgas_pro']
    uri = 'mysql+pymysql://root:jinzheng1706@139.198.191.224:3308/news_oil'
    engine = db_connect(uri)
    create_table(engine)
    preview_save_dir = '/mnt/news_img_dir/preview_imgs'
    content_save_dir = '/mnt/news_img_dir/content_imgs'
    img_table='imgs_location'
    content_urls_con = [] #list for saving all the table procssed content img
    content_urls_not_con = []
    preview_urls_con = [] # list for preview img url to 
    preview_urls_not_con = []
    preview_imgs_urls = grap_preview_imgs_urls(img_table, engine) #noprocessed preview urls
    content_imgs_urls = grap_content_imgs_urls(img_table, engine) #nonprocessed content url
    for table in table_name_pro:
        not_down_preview = get_preview_imgs_url(table, engine, preview_imgs_urls)
        preview_imgs_downloaded,imgs_not_downloaded = download_imgs(not_down_preview,
                                                            'preview_img_link','preview_img_local',preview_save_dir,table)

        not_down_content =  get_content_imgs_url(table, engine, content_imgs_urls)
        content_imgs_downloaded,imgs_not_downloaded = download_imgs(not_down_content,'title_img_url','title_img_local',
                                                           content_save_dir,table)

        save_to_db(content_imgs_downloaded,preview_imgs_downloaded,img_table,engine)
        # break
        
        
