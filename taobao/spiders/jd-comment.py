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
from urllib import quote, unquote

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class JdSpider(scrapy.Spider):
    name = "jdscroll"
    start_urls = ["http://example.com", "http://example.com/foo"]
    
    
    def __init__(self, keyword=None, *args, **kwargs):
        super(JdSpider, self).__init__(*args, **kwargs) 
        global keywords
        keywords=keyword  
        
    def start_requests(self):
    	#下滑加载其他内容
        scriptload = """
           function main(splash)
               local load_element = splash:jsfunc([[
                 function(){{
                    var i = 0;
                    var t=0;
                    t= setInterval(function(){
                            if(i<15){
                                window.scrollTo(100, i * 600);
                            }else{
                                window.clearInterval(t);
                            }
                            i+=1;
                        }, 800)
                    }}
                ]])
                #设置返回资源超时
                splash.resource_timeout = 3.0
                #设置返回响应内容超时
                splash:on_request(function(request)
                     request:set_timeout(3.0)  
                end)
                assert(splash:go(splash.args.url))
                splash:set_custom_headers({
                        [':host']='serach.jd.com',
                        [':method']='GET',
                        [':version']='HTTP/1.1',
                        ['accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        ['accept-language']='zh-CN,zh;q=0.8',
                })
                load_element()
                splash:wait(0.5)
                splash:set_user_agent('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0')
                return splash:html()
        end
        """

        for i in range(1, 101, 1):
            url = 'http://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page=%d&click=0' % (keywords,i)
            self.log(url)
            yield scrapy.Request(url, self.parse_next, meta={
                'splash': {
                    'args': {'lua_source': scriptload, 'url': url},
                    'endpoint': 'execute'
                }
            })

    def parse_next(self, response):
        #点击评论按钮
        scriptclick="""
           function main(splash)
           local click_element = splash:jsfunc([[
	       function() {{
      	 	 var c = document.createEvent("MouseEvents"),
                 
        	 el = document.getElementById("detail-tab-comm");
	         c.initMouseEvent("click",true,true,window,0,0,0,0,0,false,false,false,false,0,null);
        	 el.dispatchEvent(c);
    		}}
	    ]])
  	splash:go(splash.args.url)
        splash:wait(1.5)
 	click_element()
	splash:wait(1.5)
  	return splash:html()
	end
        
        """
        self.log(response.url)
        select = response.xpath("//ul[@class='gl-warp clearfix']/li[@class='gl-item']/div/div[@class='p-name p-name-type-2']/a/@href")
        for i in select.extract():
           
            item_urls = str(urlparse.urljoin('http:', i))+'#comment'           
            yield scrapy.Request(item_urls,callback=self.parse_item,dont_filter=True,meta={
                'splash':{
                    'args':{'lua_source':scriptclick,'url':item_urls},
                     'endpoint': 'execute'
                }
            
            })        
    def parse_item(self,response):
        self.log(response.url)
        #解析评论数据
        select=response.xpath("//div[@class='comments-item']")
       
        items=[]      
        for i in select:
            item=TaobaoItem()
            item['title']=(''.join(i.xpath("div/div[2]/div/text()").extract())).strip()
            items.append(item)
        return items
        #item['title']=response.body
        ##item['title']=response.xpath("//div[@id='name']/h1/text()").extract()
        ##item['price']=response.xpath("//strong[@id='jd-price']/text()").extract()
        #item['url']=response.url
        #item['shopname']=response.xpath("//div[@id='extInfo']/div[@class='seller-infor']/a[@class='name']/text()").extract()
        ##item['title']=response.body
        #return item

