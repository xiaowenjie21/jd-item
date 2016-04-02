# -*- coding: utf-8 -*-
import scrapy
import datetime
import urlparse
import socket
import scrapy

from scrapy.loader.processors import MapCompose, Join
from scrapy.loader import ItemLoader
from scrapy.http import Request
import json
import base64
import scrapy
from scrapy.http.headers import Headers
from taobao.items import TaobaoItem
from urllib import quote,unquote

import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class JdSpider(scrapy.Spider):
    name = "jd2"
    start_urls = ["http://example.com", "http://example.com/foo"]
  
     
    def __init__(self, keyword=None, *args, **kwargs):
        super(JdSpider, self).__init__(*args, **kwargs) 
        global keywords
        keywords=keyword
        
    def start_requests(self):
        script2="""
           function main(splash)
               local click_element = splash:jsfunc([[
                 function(){{
                    var i = 0;
                    var t=0;
                    t= setInterval(function(){
                            if(i<9){
                                window.scrollTo(100, i * 700);
                            }else{
                                window.clearInterval(t);
                            }
                            i+=1;
                        }, 700)
                    }}
                ]])

                assert(splash:go(splash.args.url))
                splash:set_custom_headers({
                        [':host']='serach.jd.com',
                        [':method']='GET',
                        [':version']='HTTP/1.1',
                        ['accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        ['accept-language']='zh-CN,zh;q=0.8',
                })
                click_element()
                splash:wait(2.5)
                splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36 OPR/35.0.2066.92')
                return splash:html()
        end
            """          

        for i in range(1,101,1):        
            url2='http://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page=%d&click=0' % (keywords,i)
            yield scrapy.Request(url2,self.parse_next,meta={'splash':{'args':{'lua_source':script2,'url':url2},'endpoint':'execute'} })            
       
   
        
   
      
    def parse_next(self,response):
        
        
        #item['title']=[]
        #item['price']=[] 
        items=[]
        select=response.xpath("//ul[@class='gl-warp clearfix']/li[@class='gl-item']/div")
        for i in select:
            item = TaobaoItem()
            item["title"]=i.xpath("div[@class='p-name p-name-type-2']/a/em/text()").extract()
            item["price"]=i.xpath("div[@class='p-price']/strong/i/text()").extract()
            item['url']=response.url
            items.append(item)
            
        return items
         
