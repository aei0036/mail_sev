#====================================================================================================
# Import API
#====================================================================================================
from hashlib import new
from sunau import AUDIO_FILE_ENCODING_MULAW_8
from time import sleep
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
from datetime import timedelta

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import pandas as pd
import webbrowser
import traceback
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#====================================================================================================
# e-mail info.
#====================================================================================================
smtp_info = dict({"smtp_server" : "smtp.worksmobile.com", # SMTP 서버 주소
                  "smtp_user_id" : "ip-radar@dodamip.com", 
                  "smtp_user_pw" : "YUOEIpA5aGRZ",
                  "smtp_port" : 587}) # SMTP 서버 포트

#====================================================================================================
# Global Val
#====================================================================================================
# 팀 별 기본 검색 키워드 셋팅
keyword0 = '특허 지재권 지식재산 사업화 IP '
keyword1 = '평가 기술가치 특허가치 '
keyword2 = "무형자산 지적재산 기술가치평가 기술평가"
gb_search_list_fi = []
mail_title = "[특허법인 도담] 지식재산(IP) 관련 지원사업 안내"
mail_content_title = "지식재산 관련 지원사업 안내"
mail_content_text = "아래와 같은 IP지원사업이 공고되어 안내드립니다.<br>지원 사업 내용을 확인해보시고, 관심 있으시면 언제든지 편하게 연락주세요.<br>감사합니다."

#====================================================================================================
# TEST Val
#====================================================================================================
SCRAPING_FLAG = TRUE
#SCRAPING_FLAG = FALSE

