import re, sys, os
import paramiko
import logging,requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin,parse_qs
from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, botflow, BotFlow, FlowRoot
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class bangmalih(BotPlugin):

    @botcmd
    def hi(self, msg, args):
        yield "Hallo gw bang malih"
        yield """
                untuk info gunung ketik:
                info namagunung  [sekarang | besok | mingdep]"""

    @botcmd
    def info_cuaca(self, msg, args):
        if args == '':
            yield "Hi gunung apa nih"
        else:    
            gn = "Gunung "+args
            yield gn

    @botcmd
    def info(self, msg, args):

        yield "tunggu yah..."
        info = args.split(' ') 

        nama = info[0]
        date = info[1]
        
        payload ="https://freemeteo.co.id/cuaca"

        search = urljoin(payload,'/cuaca/search/?language=indonesian&country=indonesia&q=gunung+'+nama)                                     
        r = requests.get(search)
       
        soup = BeautifulSoup(r.text,"html.parser")
        a = soup.find_all(class_="Point")
        xx = BeautifulSoup(str(a),"html.parser")
        
        link = []
        for i in xx.find_all('a',href=True):
            if i.text:
                link.append(i['href'])
        try: 
            today= []
            tomorrow = []
            week = []
            gid = []
            if not link:
                yield "Info gunung yang kamu cari tidak tersedia, silahkan coba gunung lain nya"
            else:
                print(link[0])
                link.pop(0)

                today = link[0]
                tomorrow = link[1]
                week = link[2]
        
                if date == 'sekarang':
                    reqbytime = urljoin(r.url,today)
                elif date == 'besok':
                    reqbytime = urljoin(r.url,tomorrow)
                elif date == "mingdep":
                    reqbytime = urljoin(r.url,week)
                else:
                    yield "masukkan waktu yang sesuai [sekarang | besok | mingdep]"
                        
                newr = requests.get(reqbytime)
                
                #decode url to get 'pointid'
                parsed = urlparse(newr.url)
                gid = parse_qs(parsed.query)
                gid = ''.join(gid['gid'])
        
                if date == 'sekarang':
                    rtd = requests.get('https://freemeteo.co.id/Services/Charts/PointFooter?LanguageID=26&pointid='+gid+'&units=Metric&day=Today')
                    srtd = BeautifulSoup(rtd.text,"html.parser")
                    yield srtd.find("div", class_="title").get_text()
                    for sp in srtd.find_all('td'):
                        yield sp.get_text()
                
                if date == 'besok':
                    rtm = requests.get('https://freemeteo.co.id/Services/Charts/PointFooter?LanguageID=26&pointid='+gid+'&units=Metric&day=TodayPlus1')
                    srtm = BeautifulSoup(rtm.text,"html.parser")
                    yield srtm.find("div", class_="title").get_text()
                    for sp in srtm.find_all('td'):
                        yield sp.get_text()
                
                if date == 'mingdep':
                    rwk = requests.get('https://freemeteo.co.id/Services/Charts/PointSevenDaysFooter?LanguageID=26&pointid='+gid+'&units=Metric')
                    srwk = BeautifulSoup(rwk.text,"html.parser")
                    yield srwk.find("div", class_="title").get_text()
                    for sp in srwk.find_all('td'):
                        yield sp.get_text()
                
        except  (RuntimeError, TypeError, NameError) as e: 
            print(e.message)
