import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import os
import zipfile

def get_video_title(url):
    try:
        video_html = requests.get(url).text
        viedo_soup = BeautifulSoup(video_html, "html.parser", from_encoding="utf-8")
    
    except:
        # 오류 발생시 잠시 기다렸다 다시 시도
        print("Oops! Wait a second.")
        sleep(5)
        video_html = requests.get(url).text
        viedo_soup = BeautifulSoup(video_html, "html.parser", from_encoding="utf-8")

    # print(viedo_soup) # 전체 내용 출력

    # 영상 제목
    youtube_upload_title = str(viedo_soup.select("title"))[8:-18]
    return youtube_upload_title

# 스프레드시트 데이터 html로 다운로드

def main(): # 리턴 사용 위해 함수로
    spreadsheets_link = "https://docs.google.com/spreadsheets/d/1JRwO_BMLQjN6nm8t27PjPBYQwMfPE4RQmy3GlOsAm7E/edit#gid=0"

    # 기본 다운로드 경로 지정
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : r"C:\Users\Yoon\Documents\Visual Studio Code\Youtube Playlist"}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # driver = webdriver.Chrome()
    driver.get(spreadsheets_link)
    time.sleep(4)

    def spreadsheets_download():
        driver.find_element_by_id("docs-file-menu").click()
        print("파일")

        time.sleep(1)
        # driver.find_element_by_id(":5b").click()

        # 마우스 좌표로 html 다운
        actionchains = ActionChains(driver)
        actionchains.move_by_offset(150, 310)
        actionchains.perform()
        print("다운로드")
        time.sleep(1)

        actionchains = ActionChains(driver)
        actionchains.move_by_offset(125, 110)
        actionchains.click()
        actionchains.perform()
        print("HTML")

        # driver.quit()
        print("Selenium Done")

    #########################################

    try:
        spreadsheets_download()
    except:
        print("downloading Failed")
        
    # 다운로드 된 파일 관리
    
    old_name = r"C:\Users\Yoon\Documents\Visual Studio Code\Youtube Playlist\우주하마 생방송 아카이브 V2.zip"
    new_name = r"C:\Users\Yoon\Documents\Visual Studio Code\Youtube Playlist\spreadsheet_data.zip"
    time.sleep(5) # 다운로드 완료까지 대기
    try:
        os.remove(new_name) # 이전 데이터 삭제
    except:
        print("There is no old version")
        
    try:
        os.rename(old_name, new_name) # 다운로드 한 파일 이름 변경
        print("Downloading Done")
    except:
        print("File is not downloaded")

    # 압축 해제
    spreadsheet_zip = zipfile.ZipFile(r"C:\Users\Yoon\Documents\Visual Studio Code\Youtube Playlist\spreadsheet_data.zip")
    print(spreadsheet_zip.namelist())
    sheets_html = spreadsheet_zip.read('아카이브 모바일.html')
    sheets_soup = BeautifulSoup(sheets_html, "html.parser")
    # print(sheets_soup.prettify) # HTML 출력

    base_list = sheets_soup.select("tr")
    new_list = []

    # 영상별로 리스트 객체 나누기
    for s in base_list:
        new_list.append(s.select("td"))

    new_list.pop(0)
    new_list.pop(1)
    # print(new_list)

    spreadsheets_database = []
    spreadsheets_database_for_merge = []
    data_for_merge = [] # [data, hyperlink, yotube_upload_hyperlink, keyword, game]
    for s in new_list: 
        if len(s) == 5:
            # 날짜
            date = s[0].get_text()

            # 링크 / 제목으로 하이퍼링크 재구성
            link = s[1].select("a") # td 내의 a 태그 선택
            if not link:
                print("Empty")
            else :
                link = link[0].attrs["href"] # a 태그에서 링크 추출
            title = s[1].get_text() # 제목 추출
            hyperlink = '=HYPERLINK("' + str(link) + '", "' + str(title) + '")' # 하이퍼링크 생성
            youtube_upload = s[2].get_text() # 유튜브 업로드

            # 유튜브 업로드 하이퍼링크 관리
            mode = "" # 모드 초기화
            try:
                youtube_upload_link = s[2].select("a") # 하이퍼링크로 걸렸는지 확인
                youtube_upload_link = youtube_upload_link[0].attrs["href"]
                mode = "hyperlink" # 하이퍼링크로 처리하도록 모드 설정
            except: # a 태그가 없을시 그냥 넘김
                mode = ""
                
            # 모바일에선 하이퍼링크 걸기가 어렵기 때문에 링크만 입력해도 제목 크롤링해서 하이퍼링크로 만들기        
            
            if "https" in youtube_upload: # "https" 유무로 링크인지 아닌지 판단 - 링크만 걸렸을 시
                youtube_upload_title = get_video_title(youtube_upload)
                youtube_upload_hyperlink = '=HYPERLINK("' + str(youtube_upload) + '", "' + youtube_upload_title + '")'
                # print("just link")
                
            elif mode == "hyperlink": # 하이퍼링크 모드일 때
                youtube_upload_title = youtube_upload # td에 걸린 텍스트값은 영상 제목
                youtube_upload_hyperlink = '=HYPERLINK("' + str(youtube_upload_link) + '", "' + str(youtube_upload_title) + '")' # 유튜브 업로드 하이퍼링크 생성
                # print("hyperlink")

            else:
                youtube_upload_hyperlink = ""
                # print("Wrong format!")
            
            # youtube_upload_hyperlink = '=HYPERLINK("' + str(youtube_upload_link) + '", "' + str(youtube_upload_title) + '")' # 유튜브 업로드 하이퍼링크 생성
            keyword = s[3].get_text() # 키워드
            game = s[4].get_text() # 게임

            data = str(date) + "$" + hyperlink + "$" + youtube_upload_hyperlink + "$" + str(keyword) + "$" + str(game)
            spreadsheets_database.append(data)
            data_for_merge = [] # 초기화
            data_for_merge.append(date)
            data_for_merge.append(hyperlink)
            data_for_merge.append(youtube_upload_hyperlink)
            data_for_merge.append(keyword)
            data_for_merge.append(game)
            spreadsheets_database_for_merge.append(data_for_merge)

    print(spreadsheets_database_for_merge)
    return spreadsheets_database_for_merge

    f = open("spreadsheets_DB.txt", 'w', encoding='utf8')
    for data in spreadsheets_database:
        f.write( data + "\n")
    f.close()

main()