def search_main(search_date):
    web_options = webdriver.ChromeOptions()
    #web_options.add_argument("headless")
    #web_options.add_argument("--start-fullscreen")
    driver = webdriver.Chrome(ChromeDriverManager().install(),  options=web_options)
    driver.set_window_size(1680,1050)
    #driver_unhide = webdriver.Chrome(ChromeDriverManager().install())
    
    search_list = []
    print("검색 기준일 :", search_date)

    if SCRAPING_FLAG: #kista(한국특허전략개발원):
        try:
            #사업정보 페이지
            driver.get("https://www.kista.re.kr/user/board.do?bbsId=BBSMSTR_000000000382")
            driver.implicitly_wait(1)

            #팝업차단함수
            popup_handler = driver.window_handles
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])


            table = driver.find_element_by_class_name('table_wrap')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.kista.re.kr/user/board.do?bbsId=BBSMSTR_000000000382"
            for index, value in enumerate(rows):

                announce_data = value.find_elements_by_tag_name("td")[3].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                
                if datetime.strptime(announce_data,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                    
                    href=href_pre
                    temp_str = "[전략원] " + announce_data + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

            #입찰공고 페이지
            driver.get("https://www.kista.re.kr/user/board.do?bbsId=BBSMSTR_000000000442")
            driver.implicitly_wait(1)

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            table = driver.find_element_by_class_name('table_wrap')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.kista.re.kr/user/board.do?bbsId=BBSMSTR_000000000442"
            for index, value in enumerate(rows):

                announce_state = value.find_elements_by_tag_name("td")[2].text

                body=value.find_elements_by_tag_name("td")[1]
                
                if announce_state == "진행중":
                    href=href_pre
                    temp_str = "[전략원] " + announce_state + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
           print("kista(한국특허전략개발원) scraping exception!!") 
           print("exception message : ",e)

    if SCRAPING_FLAG: #koipa(한국지식재산보호원):
        try:
            driver.get("https://www.koipa.re.kr/home/board/brdList.do?menu_cd=000041")
            driver.implicitly_wait(1)
            print("koipa(한국지식재산보호원) scraping")


            #팝업차단함수
            popup_handler = driver.window_handles
        
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            table = driver.find_element_by_class_name("tbl-group-inr")
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.koipa.re.kr/home/board/brdDetail.do?menu_cd=000041&num="
            for index, value in enumerate(rows):

                announce_date = value.find_elements_by_tag_name("td")[4].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                    href = href_pre + body.find_element_by_tag_name("a").get_attribute('href').split("('")[1].split("')")[0]
                    temp_str = "[보호원] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
        except Exception as e:
           print("koipa(한국지식재산보호원) scraping exception!!") 
           print("exception message : ",e)

    if SCRAPING_FLAG: #Kautm(한국대학기술이전협회):
        try:
            driver.get("http://www.kautm.net/bbs/?so_table=tlo_news&category=business")
            driver.implicitly_wait(1)
            print("kautm(한국대학기술이전협회) scraping")

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            table = driver.find_element_by_class_name("listTable")
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "http://www.kautm.net/"
            for index, value in enumerate(rows):

                announce_date = value.find_elements_by_tag_name("td")[3].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                    
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[KAUTM] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        
                    search_list.append(temp_str)
        except Exception as e:
           print("Kautm(한국대학기술이전협회) scraping exception!!") 
           print("exception message : ",e)

    if SCRAPING_FLAG: #innopolis(연구개발특구진흥재단):
        try:
            driver.get("https://www.innopolis.or.kr/newBusiness?menuId=MENU01028")
            driver.implicitly_wait(1)
            print("innopolis(연구개발특구진흥재단) scraping")

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            #table = driver.find_element_by_css_selector("#detail-contents > div.business-slider-area > div > div.bx-viewport")
            tbody = driver.find_element_by_css_selector("#business-city1-1")
            rows = tbody.find_elements_by_tag_name('li')
            
            #print(rows[0])
            href_pre = "https://www.innopolis.or.kr"

            for index, value in enumerate(rows):

                announce_date = value.find_element_by_class_name('date').text.split('~')[0].replace('-','.')
                body=value.find_element_by_class_name('title').text
                        
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                    
                    href = value.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[INNOPOLIS] " + announce_date + "  "+ body.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
        except Exception as e:
           print("innopolis(연구개발특구진흥재단) scraping exception!!") 
           print("exception message : ",e)

    if SCRAPING_FLAG: #compa(과학기술일자리진흥원):
        try:        
            driver.get("https://www.compa.re.kr/cop/bbs/selectBoardList.do;jsessionid=0E67D131CE4444EE0EB1266CF5721EDA?bbsId=BBSMSTR_DDDDDDDDDDDD")
            driver.implicitly_wait(10)
            print("compa(과학기술일자리진흥원) scraping")

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])
            
            table = driver.find_element_by_class_name("CommonArea")
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.compa.re.kr/cop/bbs/selectBoardArticle.do?bbsId=BBSMSTR_DDDDDDDDDDDD&nttId="
            href_post = "&bbsTyCode=BBST01&bbsAttrbCode=BBSA01&authFlag=&pageIndex=1&searchCnd=&searchWrd=&goMenuNo="

            for index, value in enumerate(rows):

                announce_date = value.find_elements_by_tag_name("td")[3].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                    xpath = '//*[@id="S_Contents"]/div[2]/div[3]/table/tbody/input[' + str(2+index*9) + ']'
                    href_mid = value.find_element_by_xpath(xpath).get_attribute("value")
                    href = href_pre + href_mid + href_post
                    
                    temp_str = "[과학기술일자리진흥원] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
        except Exception as e:
           print("compa(과학기술일자리진흥원) scraping exception!!") 
           print("exception message : ",e)

    if SCRAPING_FLAG: #technopark:
        try:
            #driver = webdriver.Chrome('chromedriver')
            driver.get("http://www.technopark.kr/businessboard")
            driver.implicitly_wait(1)
            print("technopart scraping")

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            Location_list = driver.find_element_by_class_name("list").find_elements_by_tag_name('a')
            
            sub_driver = webdriver.Chrome(ChromeDriverManager().install(),  options=web_options)

            for index, value in enumerate(Location_list):
                #print(index," | ",value.get_attribute('href'))

                if index != 0:  #0 인 경우(전체 공고) 패스, 지역공고만 크롤링 수행
                    sub_driver.get(value.get_attribute('href'))
                    sub_driver.implicitly_wait(1)
                    
                    table = sub_driver.find_element_by_class_name("tb_board_list")
                    tbody = table.find_element_by_tag_name("tbody")
                    rows = tbody.find_elements_by_tag_name("tr")
                    for j_index, j_value in enumerate(rows):

                        announce_date = j_value.find_elements_by_tag_name("td")[4].text
                        body=j_value.find_elements_by_tag_name("td")[2]
                        location=j_value.find_elements_by_tag_name("td")[1].text
                        
                        if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):
                            href = body.find_element_by_tag_name("a").get_attribute('href')
                            temp_str = "[테크노파크][" + location +"] "+ announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                            search_list.append(temp_str)
            
            sub_driver.close()
        except Exception as e:
            print("technopark scraping exception!!")
            print("exception message : ",e)
                
    if SCRAPING_FLAG: #kaips(한국지식재산서비스협회):
        try:
            print("kaips(한국지식재산서비스협회) scraping")
            for i in range(1,3):
                driver.get("http://www.kaips.or.kr/bbs_shop/list.htm?page="+str(i)+"&board_code=kaips_4")
                driver.implicitly_wait(1)
                

                #팝업차단함수
                popup_handler = driver.window_handles
                
                for popup_i in popup_handler:
                    if popup_i != popup_handler[0]:
                        driver.switch_to.window(popup_i)
                        driver.close()
                driver.switch_to.window(popup_handler[0])
                
                tbody = driver.find_element_by_xpath('//*[@id="list_board"]/ul[3]')
                rows = tbody.find_elements_by_tag_name('li')
                for index, value in enumerate(rows):
                    announce_date = value.find_elements_by_tag_name("div")[3].text.replace('-','.')
                    body=value.find_elements_by_tag_name("div")[1]

                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                        href = body.find_element_by_tag_name("a").get_attribute('href')
                        temp_str = "[지식재산서비스협회] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
        except Exception as e:
            print("kaips(한국지식재산서비스협회) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #RIPC(지역지식재산센터):
        try: 
            driver.get("https://pms.ripc.org/pms/biz/applicant/notice/list.do")
            driver.implicitly_wait(1)
            print("RIPC(지역지식재산센터) scraping")

            #팝업차단함수
            popup_handler = driver.window_handles
            
            for popup_i in popup_handler:
                if popup_i != popup_handler[0]:
                    driver.switch_to.window(popup_i)
                    driver.close()
            driver.switch_to.window(popup_handler[0])

            Location_list = driver.find_element_by_class_name("checkbox_grp")
            search_button = driver.find_element_by_class_name("srch-group-text")
            Location_but = Location_list.find_elements_by_tag_name('div')

            # 목록수 50건 선택 (드롭다운)
            recordcountperpage = driver.find_element_by_name('recordCountPerPage')
            selector = Select(recordcountperpage)
            selector.select_by_value('50')

            for index, location in enumerate(Location_but):
                if index != 0:  #0 인 경우(전체 공고) 패스, 지역공고만 크롤링 수행
                    location.find_element_by_tag_name("label").click()
                    search_button.click()
                    sleep(1)
                    
                    table = driver.find_element_by_class_name("table_area")
                    tbody = table.find_element_by_tag_name("tbody")
                    rows = tbody.find_elements_by_tag_name("tr")

                    for j_index, value in enumerate(rows):
                        if j_index != 0: 
                            if value.find_elements_by_tag_name("td")[0].text != '데이터가 없습니다':
                                announce_date = value.find_elements_by_tag_name("td")[4].text.split(' ')[0].replace('-','.')
                                body=value.find_elements_by_tag_name("td")[3]
                                
                                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                                    href = "https://pms.ripc.org" + body.get_attribute('onClick').split("'")[1]
                                    temp_str = "[RIPC][" + location.find_element_by_tag_name("label").text +"] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                                    search_list.append(temp_str)
                    
                    location.click()
        except Exception as e:
            print("RIPC(지역지식재산센터) scraping exception!!")
            print("exception message : ",e)


    """if 0:#SCRAPING_FLAG: #RIPC(서울센터) / ripc통합 사이트에서 조회 가능하기에 동작x
        try:
            driver.get("https://www.ipseoul.kr/board/listView.do?boardCode=B00001")
            driver.implicitly_wait(1)
            print("RIPC(서울센터) scraping")

            table = driver.find_element_by_class_name('table_list')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.ipseoul.kr/board/detailView.do?boardCode=B00001&articleSeq="
            for index, value in enumerate(rows):
                if index != 0: 
                    announce_date = value.find_elements_by_tag_name("td")[2].text.replace('-','.')
                    body=value.find_elements_by_tag_name("td")[1]
                    
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                        href = href_pre + body.find_element_by_tag_name("a").get_attribute('href').split("'")[1]
                        temp_str = "[RIPC][서울] " + announce_date + "  "+ body.find_element_by_tag_name("a").get_attribute('title').replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
        except Exception as e:
            print("RIPC(서울센터) scraping exception!!")
            print("exception message : ",e)"""

    if SCRAPING_FLAG: #kipa(발명진흥회):
        try: 
            driver.get("https://www.kipa.org/kipa/notice/kw_0403_01.jsp?")
            driver.implicitly_wait(1)
            print("kipa(발명진흥회) scraping")

            table = driver.find_element_by_class_name('list_table')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[2].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[발명진흥회] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
        except Exception as e:
            print("KIPA(발명진흥회) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #JCIA(전남정보문화산업진흥원):
        try: 
            driver.get("https://jcia.or.kr/cf/information/notice/business.do")
            driver.implicitly_wait(1)
            print("JCIA(전남정보문화산업진흥원) scraping")

            table = driver.find_element_by_class_name('tblBoardBox')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[5].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[2]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):    
                    href = "https://jcia.or.kr/cf/Board/" + body.find_element_by_tag_name("a").get_attribute('OnClick').split("'")[1] + "/detailView.do"
                    temp_str = "[전남정보문화산업진흥원][전남] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
        except Exception as e:
            print("JCIA(전남정보문화산업진흥원) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #한국저작권위원회:
        try: 
            driver.get("https://www.copyright.or.kr/notify/notice/list.do")
            driver.implicitly_wait(1)
            print("한국저작권위원회 scraping")

            table = driver.find_element_by_class_name('sub-con')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[2].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[한국저작권위원회] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("한국저작권위원회 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #대구디지털산업진흥원:
        try: 
            driver.get("https://dip.or.kr/home/notice/businessbbs/boardList.ubs?fboardcd=business")
            driver.implicitly_wait(1)
            print("대구디지털산업진흥원 scraping")

            table = driver.find_element_by_class_name('board__list')
            #tbody = table.find_element_by_tag_name("tbody")
            rows = table.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_element_by_class_name('date').text.replace('-','.')
                body=value.find_element_by_class_name('title')
                
                href_pre = "https://dip.or.kr/home/notice/businessbbs/boardRead.ubs?sfpsize=10&fboardcd=business&fboardnum="
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                    href = href_pre + body.find_element_by_tag_name("a").get_attribute('href').split("'")[3]
                    temp_str = "[대구디지털산업진흥원][대구] " + announce_date + "  "+ body.text.split('\n')[0].replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("대구디지털산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #광주정보문화산업진흥원:
        try: 
            driver.get("https://www.gicon.or.kr/board.es?mid=a10204000000&bid=0003")
            driver.implicitly_wait(1)
            print("광주정보문화산업진흥원 scraping")

            table = driver.find_element_by_class_name('board_list')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[2].text.split(' ')[0]
                body=value.find_elements_by_tag_name("td")[1]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[광주정보문화산업진흥원][광주] " + announce_date + "  "+ body.text.replace('\n','_').replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("광주정보문화산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #전북바이오융합산업진흥원:
        try: 
            driver.get("https://www.jif.re.kr/board/list.do?boardUUID=53473d307cb77a53017cb7e09b8e0003&menuUUID=53473d307cb7118c017cb71940970029")
            driver.implicitly_wait(1)
            print("전북바이오융합산업진흥원 scraping")

            table = driver.find_element_by_class_name('tbl_01')
            tbody = table.find_element_by_tag_name("tbody")
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "https://www.jif.re.kr/board/view.do?boardUUID=53473d307cb77a53017cb7e09b8e0003&menuUUID=53473d307cb7118c017cb71940970029&boardArticleUUID="
            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[3].text.split(' ')[0].replace('-','.')
                body=value.find_elements_by_tag_name("td")[2]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = href_pre + body.find_element_by_tag_name("a").get_attribute('Onclick').split("'")[1]
                    temp_str = "[전북바이오융합산업진흥원][전북] " + announce_date + "  "+ body.text.replace('\n','_').replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("전북바이오융합산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #BIZ INFO(기업마당):
    #-------------------------------------------------------------------------------
    # 여러 지자체 및 중앙부처에서 공고를 가져와 보여주는 사이트로 하루에도 올라오는 공고가 매우 많음
    # 따라서, 각 카테고리(금융/기술 등등) 별로 1~9페이지까지 스크래핑 하도록 구현함
    # 1~9페이지 스크래핑 중, 검색일 이전 공고 확인 시 break
    #-------------------------------------------------------------------------------
        try: 
            driver.get("https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do")
            driver.implicitly_wait(1)
            print("BIZ INFO(기업마당) scraping")

            content_list = driver.find_element_by_class_name('os-content')
            content_buts = content_list.find_elements_by_tag_name('div')

            sub_driver = webdriver.Chrome(ChromeDriverManager().install(),  options=web_options)
            break_flag = FALSE
            for index, content_but in enumerate(content_buts):
                for page_index in range(1,10):
                    if index != 0:  #0 인 경우(전체 공고) 패스
                        sub_driver.get("https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do?hashCode="+content_but.find_element_by_tag_name('a').get_attribute('id') + "&cpage=" + str(page_index))
                        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,'//*[@id="articleSearchForm"]/div[2]/div[4]/table/tbody/tr[1]/td[1]')))
                        #sub_driver.implicitly_wait(1)
                        
                        table = sub_driver.find_element_by_class_name("table_Type_1")
                        tbody = table.find_element_by_tag_name("tbody")
                        rows = tbody.find_elements_by_tag_name("tr")

                        for j_index, value in enumerate(rows):
                            announce_date = value.find_elements_by_tag_name("td")[6].text.replace('-','.')
                            body=value.find_elements_by_tag_name("td")[2]
                            if body.text[0] == '[':
                                announce_location = body.text.split(']')[0].split('[')[1]
                            else:
                                announce_location = '전국'
    
                            if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"):                  
                                href = body.find_element_by_tag_name("a").get_attribute('href')                            
                                temp_str = "[BizInfo][" + announce_location + "] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                                search_list.append(temp_str)

                            if datetime.strptime(announce_date,"%Y.%m.%d")<datetime.strptime(search_date,"%Y.%m.%d"):
                                break_flag = TRUE
                                break
                    if break_flag == TRUE:
                        break_flag = FALSE
                        break
            sub_driver.close()
            
        except Exception as e:
            print("BIZ INFO(기업마당) scraping exception!!")
            print("exception message : ",traceback.format_exc())

    if FALSE: #중소벤처기업진흥공단:
        try: 
            driver.get("http://kosmes.or.kr/sbc/SH/NTS/SHNTS001M0.do")
            driver.implicitly_wait(1)
            print("중소벤처기업진흥공단 scraping")

            table = driver.find_element_by_class_name('gridBodyTable')
            tbody = table.find_element_by_id('AXGridTarget_AX_tbody')
            rows = tbody.find_elements_by_tag_name("tr")
            href_pre = "http://kosmes.or.kr/sbc/SH/NTS/SHNTS001F0.do?seqNo="
            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[3].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[2]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = href_pre + body.find_element_by_tag_name("a").get_attribute('Onclick').split("(")[1].split(")")[0]
                    temp_str = "[중소벤처기업진흥공단] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("중소벤처기업진흥공단 scraping exception!!")
            print("exception message : ",e)

    """if 0: #SCRAPING_FLAG: #성남산업단지관리공단:  / 유효한 공고가 많지 않아 보이므로 일단 0으로 설정
        try: 
            driver.get("https://snic.or.kr/Info/notice")
            driver.implicitly_wait(1)
            print("성남산업단지관리공단 scraping")

            table = driver.find_element_by_id('notice_table')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                
                # 해당 사이트 공고일자 형식이 표준화 되어있지 않음(yyyy-mm-dd / yyyy-mm-dd ~ yyyy-mm-dd / yyyymmdd 3가지가 혼합되어 사용되고 있음)
                # 혼용된 공고일자 형식을 통합함
                temp_announce_date = value.find_elements_by_tag_name("td")[2].text.split(' ')[0]
                if(len(temp_announce_date) == 7):
                    announce_date = temp_announce_date[:4] + '.0' + temp_announce_date[4:5] + '.' + temp_announce_date[5:]
                elif(len(temp_announce_date) == 8):
                    announce_date = temp_announce_date[:4] + '.' + temp_announce_date[4:6] + '.' + temp_announce_date[6:]
                else:
                    announce_date = temp_announce_date.replace('-','.')

                body=value.find_elements_by_tag_name("td")[1]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[성남산업단지관리공단][성남] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("성남산업단지관리공단 scraping exception!!")
            print("exception message : ",e)"""

    if SCRAPING_FLAG: #부산정보산업진흥원:
        try: 
            for page_index in range(1,10):
                driver.get("http://www.busanit.or.kr/board/list.asp?bcode=notice&ipage="+ str(page_index))
                driver.implicitly_wait(1)
                print("부산정보산업진흥원 scraping")

                table = driver.find_element_by_class_name('bbs_ltype')
                tbody = table.find_element_by_tag_name('tbody')
                rows = tbody.find_elements_by_tag_name("tr")
                break_flag = FALSE

                for index, value in enumerate(rows):
                    
                        announce_date = value.find_elements_by_tag_name("td")[2].text.replace('-','.')
                        body=value.find_elements_by_tag_name("td")[1]
                        if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                            href = body.find_element_by_tag_name("a").get_attribute('href')
                            temp_str = "[부산정보산업진흥원][부산] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                            search_list.append(temp_str)
                        
                        if datetime.strptime(announce_date,"%Y.%m.%d")<datetime.strptime(search_date,"%Y.%m.%d"):
                            break_flag = TRUE
                            break

                if break_flag == TRUE:
                        break_flag = FALSE
                        break
                        
        except Exception as e:
            print("부산정보산업진흥원 scraping exception!!")
            print("exception message : ",e)

    """if 0: #SCRAPING_FLAG: #메타버스진흥원:  / 사이트폐쇄
        try: 
            driver.get("http://www.metaversehub.kr/bbs/board.php?tbl=bbs51")
            driver.implicitly_wait(1)
            print("메타버스진흥원 scraping")

            table = driver.find_element_by_class_name('basic_bbs_list')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")
            for index, value in enumerate(rows):
                if index != 0:
                    announce_date = "20" + value.find_elements_by_tag_name("td")[3].text
                    body=value.find_elements_by_tag_name("td")[1]
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = body.find_element_by_tag_name("a").get_attribute('href')
                        temp_str = "[메타버스진흥원] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)

        except Exception as e:
            print("메타버스진흥원 scraping exception!!")
            print("exception message : ",e)"""

    if SCRAPING_FLAG: #충북글로벌마케팅시스템 - 시책사업:
        try: 
            driver.get("https://cbgms.chungbuk.go.kr/export/joinBusinessList.jsp?busi_section=1")
            driver.implicitly_wait(1)
            print("충북글로벌마케팅 scraping")

            table = driver.find_element_by_class_name('basic_table')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")
            for index, value in enumerate(rows):
                announce_date = "20" + value.find_elements_by_tag_name("td")[6].text
                body=value.find_elements_by_tag_name("td")[2]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = "https://cbgms.chungbuk.go.kr/export/joinBusinessView.jsp?busi_support_cd=" + body.find_element_by_tag_name("a").get_attribute('Onclick').split("'")[1]
                    temp_str = "[충북글로벌마케팅][충북] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)

        except Exception as e:
            print("충북글로벌마케팅 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #군포산업진흥원:
        try: 
            driver.get("https://gpipa.or.kr/sub05/sub05_02.html")
            driver.implicitly_wait(1)
            print("군포산업진흥원 scraping")

            table = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")
            for index, value in enumerate(rows):
                if index != 0 and index%2 == 0:   #해당 사이트의 경우, 사업 공고가 짝수 tr마다 기재되어 있음
                    announce_date = value.find_elements_by_tag_name("td")[4].text.replace('-','.')
                    body=value.find_elements_by_tag_name("td")[2]
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = body.find_element_by_tag_name("a").get_attribute('href')
                        temp_str = "[군포산업진흥원][군포] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)

        except Exception as e:
            print("군포산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #안양산업진흥원:
        try:
            print("안양산업진흥원 scraping")
            page_var = ['sbtp0003.do?menuId=851','sbtp0002.do?menuId=850','sbtp0010.do?menuId=1169','sbtp0004.do?menuId=853']
            for page_index in range(len(page_var)):
                driver.get("https://www.aca.or.kr/support/supportBizList/"+page_var[page_index])
                driver.implicitly_wait(1)
                

                table = driver.find_element_by_class_name('ttable-responsive')
                tbody = table.find_element_by_tag_name('tbody')
                rows = tbody.find_elements_by_tag_name("tr")
                for index, value in enumerate(rows):
                    announce_date = value.find_elements_by_tag_name("td")[2].text.split('~')[0].replace('-','.')
                    body=value.find_elements_by_tag_name("td")[1]
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = body.find_element_by_tag_name("a").get_attribute('href')
                        temp_str = "[안양산업진흥원][안양] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)

        except Exception as e:
            print("안양산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #부천산업진흥원:
        try: 
            for page_index in range(1,10):
                driver.get("https://www.bizbc.or.kr/board_skin/bbs_list.asp?id=inform0101&code=111010&gotopage="+ str(page_index))
                driver.implicitly_wait(1)
                print("부천산업진흥원 scraping")

                table = driver.find_element_by_class_name('list_table')
                tbody = table.find_element_by_tag_name('tbody')
                rows = tbody.find_elements_by_tag_name("tr")
                break_flag = FALSE

                for index, value in enumerate(rows):
                    
                        announce_date = value.find_elements_by_tag_name("td")[3].text.replace('-','.')
                        body=value.find_elements_by_tag_name("td")[1]
                        agency = value.find_elements_by_tag_name("td")[2].text.replace(' ','_')
                        if agency == "":
                            agency = "부천산업진흥원"

                        if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                            href = body.find_element_by_tag_name("a").get_attribute('href')
                            temp_str = "[" + agency +"][부천] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                            search_list.append(temp_str)
                        
                        if datetime.strptime(announce_date,"%Y.%m.%d")<datetime.strptime(search_date,"%Y.%m.%d"):
                            break_flag = TRUE
                            break

                if break_flag == TRUE:
                        break_flag = FALSE
                        break
                        
        except Exception as e:
            print("부천산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #I-PAC(특허지원센터):
        try: 
            driver.get("https://www.ipac.kr/core/?cid=18")
            driver.implicitly_wait(1)
            print("I-PAC(특허지원센터) scraping")

            table = driver.find_element_by_class_name("wrap_cont")
            tbody = table.find_element_by_class_name('tbody')
            rows = tbody.find_elements_by_class_name("tr")

            for index, value in enumerate(rows):
                
                    announce_date = value.find_elements_by_tag_name("span")[3].text
                    body=value.find_elements_by_tag_name("span")[2]

                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = body.find_element_by_tag_name("a").get_attribute('href')
                        temp_str = "[특허지원센터] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
                        
        except Exception as e:
            print("I-PAC(특허지원센터) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #KEA(한국전자정보통신산업진흥원):
        try: 
            driver.get("https://www.gokea.org/core/?cid=47")
            driver.implicitly_wait(1)
            print("KEA(한국전자정보통신산업진흥원) scraping")

            table = driver.find_element_by_class_name('tbl_list')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_element_by_class_name('col_date').text
                body=value.find_element_by_class_name('col_tit')
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[한국전자정보통신산업진흥원] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("KEA(한국전자정보통신산업진흥원) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #KFI(한국소방산업기술원):
        try: 
            driver.get("https://www.kfi.or.kr/portal/fgtIndsPromte01/promtePssrpAply/promtePssrpAply.do?menuNo=500018")
            driver.implicitly_wait(1)
            print("KFI(한국소방산업기술원) scraping")

            table = driver.find_element_by_class_name('gallery')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[2].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[1]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[한국소방산업기술원] " + announce_date + "  "+ body.find_elements_by_tag_name("span")[1].text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("KFI(한국소방산업기술원) scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #구미기업지원포털:
        try: 
            driver.get("https://www.gumi.go.kr/biz/portal/sprt/selectSprtList.do")
            driver.implicitly_wait(1)
            print("구미기업지원포털 scraping")

            table = driver.find_element_by_class_name('tableArea')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[4].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[2]
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[구미기업지원포털][구미] " + announce_date + "  "+ body.text.replace('\n','').replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("구미기업지원포털 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #중소환경기업 사업화지원시스템:
        try: 
            driver.get("https://www.konetic.or.kr/scaleup/biz/bizPblancList.do")
            driver.implicitly_wait(1)
            print("중소환경기업 사업화지원시스템 scraping")

            table = driver.find_element_by_class_name('table_normal')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[3].text
                body=value.find_elements_by_tag_name("td")[2]
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = "https://www.konetic.or.kr/scaleup/biz/bizPblancView.do?bizPblancNo=" + body.find_element_by_tag_name("a").get_attribute('onClick').split("'")[3]
                    temp_str = "[중소환경기업사업화지원시스템] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("중소환경기업 사업화지원시스템 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #기업/농어업협력재단:
        try: 
            driver.get("https://www.win-win.or.kr/kr/board/notice_enter/boardList.do")
            driver.implicitly_wait(1)
            print("농어업협력재단 scraping")

            table = driver.find_element_by_class_name('cont_bbs')
            rows = table.find_elements_by_tag_name('li')

            for index, value in enumerate(rows):
                if index != 0:
                    body=value.find_elements_by_tag_name('p')[2].find_element_by_tag_name('a')
                    announce_date_pre = value.find_elements_by_tag_name('p')[4].text.replace(' ','').split('~')[0]
                    #print("Dd")
                    if announce_date_pre == "":
                        announce_date = "2000.01.01"
                    else:
                        announce_date = "20" + announce_date_pre

                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = "https://www.win-win.or.kr" + value.get_attribute('onClick').split("'")[1]
                        temp_str = "[농어업협력재단] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
                    
        except Exception as e:
            print("농어업협력재단 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #한국정보통신진흥협회:
        try: 
            driver.get("https://cont.kait.or.kr/bidding/biddingList.do")
            driver.implicitly_wait(1)
            print("한국정보통신진흥협회 scraping")

            table = driver.find_element_by_class_name('announceListTable')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[2].text.split('(')[0].replace('-','.')
                body=value.find_elements_by_tag_name("td")[1].find_elements_by_tag_name("p")[1]
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[한국정보통신진흥협회] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("한국정보통신진흥협회 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #경상북도경제진흥원:
        try: 
            print("경상북도경제진흥원 scraping")

            for page_index in range(3,10):
                driver.get("https://www.gepa.kr/contents/madang/selectMadangList.do?menuId=223")

                driver.implicitly_wait(1)

                break_flag = FALSE                

                iframe = driver.find_element_by_id('jiwon_ifr')
                driver.switch_to.frame(iframe)

                driver.find_element_by_xpath('/html/body/ul/li['+ str(page_index) +']/a').click()

                table = driver.find_element_by_id('listForm')
                tbody = table.find_element_by_tag_name('tbody')
                rows = tbody.find_elements_by_tag_name("tr")

                for index, value in enumerate(rows):
                    announce_date = value.find_elements_by_tag_name("td")[4].text.replace('-','.')
                    body=value.find_elements_by_tag_name("td")[2]
                    
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = "https://www.gepa.kr/contents/madang/selectMadangListView.do?menuId=223&selectedId=" + body.find_element_by_tag_name("a").get_attribute('onClick').split("'")[1]
                        temp_str = "[경상북도경제진흥원][경북] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)

                    if datetime.strptime(announce_date,"%Y.%m.%d")<datetime.strptime(search_date,"%Y.%m.%d"):
                        break_flag = TRUE
                        break

                if break_flag == TRUE:
                        break_flag = FALSE
                        break
                    
        except Exception as e:
            print("경상북도경제진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #충남경제진흥원:
        try: 
            driver.get("https://www.cnsp.or.kr/project/list.do")
            driver.implicitly_wait(1)
            print("충남경제진흥원 scraping")


            for index in range(1,10):
                value = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[3]/div[2]/table/tbody/tr[' + str(index) + ']/td[2]/div')
                announce_date = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[3]/div[2]/table/tbody/tr[' + str(index) + ']/td[4]').text.split(' ')[0].replace('-','.')
                
                body=value.find_element_by_tag_name('a')

                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.get_attribute('href')
                    temp_str = "[충남경제진흥원][충남] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("충남경제진흥원 scraping exception!!")
            print("exception message : ",traceback.format_exc())

    if SCRAPING_FLAG: #성남산업진흥원:
        try: 
            driver.get("https://www.snip.or.kr/SNIP/contents/Business1.do?page=1&viewCount=50")
            driver.implicitly_wait(1)
            print("성남산업진흥원 scraping")

            table = driver.find_element_by_class_name('board-list')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name("tr")

            for index, value in enumerate(rows):
                announce_date = value.find_elements_by_tag_name("td")[5].text.replace('-','.')
                body=value.find_elements_by_tag_name("td")[2]
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = body.find_element_by_tag_name("a").get_attribute('href')
                    temp_str = "[성남산업진흥원][성남] " + announce_date + "  "+ body.text.replace(' ','_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("성남산업진흥원 scraping exception!!")
            print("exception message : ",traceback.format_exc())

    if SCRAPING_FLAG: #서울산업진흥원:
        try: 
            driver.get("https://www.sba.seoul.kr/Pages/BusinessApply/OngoingList.aspx")
            driver.implicitly_wait(1)
            print("성남산업진흥원 scraping")

            #table = driver.find_element_by_class_name('ContentPlaceHolder1_MainContents_GridView1')
            #tbody = table.find_element_by_tag_name('tbody')
            #rows = table.find_elements_by_class_name('grid_list tbody')

            for index in range(0,9):
                announce_date = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_MainContents_GridView1_lb_receipt_start_'+ str(index)+ '"]').text.replace('-','.')
                body=driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_MainContents_GridView1_new_name_'+ str(index)+ '"]')
                
                if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                    href = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_MainContents_GridView1"]/tbody/tr['+ str(index+2)+ ']/td[7]').get_attribute('onClick').split("'")[1]

                    if len(href) < 70: # 이 사이트의 href 확인해보면, full hyperlink가 써있는것도 있고, 일부만 써있는것도 있고... 그래서 이렇게 구현함
                        href = 'https://www.sba.seoul.kr/Pages/BusinessApply/' + href

                    temp_str = "[서울산업진흥원][서울] " + announce_date + "  "+ body.text.replace(' ', '_') + "  " + href + "\n"
                    search_list.append(temp_str)
                    
        except Exception as e:
            print("성남산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #한국데이터산업진흥원:
        try: 
            driver.get("https://www.kdata.or.kr/kr/board/notice_01/boardList.do")
            driver.implicitly_wait(1)
            print("한국데이터산업진흥원 scraping")

            table = driver.find_element_by_class_name('bbs_list')
            tbody = table.find_elements_by_tag_name('li')

            for index, value in enumerate(tbody):
                if index != 0:
                    announce_date = value.find_elements_by_tag_name('p')[4].text.split('\n')[1]
                    body=value.find_elements_by_tag_name('p')[1]
                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href = "https://www.kdata.or.kr/kr/board/notice_01/boardView.do?bbsIdx=" + value.get_attribute('onClick').split("'")[1]
                        temp_str = "[한국데이터산업진흥원] " + announce_date + "  "+ body.text.split('\n')[1].replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
                    
        except Exception as e:
            print("한국데이터산업진흥원 scraping exception!!")
            print("exception message : ",e)

    if SCRAPING_FLAG: #고양산업진흥원:
        try: 
            driver.get("https://www.gipa.or.kr/apply/01.php?cate=2")
            driver.implicitly_wait(1)
            print("고양산업진흥원 scraping")

            table = driver.find_element_by_class_name('table_line')
            tbody = table.find_element_by_tag_name('tbody')
            rows = tbody.find_elements_by_tag_name('tr')

            for index, value in enumerate(rows):
                    announce_date = value.find_elements_by_tag_name('td')[2].text.split('\n')[0].replace('-','.')
                    body=value.find_elements_by_tag_name('td')[1]

                    if datetime.strptime(announce_date,"%Y.%m.%d")>=datetime.strptime(search_date,"%Y.%m.%d"): 
                        href =  body.find_element_by_tag_name('a').get_attribute('href')
                        temp_str = "[고양산업진흥원][고양] " + announce_date + "  "+ body.text.split('\n')[0].replace(' ','_') + "  " + href + "\n"
                        search_list.append(temp_str)
                    
        except Exception as e:
            print("고양산업진흥원 scraping exception!!")
            print("exception message : ",e)

    driver.close()
    print("scraping success!!")

    return search_list


def templete(mail_contents, size, custom_data):
    #print(mail_contents)
    string_content = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
    <!--[if gte mso 9]>
    <xml>
    <o:OfficeDocumentSettings>
        <o:AllowPNG/>
        <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <!--[if !mso]><!--><meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
    <title></title>
    
        <style type="text/css">

        @media only screen and (min-width: 620px) {{
    .u-row {{
        width: 620px !important;
    }}
    .u-row .u-col {{
        vertical-align: top;
    }}

    .u-row .u-col-33p33 {{
        width: 199.98px !important;
    }}

    .u-row .u-col-100 {{
        width: 620px !important;
    }}

    }}

    @media (max-width: 620px) {{
    .u-row-container {{
        max-width: 100% !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
    }}
    .u-row .u-col {{
        min-width: 320px !important;
        max-width: 100% !important;
        display: block !important;
    }}
    .u-row {{
        width: calc(100% - 40px) !important;
    }}
    .u-col {{
        width: 100% !important;
    }}
    .u-col > div {{
        margin: 0 auto;
    }}
    .no-stack .u-col {{
        min-width: 0 !important;
        display: table-cell !important;
    }}

    .no-stack .u-col-33p33 {{
        width: 33.33% !important;
    }}

    }}
    body {{
    margin: 0;
    padding: 0;
    }}

    table,
    tr,
    td {{
    vertical-align: top;
    border-collapse: collapse;
    }}

    p {{
    margin: 0;
    }}

    .ie-container table,
    .mso-container table {{
    table-layout: fixed;
    }}

    * {{
    line-height: inherit;
    }}

    a[x-apple-data-detectors='true'] {{
    color: inherit !important;
    text-decoration: none !important;
    }}

    table, td {{ color: #000000; }} a {{ color: #0000ee; text-decoration: underline; }} @media (max-width: 620px) {{ #u_content_heading_5 .v-container-padding-padding {{ padding: 10px !important; }} #u_content_heading_5 .v-font-size {{ font-size: 14px !important; }} #u_content_heading_6 .v-container-padding-padding {{ padding: 10px !important; }} #u_content_heading_6 .v-font-size {{ font-size: 14px !important; }} #u_content_heading_7 .v-container-padding-padding {{ padding: 10px !important; }} #u_content_heading_7 .v-font-size {{ font-size: 14px !important; }} #u_content_heading_10 .v-container-padding-padding {{ padding: 10px !important; }} #u_content_heading_11 .v-container-padding-padding {{ padding: 40px 10px 39px !important; }} #u_content_heading_12 .v-container-padding-padding {{ padding: 40px 10px 39px !important; }}  }}
        </style>
    
    

    <!--[if !mso]><!--><link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet" type="text/css"><!--<![endif]-->

    </head>

    <body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #ffffff;color: #000000" >
    <!--[if IE]><div class="ie-container"><![endif]-->
    <!--[if mso]><div class="mso-container"><![endif]-->
    <table style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #ffffff;width:100%" cellpadding="0" cellspacing="0">
    <tbody>
    <tr style="vertical-align: top">
        <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
        <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #ffffff;"><![endif]-->
        

   <div class="u-row-container" style="padding: 0px;background-repeat: no-repeat;background-position: center top;background-color: transparent">
    <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 620px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
        <div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
        <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-repeat: no-repeat;background-position: center top;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:620px;"><tr style="background-color: transparent;"><![endif]-->
        
    <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 620px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-100" style="max-width: 320px;min-width: 620px;display: table-cell;vertical-align: top;">
    <div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

    <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 30px 30px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; color: #12335b; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 40px;">
        <strong>{mail_title}</strong>
    </h1>

        </td>
        </tr>

        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 30px 30px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; color: #000000; line-height: 140%; text-align: left; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 15px;">
        <strong>안녕하세요 {receiver_name}님<br>특허법인 도담입니다.<br><br>{mail_text} </strong>
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td><![endif]-->
        <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
        </div>
    </div>
    </div>


    <div class="u-row-container" style="padding: 0px;background-color: transparent">
    <div class="u-row no-stack" style="Margin: 0 auto;min-width: 320px;max-width: 620px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
        <div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
        <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:620px;"><tr style="background-color: transparent;"><![endif]-->
        
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #12335b;width: 150px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 150px;min-width: 150px;display: table-cell;vertical-align: top;">
    <div style="background-color: #12335b;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_5" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; color: #ffffff; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 16px;">
        <strong>기관명</strong>
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td><![endif]-->
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #12335b;width: 120px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 120px;min-width: 120px;display: table-cell;vertical-align: top;">
    <div style="background-color: #12335b;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_6" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; color: #ffffff; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 16px;">
        <strong>등록일</strong>
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td><![endif]-->
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #12335b;width: 450px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 450px;min-width: 450px;display: table-cell;vertical-align: top;">
    <div style="background-color: #12335b;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_7" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; color: #ffffff; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 16px;">
        <strong>공고 제목</strong>
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td><![endif]-->
        <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
        </div>
    </div>
    </div>
    '''.format(mail_title=mail_content_title, receiver_name=custom_data, mail_text=mail_content_text)


##################################################################################################111111
    for index in range(size):
        string_content = string_content + '''
    <div class="u-row-container" style="padding: 0px;background-color: transparent">
    <div class="u-row no-stack" style="Margin: 0 auto;min-width: 320px;max-width: 620px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
        <div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
        <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:620px;"><tr style="background-color: transparent;"><![endif]-->
        
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #ffffff;width: 150px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 150px;min-width: 150px;display: table-cell;vertical-align: top;">
    <div style="background-color: #ffffff;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_10" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px 10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 12px;">
        {content_Name}
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>


    <!--[if (mso)|(IE)]></td><![endif]-->
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #ffffff;width: 120px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 120px;min-width: 120px;display: table-cell;vertical-align: top;">
    <div style="background-color: #ffffff;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_11" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px 10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 12px;">
        <strong>{content_date}</strong>
    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>


    <!--[if (mso)|(IE)]></td><![endif]-->
    <!--[if (mso)|(IE)]><td align="center"  style="background-color: #ffffff;width: 450px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
    <div class="u-col u-col-33p33" style="max-width: 450px;min-width: 450px;display: table-cell;vertical-align: top;">
    <div style="background-color: #ffffff;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
    <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
    
    <table id="u_content_heading_12" style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
    <tbody>
        <tr>
        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px 10px;font-family:arial,helvetica,sans-serif;" align="left">
            
    <h1 class="v-font-size" style="margin: 0px; line-height: 140%; text-align: left; word-wrap: break-word; font-weight: normal; font-family: 'Montserrat',sans-serif; font-size: 12px;">
        <a href = "{content_hyperlink}" target = "_self">
            <strong>{content_title}</strong>
        </a>

    </h1>

        </td>
        </tr>
    </tbody>
    </table>

    <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td><![endif]-->
        <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
        </div>
    </div>
    </div>
    '''.format(content_Name=mail_contents[index][0], content_date=mail_contents[index][1], content_hyperlink=mail_contents[index][3], content_title=mail_contents[index][2] )

##################################################################################################

    string_content = string_content + '''



<div class="u-row-container" style="padding: 0px;background-color: transparent">
  <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 620px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
    <div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
      <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:620px;"><tr style="background-color: transparent;"><![endif]-->
      
<!--[if (mso)|(IE)]><td align="center" width="600" style="background-color: #ffffff;width: 620px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
<div class="u-col u-col-100" style="max-width: 320px;min-width: 620px;display: table-cell;vertical-align: top;">
  <div style="background-color: #ffffff;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
  <!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->
  


<table style="font-family:arial,helvetica,sans-serif; background-color: #ffffff;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
  <tbody>
    <tr style="background-color: #e6e3e3;"> 
     <div style="color: #000000; line-height: 140%; text-align: center; word-wrap: break-word;">

    <p style="font-size: 14px; line-height: 140%;"><span style="font-family: Montserrat, sans-serif; text-align: left; font-size: 14px; line-height: 19.6px;"><br>본 안내 메일의 수신 거부를 원하시면 회신하여 알려주시기 바랍니다.</span></p>
    <p style="font-size: 14px; line-height: 140%;"><span style="font-family: Montserrat, sans-serif; text-align: left; font-size: 14px; line-height: 19.6px;"><br>   T. 031-698-4120   /   F. 031-698-4130   </span></p>
    <p style="font-size: 14px; line-height: 140%;"><span style="font-family: Montserrat, sans-serif; text-align: left; font-size: 14px; line-height: 19.6px;">
       E. <a href="mailto:"sjkim@dodamip.com" >sjkim@dodamip.com</a>
       / H. <a href = "https://www.dodamip.com/" target = "_self"   >www.dodamip.com   </a></span></p>
    <p style="font-size: 14px; line-height: 140%;"><span style="font-family: Montserrat, sans-serif; text-align: left; font-size: 14px; line-height: 19.6px;"><br>
  </div>
    </tr>

    <tr style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 40px;font-family:arial,helvetica,sans-serif;" align="left" style="background-color: #ffffff;">     
       <div style= "text-align: center";>
            <img src="cid:capture" alt="dodam logo" width="50%">
        </div> 
    </tr>
  </tbody>
</table>

  <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
  </div>
</div>
<!--[if (mso)|(IE)]></td><![endif]-->
      <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
    </div>
  </div>
</div>


    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    </td>
  </tr>
  </tbody>
  </table>
  <!--[if mso]></div><![endif]-->
  <!--[if IE]></div><![endif]-->
</body>

</html>
    '''

    return string_content    


def send_email(smtp_info, msg):
    with smtplib.SMTP(smtp_info["smtp_server"], smtp_info["smtp_port"]) as server:
        #TLS 보안연결
        server.starttls()
        
        #로그인
        server.login(smtp_info["smtp_user_id"], smtp_info["smtp_user_pw"])

        response = server.sendmail(msg['from'], msg['to'], msg.as_string())

        if not response:
            print(msg['To']+' : 이메일을 성공적으로 보냈습니다.')
        else:
            print(response)

def read_mail_addr_file():
    #print("read addr list excel file")
    #print(Addr_list)
    return pd.read_excel('mail_addr_list.xlsx')

def Location_mail_list(search_list_fi):
    #리턴용 메일 리스트 선언 
    mail_list = []
    mail_list.append([])

    #전국 메일 리스트 선언 
    mail_list_all = ['전국']

    #광역자치단체 메일 리스트 선언  
    mail_list_seoul = ['서울'] 
    mail_list_busan = ['부산'] 
    mail_list_daegu = ['대구'] 
    mail_list_incheon = ['인천'] 

    mail_list_daejeon = ['대전'] 
    mail_list_gwangju = ['광주'] 
    mail_list_ulsan = ['울산'] 
    mail_list_sejong = ['세종'] 
    mail_list_gyeonggi = ['경기'] 

    mail_list_gangwon = ['강원'] 
    mail_list_chungbuk = ['충북'] 
    mail_list_chungnam = ['충남'] 
    mail_list_jeonbuk = ['전북'] 
    mail_list_jeonnam = ['전남'] 

    mail_list_gyeongbuk = ['경북'] 
    mail_list_gyeongnam = ['경남'] 
    mail_list_jeju = ['제주']

    #기초자치단체 메일리스트 선언
    mail_list_pohang = ['포항']
    mail_list_bucheon = ['부천']

    mail_list_seongnam = ['성남']
    mail_list_gunpo = ['군포']
    mail_list_anyang = ['안양']
    mail_list_gumi = ['구미']
    mail_list_goyang = ['고양']

    multi_location_temp = []

    for index in range(len(search_list_fi)): 
        #print(search_list_fi[index][1].split('ㆍ'))
        multi_location_temp.extend(search_list_fi[index][1].split('ㆍ'))

        for loca_index in range(len(multi_location_temp)):
            if '전국' in multi_location_temp[loca_index]:
                mail_list_all.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '진흥회' in multi_location_temp[loca_index]:
                mail_list_all.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '서울' in multi_location_temp[loca_index]:
                mail_list_seoul.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '부산' in multi_location_temp[loca_index]:
                mail_list_busan.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '대구' in multi_location_temp[loca_index]:
                mail_list_daegu.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '인천' in multi_location_temp[loca_index]:
                mail_list_incheon.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '대전' in multi_location_temp[loca_index]:
                mail_list_daejeon.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '광주' in multi_location_temp[loca_index]:
                mail_list_gwangju.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '울산' in multi_location_temp[loca_index]:
                mail_list_ulsan.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '세종' in multi_location_temp[loca_index]:
                mail_list_sejong.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '경기' in multi_location_temp[loca_index]:
                mail_list_gyeonggi.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '강원' in multi_location_temp[loca_index]:
                mail_list_gangwon.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '충북' in multi_location_temp[loca_index]:
                mail_list_chungbuk.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '충남' in multi_location_temp[loca_index]:
                mail_list_chungnam.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '전북' in multi_location_temp[loca_index]:
                mail_list_jeonbuk.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '전남' in multi_location_temp[loca_index]:
                mail_list_jeonnam.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '경북' in multi_location_temp[loca_index]:
                mail_list_gyeongbuk.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '경남' in multi_location_temp[loca_index]:
                mail_list_gyeongnam.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '제주' in multi_location_temp[loca_index]:
                mail_list_jeju.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '포항' in multi_location_temp[loca_index]:
                mail_list_pohang.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '부천' in multi_location_temp[loca_index]:
                mail_list_bucheon.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '성남' in multi_location_temp[loca_index]:
                mail_list_seongnam.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '군포' in multi_location_temp[loca_index]:
                mail_list_gunpo.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '안양' in multi_location_temp[loca_index]:
                mail_list_anyang.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '구미' in multi_location_temp[loca_index]:
                mail_list_gumi.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])

            elif '고양' in multi_location_temp[loca_index]:
                mail_list_goyang.append(search_list_fi[index][0] + " " + search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])
            else:
                print("지역명 에러 발생 / 공고내용 : "+ search_list_fi[index][0] + " " + search_list_fi[index][1] + " "+ search_list_fi[index][2] + " " + search_list_fi[index][3] + " " +search_list_fi[index][4])
        
        multi_location_temp = []

    mail_list[0].append(mail_list_all)
    mail_list.append([])
    mail_list[1].append(mail_list_seoul)
    mail_list.append([])
    mail_list[2].append(mail_list_busan)
    mail_list.append([])
    mail_list[3].append(mail_list_daegu)
    mail_list.append([])
    mail_list[4].append(mail_list_incheon)

    mail_list.append([])
    mail_list[5].append(mail_list_daejeon)
    mail_list.append([])
    mail_list[6].append(mail_list_gwangju)
    mail_list.append([])
    mail_list[7].append(mail_list_ulsan)
    mail_list.append([])
    mail_list[8].append(mail_list_sejong)
    mail_list.append([])
    mail_list[9].append(mail_list_gyeonggi)

    mail_list.append([])
    mail_list[10].append(mail_list_gangwon)
    mail_list.append([])
    mail_list[11].append(mail_list_chungbuk)
    mail_list.append([])
    mail_list[12].append(mail_list_chungnam)
    mail_list.append([])
    mail_list[13].append(mail_list_jeonbuk)
    mail_list.append([])
    mail_list[14].append(mail_list_jeonnam)

    mail_list.append([])
    mail_list[15].append(mail_list_gyeongbuk)
    mail_list.append([])
    mail_list[16].append(mail_list_gyeongnam)
    mail_list.append([])
    mail_list[17].append(mail_list_jeju)
    mail_list.append([])
    mail_list[18].append(mail_list_pohang)
    mail_list.append([])
    mail_list[19].append(mail_list_bucheon)

    mail_list.append([])
    mail_list[20].append(mail_list_seongnam)
    mail_list.append([])
    mail_list[21].append(mail_list_gunpo)
    mail_list.append([])
    mail_list[22].append(mail_list_anyang)
    mail_list.append([])
    mail_list[23].append(mail_list_gumi)
    mail_list.append([])
    mail_list[24].append(mail_list_goyang)

    #print(mail_list)
    
    return mail_list

def user_addr_mail_contents(receiver_addr, mail_list_fi):

    user_mail_list = []
    user_mail_list.extend(mail_list_fi[0][0][1:len(mail_list_fi[0][0])])  #전국 공고 공통 삽입
    if receiver_addr != "-":
        for location_index in range(1, len(mail_list_fi)):
            if mail_list_fi[location_index][0][0] in receiver_addr:
                user_mail_list.extend(mail_list_fi[location_index][0][1:len(mail_list_fi[location_index][0])])

    #print(user_mail_list)
    return user_mail_list

def auto_mail(search_list_fi):

    mail_contents = ""

    if search_list_fi==False:
        mail_contents = "검색 결과 없음"

    # 메일 정보 작성
    receiver = read_mail_addr_file()
    receiver_addr = receiver['Address']
    receiver_name = receiver['Name']
    receiver_email = receiver['E-mail']

    mail_list_fi = []

    # 지역별 메일 list 생성(다차원 배열)
    mail_list_fi = Location_mail_list(search_list_fi)
    
    

    for index in range(len(receiver_email)): 
        
        #유저 메일 주소에 따라, 메일 리스트 할당
        user_mail_list_fi = user_addr_mail_contents(receiver_addr[index], mail_list_fi)

        #메일 전송용 리스트 초기화
        mail_contents = [None]*len(user_mail_list_fi)  

        for mail_index in range(len(user_mail_list_fi)):
            mail_contents[mail_index] = user_mail_list_fi[mail_index].split(" ")

        #print(receiver_name[index], receiver_email[index], mail_contents)
        # 메일 객체 생성
        global mail_title
        title = mail_title # 메일 제목
        content = templete(mail_contents, len(user_mail_list_fi), receiver_name[index]) # 메일 내용 작성
        sender = "sjkim@dodamip.com"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title     # 메일 제목
        msg['From'] = sender       # 송신자
        msg['To'] = receiver_email[index]       # 수신자
        html = MIMEText(content,'html')

        msg.attach(html)

        with open('images/dodam_logo.jpg', 'rb') as fp:
            img = MIMEImage(fp.read(), Name = 'dodam_logo')
            img.add_header('Content-ID','<capture>')
            msg.attach(img)

        send_email(smtp_info, msg)

def Location_extract(list):
    location_val = ""

    def Location_Normalization(location_val):
        temp_loca = location_val[1:len(location_val)-1] 

        if temp_loca == '경기대진':
            return_location = '경기'
        elif temp_loca == '강원남부':
            return_location = '강원'
        elif temp_loca == '강원서부':
            return_location = '강원'
        elif temp_loca == '경기남부':
            return_location = '경기'
        elif temp_loca == '경기북부':
            return_location = '경기'
        elif temp_loca == '경남서부':
            return_location = '경남'
        elif temp_loca == '경북북부':
            return_location = '경북'
        elif temp_loca == '경북서부':
            return_location = '경북'
        #if temp_loca == '부천':
        #    return_location = '부천ㆍ경기'
        elif temp_loca == '충남서부':
            return_location = '충남'
        elif temp_loca == '충북북부':
            return_location = '충북'
        #elif temp_loca == '성남':
        #    return_location = '성남ㆍ경기'
        #elif temp_loca == '군포':
        #    return_location = '군포ㆍ경기'
        #elif temp_loca == '안양':
        #    return_location = '안양ㆍ경기'
        #elif temp_loca == '구미':
        #    return_location = '구미ㆍ경북'
        #elif temp_loca == '고양':
        #    return_location = '고양ㆍ경기'
        else:
            return_location = temp_loca

        return '['+return_location+']'

    if list[0].find("][") > 0:  #지역값이 존재하는 경우
        
        #지역값 분할
        location_val = list[0][list[0].find("][") + 1 :len(list[0])]

        #0번 배열에서 지역값 삭제
        list[0] = list[0][0:list[0].find("][") + 1]

        #지역값 정규화 ( 구미 -> 구미ㆍ경북 / 강원서부 -> 강원)
        return_location = Location_Normalization(location_val)

        #1번 배열에 지역값 삽입
        list.insert(1,return_location)

    else:  #존재하지 않는 경우, 전국으로 통칭
        list.insert(1,'[전국]')

    return list

def scraping_input():
    #-------------------------------------------------------------------------------
    # '검색' 버튼 클릭 시 공고 크롤링 수행
    #-------------------------------------------------------------------------------
    def search_btncmd():
        global gb_search_list_fi
        #tree 초기화
        for i in treeview.get_children():
            treeview.delete(i)
        
        #검색 기준일 설정
        if date_Var.get() == 10:
            search_date = input_date.get()
        else:
            search_date =  (datetime.today() - timedelta(date_Var.get())).strftime("%Y.%m.%d")

        try:
            search_list_fi = search_main(search_date)
            gb_search_list_fi = search_list_fi
        except Exception as e:
            messagebox.showinfo("[오류]", "검색 동작 비정상 종료")    
            search_list_fi = 0
        
        

        if search_list_fi==0:
            messagebox.showinfo("[알림]", "검색 결과 없음")

        #tree에 값 작성
        else:
            for index in range(len(search_list_fi)):
                treeview.insert('','end',text=index+1,value = search_list_fi[index], iid=index)

    #-------------------------------------------------------------------------------
    # 버튼 클릭 시 해당 공고의 하이퍼링크 창 오픈
    #-------------------------------------------------------------------------------
    def hyperlink_btncmd():
        selecteditem = treeview.focus()
        if selecteditem == "":
            messagebox.showinfo("[오류]", "선택한 리스트가 없음")
        else:
            hyper_str= treeview.item(selecteditem).get('values')[3]
            webbrowser.open(url=hyper_str)

    #-------------------------------------------------------------------------------
    # 메일 보내기용 리스트의 공고 삭제
    #-------------------------------------------------------------------------------
    def delete_btncmd():

        selecteditem = treeview_mail.selection()
        tree_data_temp = []
        break_num = 0


        for sel_tree_index in range(len(selecteditem)):
            if selecteditem[sel_tree_index] == "":
                messagebox.showinfo("[오류]", "삭제할 리스트가 없음")
            else:
                for index in range(break_num,len(treeview_mail.get_children())):
                    if index == int(selecteditem[sel_tree_index]):
                        #treeview_mail.delete(selecteditem)
                        break_num = break_num + 1
                        break
                    else:
                        tree_data_temp.append(treeview_mail.item(index).get('values'))
                        break_num = break_num + 1

        if break_num < len(treeview_mail.get_children()):
            for index in range(break_num,len(treeview_mail.get_children())):
                tree_data_temp.append(treeview_mail.item(index).get('values'))



        #treeview_mail 리셋 및 재작성
        for index in treeview_mail.get_children():
            treeview_mail.delete(index)

        for index in range(len(tree_data_temp)):
            treeview_mail.insert('','end',text=index+1,value = tree_data_temp[index], iid=index)

    #-------------------------------------------------------------------------------
    # 메일 보내기용 리스트 정보 메일로 보내기
    #-------------------------------------------------------------------------------
    def mail_send_btncmd():
        try:
            if len(treeview_mail.get_children()) == 0:
                messagebox.showinfo("[오류]", "보낼 리스트가 없음")
            else:
                            
                mail_list_fi = []
                for index in range(len(treeview_mail.get_children())):
                    mail_list_fi.append(treeview_mail.item(index).get('values'))                

                #검색결과 이메일 전송
                if len(mail_list_fi)==0:
                    auto_mail(False)
                else:
                    auto_mail(mail_list_fi)
                    messagebox.showinfo("[알림]", "메일 발송 완료")
        
        except FileNotFoundError:
            print("mail_addr_list.xlsx 파일 없음")
            messagebox.showinfo("[오류]", "메일 리스트 엑셀 파일이 확인되지 않음. 파일위치/파일이름 확인 필요")

    #-------------------------------------------------------------------------------
    # 입력된 키워드를 기준으로 검색 결과 필터링
    #-------------------------------------------------------------------------------   
    def keyword_filter_btncmd():
        fil_keyword_init = input_keyword.get()
        fil_keyword = fil_keyword_init.split(" ")
        treeview_data_temp=[]

        if len(treeview.get_children()) == 0:
            messagebox.showinfo("[오류]", "검색 결과 리스트가 없음")
        else:
            #키워드에 해당하는 공고 treeview_data_temp에 저장
            for index in range(len(treeview.get_children())):
                for j_index in range(len(fil_keyword)):
                    if fil_keyword[j_index] in treeview.item(index).get('values')[2]:
                        treeview_data_temp.append(treeview.item(index).get('values'))

            #treeview_data_temp 중복 제거
            duplicated_data_temp = []
            for index in range(len(treeview_data_temp)):
                if treeview_data_temp[index] not in duplicated_data_temp:
                    duplicated_data_temp.append(treeview_data_temp[index])
                        

            #treeview 리셋
            for index in treeview.get_children():
                treeview.delete(index)

            #duplicated_data_temp의 데이터 treeview에 작성
            for index in range(len(duplicated_data_temp)):
                treeview.insert('','end',text=index+1,value = duplicated_data_temp[index], iid=index)

    #-------------------------------------------------------------------------------
    # 초기 검색 결과(리스트)로 리셋
    #-------------------------------------------------------------------------------  
    def filter_reset_btncmd():

        global gb_search_list_fi

        if len(treeview.get_children()) == 0:
            messagebox.showinfo("[오류]", "검색 결과 리스트가 없음")
        else:
            #tree 초기화
            for i in treeview.get_children():
                treeview.delete(i)

        if len(gb_search_list_fi)==0:
            messagebox.showinfo("[알림]", "검색 결과 없음")
        #tree에 값 작성
        else:
            for index in range(len(gb_search_list_fi)):
                treeview.insert('','end',text=index+1,value = gb_search_list_fi[index], iid=index)

    #-------------------------------------------------------------------------------
    # sub window1(수동 공고 추가) set
    #-------------------------------------------------------------------------------
    def list_manual_add_btncmd():

        def list_manual_add_func(newWindow1):
            def Announcement_Add_set():
                manual_add_list = Announcement_Name_input.get() + " " + Announcement_Loca_input.get() + " " +Announcement_Dat_input.get() + " " + Announcement_title_input.get() + " " + Announcement_link_input.get()
                treeview_mail.insert('','end',text=" ",values = manual_add_list, iid=len(treeview_mail.get_children()))
                print(manual_add_list)
                newWindow1.destroy()
            #-------------------------------------------------------------------------------
            # UI set
            #-------------------------------------------------------------------------------
            Announcement_Name_Label = Label(newWindow1, text='기관명( [기관명] )')
            Announcement_Name_Label.grid(row=0, column=0, padx=5, pady=5)

            Announcement_Name_input = Entry(newWindow1, width=50)
            Announcement_Name_input.grid(row=0, column=1, padx=5, pady=5,sticky=W)
            
            Announcement_Loca_Label = Label(newWindow1, text='지역( [지역] )')
            Announcement_Loca_Label.grid(row=1, column=0, padx=5, pady=5)

            Announcement_Loca_input = Entry(newWindow1, width=50)
            Announcement_Loca_input.grid(row=1, column=1, padx=5, pady=5,sticky=W)

            Announcement_Date_Label = Label(newWindow1, text='공고 개시일(yyyy.mm.dd)')
            Announcement_Date_Label.grid(row=2, column=0, padx=5, pady=5)

            Announcement_Dat_input = Entry(newWindow1, width=50)
            Announcement_Dat_input.grid(row=2, column=1, padx=5, pady=5,sticky=W)

            Announcement_title_Label = Label(newWindow1, text='공고 제목')
            Announcement_title_Label.grid(row=3, column=0, pady=5)

            Announcement_title_input = Entry(newWindow1, width=50)
            Announcement_title_input.grid(row=3, column=1, padx=5, pady=5,sticky=W)

            Announcement_link_Label = Label(newWindow1, text='공고 링크')
            Announcement_link_Label.grid(row=4, column=0, pady=5)

            Announcement_link_input = Entry(newWindow1, width=50)
            Announcement_link_input.grid(row=4, column=1, padx=5, pady=5,sticky=W)

            ok_btn = Button(newWindow1, text="확인", command=Announcement_Add_set)
            ok_btn.grid(row=5, column=1, columnspan=2, padx=5, pady=5,sticky=W)

        newWindow1 = tk.Toplevel()
        newWindow1.title("list manual add UI")
        newWindow1.resizable(True, True)

        list_manual_add_func(newWindow1)
        

        newWindow1.columnconfigure(0, weight=1)
        newWindow1.rowconfigure(1, weight=1)

    #-------------------------------------------------------------------------------
    # sub window2(메일 내용 변경) set
    #-------------------------------------------------------------------------------
    def mail_content_input_btncmd():

        def mail_content_input_func(newWindow2):

            def mail_content_set():
                global mail_title
                global mail_content_text
                global mail_content_title

                mail_title = mail_title_input.get()
                mail_content_title = mail_text_title_input.get()
                mail_content_text = mail_text_input.get("1.0", tk.END).replace('\n','<br>')

                newWindow2.destroy()
            #-------------------------------------------------------------------------------
            # UI set
            #-------------------------------------------------------------------------------
            mail_title_Label = Label(newWindow2, text='메일 제목')
            mail_title_Label.grid(row=0, column=0, padx=5, pady=5)

            mail_title_input = Entry(newWindow2, width=50)
            mail_title_input.grid(row=0, column=1, padx=5, pady=5,sticky=W)
            mail_title_input.insert(0, mail_title)
            
            mail_text_title_Label = Label(newWindow2, text='본문 제목')
            mail_text_title_Label.grid(row=1, column=0, padx=5, pady=5)

            mail_text_title_input = Entry(newWindow2, width=50)
            mail_text_title_input.grid(row=1, column=1, padx=5, pady=5,sticky=W)
            mail_text_title_input.insert(0, mail_content_title)

            mail_text_Label = Label(newWindow2, text='본문 내용')
            mail_text_Label.grid(row=2, column=0, pady=5)

            mail_text_input = Text(newWindow2, width=50, height=5)
            mail_text_input.grid(row=2, column=1, padx=5, pady=5,sticky=W)
            mail_text_input.insert(tk.END, mail_content_text.replace('<br>','\n'))

            ok_btn = Button(newWindow2, text="확인", command=mail_content_set)
            ok_btn.grid(row=3, column=1, columnspan=2, padx=5, pady=5,sticky=W)

        newWindow2 = tk.Toplevel()
        newWindow2.title("mail_content UI")
        newWindow2.resizable(True, True)

        mail_content_input_func(newWindow2)

        newWindow2.columnconfigure(0, weight=1)
        newWindow2.rowconfigure(1, weight=1)

    #-------------------------------------------------------------------------------
    # 검색 결과 다중 선택 후 버튼 클릭 시 해당 리스트값을 메일 리스트로 복사
    #-------------------------------------------------------------------------------
    def list_add_btncmd():
        selecteditem = treeview.selection()  #선택된 공고 lid를 tuple형 변수로 넘겨받음

        for index in range(len(selecteditem)):
            
            # 중복 리스트 선택 시, 메일 리스트로 복사하지 않음
            if len(treeview_mail.get_children()) == 0:
                treeview_mail.insert('','end',text=" ",values=Location_extract(treeview.item(selecteditem[index]).get('values')), iid=0)
            else:
                duplicated_flag = FALSE
                temp_num = len(treeview_mail.get_children())
                for j_index in range(temp_num):
                    
                    if(Location_extract(treeview.item(selecteditem[index]).get('values')) == treeview_mail.item(j_index).get('values')):   
                        duplicated_flag=TRUE
                        print("중복")
                
                if(duplicated_flag==FALSE):
                    treeview_mail.insert('','end',text=" ",values=Location_extract(treeview.item(selecteditem[index]).get('values')), iid=temp_num)

    #-------------------------------------------------------------------------------
    # 검색 결과 더블클릭 시 해당 리스트값을 메일 리스트로 복사
    #-------------------------------------------------------------------------------
    def double_click(event):
        selecteditem = treeview.focus()
        
        # 중복 리스트 더블클릭 시, 메일 리스트로 복사하지 않음
        if len(treeview_mail.get_children()) == 0:
            #Location_extract_result = Location_extract(treeview.item(selecteditem).get('values'))
            treeview_mail.insert('','end',text=" ",values=Location_extract(treeview.item(selecteditem).get('values')), iid=0)
        else:
            duplicated_flag = FALSE
            temp_num = len(treeview_mail.get_children())
            for index in range(temp_num):
                
                if(Location_extract(treeview.item(selecteditem).get('values')) == treeview_mail.item(index).get('values')):   
                    duplicated_flag=TRUE
                    print("중복")
            
            if(duplicated_flag==FALSE):
                treeview_mail.insert('','end',text=" ",values=Location_extract(treeview.item(selecteditem).get('values')), iid=temp_num)

    #-------------------------------------------------------------------------------
    # 메일 리스트의 지역값 수동 변경
    #-------------------------------------------------------------------------------
    def loca_setting_btncmd():
        
        def mail_loca_setting(newWindow3):

            def loca_set():
                selecteditem = treeview_mail.focus()

                old_maillist_item =  treeview_mail.item(selecteditem).get('values')
                new_maillist_item = old_maillist_item[0] + " " + loca_Var.get() + " " + old_maillist_item[2] + " " + old_maillist_item[3] + " " + old_maillist_item[4]
                treeview_mail.item(selecteditem, values = new_maillist_item)
                newWindow3.destroy()
            #-------------------------------------------------------------------------------
            # UI set
            #-------------------------------------------------------------------------------
            loca_Var = tk.StringVar()
            loca_Rad1 = tk.Radiobutton(newWindow3, text="전국", variable=loca_Var, value = '[전국]')
            loca_Rad1.grid(row=0, column=0, padx=2)
            loca_Rad1.select()

            loca_Rad2 = tk.Radiobutton(newWindow3, text="강원", variable=loca_Var, value = '[강원]')
            loca_Rad2.grid(row=0, column=1, padx=2)
            loca_Rad2.deselect()

            loca_Rad3 = tk.Radiobutton(newWindow3, text="경기", variable=loca_Var, value = '[경기]')
            loca_Rad3.grid(row=0, column=2, padx=2)
            loca_Rad3.deselect()
            
            loca_Rad4 = tk.Radiobutton(newWindow3, text="경남", variable=loca_Var, value = '[경남]')
            loca_Rad4.grid(row=0, column=3, padx=2)
            loca_Rad4.deselect()

            loca_Rad5 = tk.Radiobutton(newWindow3, text="경북", variable=loca_Var, value = '[경북]')
            loca_Rad5.grid(row=0, column=4, padx=2)
            loca_Rad5.deselect()
            
            loca_Rad6 = tk.Radiobutton(newWindow3, text="광주", variable=loca_Var, value = '[광주]')
            loca_Rad6.grid(row=0, column=5, padx=2)
            loca_Rad6.deselect()

            loca_Rad7 = tk.Radiobutton(newWindow3, text="대구", variable=loca_Var, value = '[대구]')
            loca_Rad7.grid(row=1, column=0, padx=2)
            loca_Rad7.deselect()

            loca_Rad8 = tk.Radiobutton(newWindow3, text="대전", variable=loca_Var, value = '[대전]')
            loca_Rad8.grid(row=1, column=1, padx=2)
            loca_Rad8.deselect()
            
            loca_Rad9 = tk.Radiobutton(newWindow3, text="부산", variable=loca_Var, value = '[부산]')
            loca_Rad9.grid(row=1, column=2, padx=2)
            loca_Rad9.deselect()
            
            loca_Rad10 = tk.Radiobutton(newWindow3, text="서울", variable=loca_Var, value = '[서울]')
            loca_Rad10.grid(row=1, column=3, padx=2)
            loca_Rad10.deselect()

            loca_Rad11 = tk.Radiobutton(newWindow3, text="세종", variable=loca_Var, value = '[세종]')
            loca_Rad11.grid(row=1, column=4, padx=2)
            loca_Rad11.deselect()
            
            loca_Rad12 = tk.Radiobutton(newWindow3, text="울산", variable=loca_Var, value = '[울산]')
            loca_Rad12.grid(row=1, column=5, padx=2)
            loca_Rad12.deselect()

            loca_Rad13 = tk.Radiobutton(newWindow3, text="인천", variable=loca_Var, value = '[인천]')
            loca_Rad13.grid(row=2, column=0, padx=2)
            loca_Rad13.deselect()

            loca_Rad14 = tk.Radiobutton(newWindow3, text="전남", variable=loca_Var, value = '[전남]')
            loca_Rad14.grid(row=2, column=1, padx=2)
            loca_Rad14.deselect()
            
            loca_Rad15 = tk.Radiobutton(newWindow3, text="전북", variable=loca_Var, value = '[전북]')
            loca_Rad15.grid(row=2, column=2, padx=2)
            loca_Rad15.deselect()
            
            loca_Rad16 = tk.Radiobutton(newWindow3, text="제주", variable=loca_Var, value = '[제주]')
            loca_Rad16.grid(row=2, column=3, padx=2)
            loca_Rad16.deselect()

            loca_Rad17 = tk.Radiobutton(newWindow3, text="충남", variable=loca_Var, value = '[충남]')
            loca_Rad17.grid(row=2, column=4, padx=2)
            loca_Rad17.deselect()
            
            loca_Rad18 = tk.Radiobutton(newWindow3, text="충북", variable=loca_Var, value = '[충북]')
            loca_Rad18.grid(row=2, column=5, padx=2)
            loca_Rad18.deselect()

            ok_btn = Button(newWindow3, text="확인", command=loca_set)
            ok_btn.grid(row=3, column=1, columnspan=2, padx=5, pady=5,sticky=W)

        newWindow3 = tk.Toplevel()
        newWindow3.title("mail_location_setting UI")
        newWindow3.resizable(True, True)

        mail_loca_setting(newWindow3)

        newWindow3.columnconfigure(0, weight=1)
        newWindow3.rowconfigure(1, weight=1)
 

    #===============================================================================
    # Config Group Main
    #===============================================================================            
    config_group_main = LabelFrame(root, text="Search Config", padx=0, pady=0)
    config_group_main.grid(row = 0, column=0, padx=10, pady=5, sticky=W+E)

    #-------------------------------------------------------------------------------
    #Config Group Sub0
    #-------------------------------------------------------------------------------    
    config_group_sub2 = Frame(config_group_main, relief = "ridge", bd=2)
    config_group_sub2.grid(row = 0, column=0, padx=10, pady=5, sticky=E+W)

    label_date = Label(config_group_sub2, text='검색 기준 날짜')
    label_date.grid(row=0, column=0, padx=5)

    date_Var = tk.IntVar()
    date_Rad1 = tk.Radiobutton(config_group_sub2, text="1일 전", variable=date_Var, value = 1)#, command=write_input_data)
    date_Rad1.grid(row=1, column=0, padx=2)
    date_Rad1.deselect()

    date_Rad2 = tk.Radiobutton(config_group_sub2, text="3일 전", variable=date_Var, value = 3)#, command=write_input_data)
    date_Rad2.grid(row=1, column=1, padx=2)
    date_Rad2.deselect()
    
    date_Rad3 = tk.Radiobutton(config_group_sub2, text="7일 전", variable=date_Var, value = 7)#, checked="checked", command=write_input_data)
    date_Rad3.grid(row=1, column=2, padx=2)
    date_Rad3.select()
    
    date_Rad4 = tk.Radiobutton(config_group_sub2, text="직접 작성", variable=date_Var, value = 10)#, command=write_input_data)
    date_Rad4.grid(row=1, column=3, padx=2)
    date_Rad4.deselect()
    

    input_date = Entry(config_group_sub2, width=20)
    input_date.grid(row=1, column=4, padx=5)
    input_date.insert(0, (datetime.today() - timedelta(10)).strftime("%Y.%m.%d"))    

    search_btn = Button(config_group_sub2, text="검색", command=search_btncmd)
    search_btn.grid(row=1, column=5, padx=2)

    config_group_main.rowconfigure(0, weight=0)
    config_group_main.columnconfigure(0, weight=1)

    #===============================================================================
    # Search Result Group Main
    #===============================================================================
    result_group_main = LabelFrame(root, text="Search Result", padx=0, pady=0)
    result_group_main.grid(row = 1, column=0, columnspan=3, padx=10, pady=5, sticky=E+W+S+N)

    hyperlink_btn = Button(result_group_main, text="상세공고 확인", command=hyperlink_btncmd)
    hyperlink_btn.grid(row=0, column=0, padx=5, sticky=W)

    list_add_btn = Button(result_group_main, text="선택공고 추가", command=list_add_btncmd)
    list_add_btn.grid(row=0, column=1, padx=5, sticky=W)

    label_tree_remark = Label(result_group_main, text='(공고 더블클릭시 메일 리스트 확정)', anchor="w")
    label_tree_remark.grid(row=0, column=2, ipadx=100)

    label_keyword = Label(result_group_main, text='필터링 키워드')
    label_keyword.grid(row=1, column=0, padx=5, sticky=W)

    input_keyword = Entry(result_group_main, width=100)
    input_keyword.grid(row=1, column=1, padx=5, columnspan=2,sticky=W)
    input_keyword.insert(0, keyword0+keyword1+keyword2)

    filter_btn = Button(result_group_main, text="공고 필터링", command=keyword_filter_btncmd)
    filter_btn.grid(row=1, column=3, padx=5, sticky=W)

    ft_reset_btn = Button(result_group_main, text="필터 리셋", command=filter_reset_btncmd)
    ft_reset_btn.grid(row=1, column=4, padx=5, sticky=W)

    treeview = ttk.Treeview(result_group_main,columns=["one", "two", "three"], displaycolumns=["one","two", "three"])
    treeview.grid(row=2, column=0, columnspan=5, padx=10, pady=5, sticky=E+W+S+N)
    
    hsb = tk.Scrollbar(result_group_main, orient="horizon", command=treeview.xview)
    hsb.grid(row=3, column=0, padx=10, sticky=E+W)
    treeview.configure(xscrollcommand=hsb.set)
    
    vsb = tk.Scrollbar(result_group_main, orient="vertical", command=treeview.yview)
    vsb.grid(row=2, column=5, padx=0, sticky=N+S)
    treeview.configure(yscrollcommand=vsb.set)
    
    treeview.column("#0", minwidth=0, width=40, stretch=NO)
    treeview.heading("#0", text="No.")
    
    treeview.column("#1", minwidth=0, width=100, stretch=NO, anchor="center")
    treeview.heading("one", text="Name", anchor="center")

    treeview.column("#2", minwidth=0, width=100, stretch=NO, anchor="center")
    treeview.heading("two", text="Date", anchor="center")

    treeview.column("#3", minwidth=0, width=600, stretch=NO, anchor="center")
    treeview.heading("three", text="Title", anchor="center")

    treeview.bind("<Double-1>", double_click)               

    result_group_main.rowconfigure(1, weight=1)
    result_group_main.columnconfigure(0, weight=1)

    #===============================================================================
    # mail list Result Group Main
    #===============================================================================
    mail_list_group_main = LabelFrame(root, text="mail SET", padx=0, pady=0)
    mail_list_group_main.grid(row = 2, column=0, columnspan=3, padx=10, pady=5, sticky=E+W+S+N)

    delete_btn = Button(mail_list_group_main, text="선택공고 삭제", command=delete_btncmd)
    delete_btn.grid(row=0, column=0, padx=5, sticky=W )

    delete_btn = Button(mail_list_group_main, text="선택공고 지역 변경", command=loca_setting_btncmd)
    delete_btn.grid(row=0, column=1, padx=5, sticky=W )

    list_manual_add_btn = Button(mail_list_group_main, text="공고 수동 추가", command=list_manual_add_btncmd)
    list_manual_add_btn.grid(row=0, column=2, padx=5, sticky=W)

    mail_text_btn = Button(mail_list_group_main, text="메일 내용 변경", command=mail_content_input_btncmd)
    mail_text_btn.grid(row=0, column=3, padx=5, sticky=W)

    mail_send_btn = Button(mail_list_group_main, text="메일 보내기", command=mail_send_btncmd)
    mail_send_btn.grid(row=0, column=4, padx=5, sticky=W)

    treeview_mail = ttk.Treeview(mail_list_group_main,columns=["one", "two", "three","four"], displaycolumns=["one","two", "three","four"])
    treeview_mail.grid(row=1, column=0, padx=10, pady=5, columnspan=5, sticky=E+W+S+N)
    
    hsb = tk.Scrollbar(mail_list_group_main, orient="horizon", command=treeview_mail.xview)
    hsb.grid(row=2, column=0, padx=10, sticky=E+W)
    treeview_mail.configure(xscrollcommand=hsb.set)
    
    vsb = tk.Scrollbar(mail_list_group_main, orient="vertical", command=treeview_mail.yview)
    vsb.grid(row=1, column=5, padx=0, sticky=N+S)
    treeview_mail.configure(yscrollcommand=vsb.set)
    
    treeview_mail.column("#0", minwidth=0, width=40, stretch=NO)
    treeview_mail.heading("#0", text="No.")
    
    treeview_mail.column("#1", minwidth=0, width=100, stretch=NO, anchor="center")
    treeview_mail.heading("one", text="Name", anchor="center")

    treeview_mail.column("#2", minwidth=0, width=100, stretch=NO, anchor="center")
    treeview_mail.heading("two", text="Location", anchor="center")

    treeview_mail.column("#3", minwidth=0, width=100, stretch=NO, anchor="center")
    treeview_mail.heading("three", text="Date", anchor="center")
    
    treeview_mail.column("#4", minwidth=0, width=600, stretch=NO, anchor="center")
    treeview_mail.heading("four", text="Title", anchor="center")

    treeview_mail.bind("<Double-1>", double_click)               

    mail_list_group_main.rowconfigure(1, weight=1)
    mail_list_group_main.columnconfigure(0, weight=1)
        
#====================================================================================================
# MAIN CALL
#====================================================================================================
if __name__ == "__main__":

    root = Tk()
    # 초기 윈도우 셋팅
    root.title("dodam_mail_sev_scraping_result")
    # root.geometry("800x600+100+100")
    root.resizable(True, True)

    # UI 셋팅
    scraping_input()

    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    root.mainloop()
