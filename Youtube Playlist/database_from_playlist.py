import httplib2
import sys
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests
from time import sleep

# options.add_argument('headless') #크롬창이 띄워지지 않도록 하는 headless모드 옵션이다.

url = "https://www.youtube.com/playlist?list=PLtZUBC99r0scIZ_elUV-fov5TpCMVdHLJ"# 크롤링할 플레이리스트 지정
TIMESTAMP_URL = "https://www.youtube.com/playlist?list=PLtZUBC99r0sd8f5zf2QmJW8AqijyFMYmv" # 타임 스탬프 링크

# 재생목록 링크 목록 가져오기
def selenium_YT_Playlist_Crawler(url, soup_name):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(10) #창이 로드될때까지 10초기다리고, 로드 다되면 10초 굳이 안기다리고 다음 코드실행

    searching = driver.find_element_by_name("search_query")
    searching.send_keys('우주하마 생방송')

    playlist_body = driver.find_element_by_css_selector("body")
    PAGE_DOWN = '\ue00f'
    num_of_scroll = 1000

    while num_of_scroll:
        playlist_body.send_keys(Keys.PAGE_DOWN)
        num_of_scroll -= 1

    # 셀레니움 데이터 추출
    source = driver.page_source
    soup_name = BeautifulSoup(source, 'html.parser')
    return soup_name
    driver.Quit() # 셀레니움 종료
    print("selenium Done")

# 재생목록 데이터 가져오기
playlist_soup = selenium_YT_Playlist_Crawler(url, "playlist_soup")
# print(selenium_YT_Playlist_Crawler(url, "playlist_soup"))

# 블랙리스트 재생목록 데이터 가져오기
blacklist = selenium_YT_Playlist_Crawler(TIMESTAMP_URL, "blacklist")
# print(blacklist)

# 데이터에서 href 내부에 있는 링크 추출
def data_manufacturing(soup, links_name):
    links_name = []
    data_list = soup.select("a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer")
    for data in data_list:
        links_name.append(data.attrs['href'])
    # print(href)

    # 링크 리스트 가공
    href_index = 0
    for href_new in links_name:
        links_name[href_index] = "https://youtu.be/" + href_new[9:20]
        href_index += 1
    # print(links_name)
    print("links Done")
    return links_name

def main(): # 리턴 사용 위해 함수로
    # 링크들 가공
    links = data_manufacturing(playlist_soup, "links")

    # 블랙리스트 가공
    blacklists = data_manufacturing(blacklist, "blacklists")

    # 재생목록 링크들 중복 제거
    # print(len(links))
    new_links = []
    for v in links:
        if v not in new_links:
            new_links.append(v)
    print(new_links)
    # print(len(new_links))

    # 재생목록 링크들에서 블랙리스트 제거
    for timestamp in blacklists:
        links.remove(timestamp)
    print("Filtering Done")

    # 영상 정보 크롤링
    # links = ['https://youtu.be/dCAetQcwogA']
    database = []
    titles = []
    dates = []
    info_number = 1
    playlist_database_for_merge = []
    for link in links:
        try:
            video_html = requests.get(link).text
            viedo_soup = BeautifulSoup(video_html, "html.parser", from_encoding="utf-8")
        
        except:
            # 오류 발생시 잠시 기다렸다 다시 시도
            print("Oops! Wait a second.")
            sleep(5)
            video_html = requests.get(link).text
            viedo_soup = BeautifulSoup(video_html, "html.parser", from_encoding="utf-8")

        # print(viedo_soup) # 전체 내용 출력

        # 영상 제목
        titles.append(str(viedo_soup.select("title"))[8:-18])
        # print(str(viedo_soup.select("title"))[8:-18])
        
        # 영상 날짜
        # date = viedo_soup.select("meta")[-1] # 밑에꺼 잘 되면 삭제
        date = viedo_soup.select("meta")
        for meta in date:
            if "startDate" in str(meta):
                new_date = str(meta)[15:25].replace("-", ".")
                
        hyperlink = '=HYPERLINK("' + link + '", "' + str(viedo_soup.select("title"))[8:-18]
        # UI 개선 후 활성화
        # 썸네일 (720)
        # thumbnail_link = "https://i.ytimg.com/vi/" + str(link)[17:] + "/maxresdefault.jpg"
        # print(thumbnail_link)
        # thumbnail_html = requests.get(thumbnail_link).text
        # thumbnail_soup = BeautifulSoup(thumbnail_html, "html.parser")

        print("Info Done " + str(info_number))
        info_number += 1
        print(new_date)

        # spreadsheets_data = [[DATA1, URL1, TITLE1,KEYWORD1,GAME1],[DATA2, URL2, TITLE2,KEYWORD2,GAME2],[DATA3, URL3, TITLE3,KEYWORD3,GAME3]]
        group = [] # 한 영상에 대한 정보
        group.append(new_date)
        group.append('=HYPERLINK("' + link + '", "' + str(viedo_soup.select("title"))[8:-18] + '")') 
        database.append(group)
        data = [] # 초기화
        data.append(new_date)
        data.append(hyperlink)
        playlist_database_for_merge.append(data)

    print(playlist_database_for_merge)
    return playlist_database_for_merge

    f = open("selenium_DB.txt", 'w', encoding='utf8')
    for data in database:
        f.write(str(data[0]) + "$" + str(data[1]) + "$" + "$" + "$" + "\n")
    f.close()

main()