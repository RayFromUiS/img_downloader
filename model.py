from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

# from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect(uri):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    # print('uri',get_project_settings().get("SQL_CONNECT_STRING"))
#     uri='mysql+pymysql://root:password@localhost:3308/news_oil'
    return create_engine(uri)


class ImagesUrl(Base):
    __tablename__ = 'imgs_location'
    id = Column(Integer, primary_key=True)
    orig_id = Column(Integer)
    title = Column(String(1024))
    preview_img_link = Column(String(2048))
    img_urls_new = Column(String(4096))
    preview_img_location = Column(String(1024))
    img_urls_location= Column(String(2048))

def create_table(engine):
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    db_connect()
