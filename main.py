import time
import bs4
import requests
import StellarPlayer
import re
import urllib.parse
import urllib.request
import math
import json
import urllib3

spy = [
        {'name':'88电影资源','api':'http://www.88zy.live/inc/api.php/provide/vod/','datatype':'xml','search':False},
        {'name':'百度资源','api':'https://m3u8.apibdzy.com/api.php/provide/vod/','datatype':'json','search':True},
        {'name':'八戒资源','api':'http://cj.bajiecaiji.com/inc/api.php/provide/vod/','datatype':'xml','search':False},
        {'name':'穿梭资源','api':'https://ok.888hyk.com/api.php/provide/vod/','datatype':'json','search':True},
        {'name':'天空资源','api':'http://api.tiankongapi.com/api.php/provide/vod/','datatype':'json','search':False},
        #{'name':'新奇遇资源','api':'https://www.newqiy.com/api.php/provide/vod/','datatype':'json','search':False},
        {'name':'太初电影','api':'https://www.tcdya.com/api.php/provide/vod/','datatype':'json','search':False},
        {'name':'免费影院','api':'http://www.ruiuri.com/api.php/provide/vod/','datatype':'json','search':True},
        {'name':'快播资源','api':'http://www.kuaibozy.com/api.php/provide/vod/','datatype':'json','search':False},
        {'name':'豆瓣资源','api':'https://api.dbyunzy.com/api.php/provide/vod/','datatype':'json','search':True},
        {'name':'飞鱼资源','api':'https://app.feiyu5.com/api.php/provide/vod/','datatype':'json','search':True},
    ]

class dyxsplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        urllib3.disable_warnings()
        self.medias = []
        self.allmovidesdata = {}
        self.mediaclass = []
        self.pageindex = 0
        self.pagenumbers = 0
        self.apiurl = ''
        self.apitype = ''
        self.cur_page = ''
        self.max_page = ''
        self.nextpg = ''
        self.previouspg = ''
        self.firstpg = ''
        self.lastpg = ''
        self.pg = ''
        self.wd = ''
        self.ids = ''
        self.tid = ''
    
    def start(self):
        super().start()
        
    
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,600,'',controls)        
    
    def makeLayout(self):
        mainmenulist = []
        for cat in spy:
            mainmenulist.append({'type':'link','name':cat['name'],'@click':'onMainMenuClick','width':80})
        secmenu_layout = [
            {'type':'link','name':'title','@click':'onSecMenuClick'}
        ]

        mediaclass_layout = [
            {'type':'link','name':'type_name','textColor':'#ff00ff', '@click':'on_class_click'}
        ]
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_grid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':15,'height':0.15, '@click':'on_grid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {
                'group':[
                    {'type':'edit','name':'search_edit','label':'搜索','width':0.4},
                    {'type':'button','name':'搜索','@click':'onSearch','width':80}
                ],
                'width':1.0,
                'height':30
            },
            {'type':'space','height':10},
            {'group':mainmenulist,'height':30},
            {'type':'space','height':5},
            {'type':'grid','name':'mediaclassgrid','itemlayout':mediaclass_layout,'value':self.mediaclass,'itemheight':30,'itemwidth':80,'height':70},
            {'type':'space','height':5},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':240,'itemwidth':150},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','@click':'onClickNextPage'},
                            {'type':'link','name':'末页','@click':'onClickLastPage'},
                            {'type':'label','name':'max_page',':value':'max_page'},
                        ]
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
    
    def onMainMenuClick(self,pageId,control,*args):
        self.loading()
        self.apiurl = ''
        apidatatype = ''
        for cat in spy:
            if control == cat['name']:
                self.apiurl = cat['api']
                self.apitype = cat['datatype']
                self.getMediaType()
                self.pg = ''
                self.wd = ''
                self.tid = ''
                self.getMediaList()
                break
        self.loading(True)    
            
    def getMediaType(self):
        self.mediaclass = []
        url = self.apiurl + '?ac=list'
        print(url)
        res = requests.get(url,timeout = 3,verify=False)
        if res.status_code == 200:
            if self.apitype == 'json':
                jsondata = json.loads(res.text, strict = False)
                if jsondata:
                    self.mediaclass = jsondata['class']
                    self.getPageInfoJson(jsondata)
            else:
                bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                selector = bs.select('rss > class >ty')
                if selector:
                    for item in selector:
                        t_id = int(item.get('id'))
                        t_name = item.string
                        self.mediaclass.append({'type_id':t_id,'type_name':t_name})
                    self.getPageInfoXML(bs)
        else:
            self.player and self.player.toast('main','请求失败')
        self.player.updateControlValue('main','mediaclassgrid',self.mediaclass)
        
    def getMediaList(self):
        self.medias = []
        if self.apiurl == '':
            return
        url = self.apiurl + '?ac=videolist'
        if self.wd != '':
            self.tid = ''
            url = url + '&wd=' +self.wd
        if self.tid != '':
            url = url + self.tid
        if self.pg != '':
            url = url + self.pg
        print(url)
        res = requests.get(url,timeout = 5,verify=False)
        if res.status_code == 200:
            if self.apitype == 'json':
                jsondata = json.loads(res.text, strict = False)
                if jsondata:
                    jsonlist = jsondata['list']
                    for item in jsonlist:
                        self.medias.append({'ids':item['vod_id'],'title':item['vod_name'],'picture':item['vod_pic']})
                    self.getPageInfoJson(jsondata)
            else:
                bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                selector = bs.select('rss > list > video')
                if selector:
                    for item in selector:
                        nameinfo = item.select('name')
                        picinfo = item.select('pic')
                        idsinfo = item.select('id')
                        if nameinfo and picinfo and idsinfo:
                            name = nameinfo[0].string
                            pic = picinfo[0].string
                            ids = int(idsinfo[0].string)
                            self.medias.append({'ids':ids,'title':name,'picture':pic})
                self.getPageInfoXML(bs)
        else:
            self.player and self.player.toast('main','请求失败')
        self.player.updateControlValue('main','mediagrid',self.medias)
    
    def on_class_click(self, page, listControl, item, itemControl):
        if self.apiurl == '':
            return
        self.loading()
        typeid = self.mediaclass[item]['type_id']
        self.wd = ''
        self.pg = ''
        self.tid = '&t=' + str(typeid)
        self.getMediaList()
        self.loading(True)
    
    def getPageInfoJson(self,jsondata):
        self.pageindex = jsondata['page']
        self.pagenumbers = jsondata['pagecount']
        self.nextpg = '&pg=' + str(int(self.pageindex) + 1)
        if self.pageindex == 1:
            self.previouspg = '&pg=1'
        else:
            self.previouspg = '&pg=' + str(int(self.pageindex) - 1)
        self.firstpg = '&pg=1'
        self.lastpg = '&pg=' + str(self.pagenumbers)
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'
    
    def getPageInfoXML(self,bs):
        self.nextpg = ''
        self.previouspg = ''
        self.firstpg = ''
        self.lastpg = ''
        selector = bs.select('rss > list')
        self.pagenumbers = 0
        self.pageindex = 0
        if selector:
            self.pageindex = int(selector[0].get('page'))
            self.pagenumbers = int(selector[0].get('pagecount'))
            self.cur_page = '第' + str(self.pageindex) + '页'
            self.max_page = '共' + str(self.pagenumbers) + '页'
            if self.pageindex < self.pagenumbers:
                self.nextpg = '&pg=' + str(int(self.pageindex) + 1)
            else:
                self.nextpg = '&pg=' + str(self.pagenumbers)
            if self.pageindex == 1:
                self.previouspg = '&pg=1'
            else:
                self.previouspg = '&pg=' + str(int(self.pageindex) - 1)
            self.firstpg = '&pg=1'
            self.lastpg = '&pg=' + str(self.pagenumbers)
    
    def onSearch(self, *args):
        search_word = self.player.getControlValue('main','search_edit').strip()
        if search_word == '':
            self.player.toast("main","搜索条件不能为空")
            return   
        if self.apiurl == '':
            self.player.toast("main","请先选择资源站")
            return
        for cat in spy:
            if self.apiurl == cat['api']:
                if cat['search'] == False:
                    self.player.toast('main','该资源站不支持搜索')
                    return
        self.loading()
        self.wd = search_word
        self.getMediaList()
        self.loading(True)        
        
    def on_grid_click(self, page, listControl, item, itemControl):
        videoid = self.medias[item]['ids']
        url = self.apiurl + '?ac=videolist&ids=' + str(videoid)
        print(url)
        self.onGetMediaPage(url)
        
    def onGetMediaPage(self,url):
        res = requests.get(url,timeout = 5,verify=False)
        if res.status_code == 200:
            if self.apitype == 'json':
                jsondata = json.loads(res.text, strict = False)
                if jsondata:
                    medialist = jsondata['list']
                    if len(medialist) > 0:
                        info = medialist[0]
                        playfrom = info["vod_play_from"]
                        playnote = '$$$'
                        playfromlist = playfrom.split(playnote)
                        playurl = info["vod_play_url"]
                        playurllist = playurl.split(playnote)
                        sourcelen = len(playfromlist)
                        sourcelist = []
                        for i in range(sourcelen):
                            if playfromlist[i].find('m3u8') >= 0:
                                urllist = [] 
                                urlstr = playurllist[i]
                                jjlist = urlstr.split('#')
                                for jj in jjlist:
                                    jjinfo = jj.split('$')
                                    urllist.append({'title':jjinfo[0],'url':jjinfo[1]})
                                sourcelist.append({'flag':playfromlist[i],'medias':urllist})
                        mediainfo = {'name':info['vod_name'],'pic':info['vod_pic'],'actor':'演员:' + info['vod_actor'].strip(),'content':'简介:' + info['vod_content'].strip(),'source':sourcelist}
                        self.getPageInfoJson(jsondata)
                        self.createMediaFrame(mediainfo)
                        return
            else:
                bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                selector = bs.select('rss > list > video')
                if len(selector) > 0:
                    info = selector[0]
                    nameinfo = info.select('name')[0]
                    name = nameinfo.text
                    picinfo = info.select('pic')[0]
                    pic = picinfo.text
                    actorinfo = info.select('actor')[0]
                    actor = '演员:' + actorinfo.text.strip()
                    desinfo = info.select('des')[0]
                    des = '简介:' + desinfo.text.strip()
                    dds = info.select('dl > dd')
                    sourcelist = []
                    for dd in dds:
                        ddflag = dd.get('flag')
                        ddinfo = dd.text
                        m3u8list = []
                        if ddflag.find('m3u8') >= 0:
                            urllist = ddinfo.split('#')
                            n = 1
                            for source in urllist:
                                urlinfo = source.split('$')
                                if len(urlinfo) == 1:
                                    m3u8list.append({'title':'第' + str(n) + '集','url':ddinfo})
                                else:
                                    m3u8list.append({'title':urlinfo[0],'url':urlinfo[1]})
                                n = n + 1
                            sourcelist.append({'flag':ddflag,'medias':m3u8list})
                    mediainfo = {'name':name,'pic':pic,'actor':actor,'content':des,'source':sourcelist}
                    self.getPageInfoXML(bs)
                    self.createMediaFrame(mediainfo)
                    return
        self.player and self.player.toast('main','无法获取视频信息')
        return
        
    def createMediaFrame(self,mediainfo):
        if len(mediainfo['source']) == 0:
            self.player.toast('main','该视频没有可播放的视频源')
            return
        actmovies = []
        if len(mediainfo['source']) > 0:
            actmovies = mediainfo['source'][0]['medias']
        print(actmovies)
        medianame = mediainfo['name']
        self.allmovidesdata[medianame] = {'allmovies':mediainfo['source'],'actmovies':actmovies}
        xl_list_layout = {'type':'link','name':'flag','textColor':'#ff0000','width':0.6,'@click':'on_xl_click'}
        movie_list_layout = {'type':'link','name':'title','@click':'on_movieurl_click'}
        controls = [
            {'type':'space','height':5},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':mediainfo['pic'],'width':0.25},
                    {'group':[
                            {'type':'label','name':'actor','textColor':'#555500','value':mediainfo['actor'],'height':0.3},
                            {'type':'label','name':'info','textColor':'#005555','value':mediainfo['content'],'height':0.7}
                        ],
                        'dir':'vertical',
                        'width':0.75
                    }
                ],
                'width':1.0,
                'height':250
            },
            {'group':
                {'type':'grid','name':'xllist','itemlayout':xl_list_layout,'value':mediainfo['source'],'separator':True,'itemheight':30,'itemwidth':120},
                'height':40
            },
            {'type':'space','height':5},
            {'group':
                {'type':'grid','name':'movielist','itemlayout':movie_list_layout,'value':actmovies,'separator':True,'itemheight':30,'itemwidth':60},
                'height':200
            }
        ]
        self.doModal(mediainfo['name'],750,500,'',controls)   
        
    def onClickFirstPage(self, *args):
        if self.firstpg == '':
            return
        self.pg = self.firstpg
        self.loading()
        self.getMediaList()
        self.loading(True)
        
    def onClickFormerPage(self, *args):
        if self.previouspg == '':
            return
        self.pg = self.previouspg
        self.loading()
        self.getMediaList()
        self.loading(True)
    
    def onClickNextPage(self, *args):
        if self.nextpg == '':
            return
        self.pg = self.nextpg
        self.loading()
        self.getMediaList()
        self.loading(True)
        
    def onClickLastPage(self, *args):
        if self.lastpg == '':
            return
        self.pg = self.lastpg
        self.loading()
        self.getMediaList()
        self.loading(True)
                
    def on_movieurl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['actmovies']) > item:
            playurl = self.allmovidesdata[page]['actmovies'][item]['url']
            print(playurl)
            self.player.play(playurl)
            
    def playMovieUrl(self,playpageurl):
        return
        
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = dyxsplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()