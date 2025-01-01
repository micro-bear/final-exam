import requests #爬蟲請求專用
import json #JSON 格式解析器
import re #正則表達式處理函示
#自製模組針對各個Table做資料庫撈取邏輯
import venue
import company
import movie
import hall
import timeable

URL = "https://www.vscinemas.com.tw"

NAME = "威秀"

def run():
    print("開始抓取威秀影城電影")
    print("1.新增公司")
    brandRow = company.checkCompany(NAME)
    print("新增公司完成")
    print("2.取得場地")
    venues = getVenues() 
    venuesLen = len(venues)
    venueRows = []
    for index, item in enumerate(venues):
        print(f"新增場地[{(index+1)}/{venuesLen}]")
        venueRows.append(venue.checkVenue(brandRow['id'], item))
    print("新增場地完成")
    print("3.取得電影資料")
    movies = getMoviesDetail()
    movieRows = []
    moviesLen = len(movies)
    for index, item in enumerate(movies):
        print(f"新增電影[{(index+1)}/{moviesLen}]")
        movieRows.append(movie.checkMovie(item))
    
    for venueRow in venueRows:
        dic_movies = GetLstDicMovie(venueRow) #選擇場館
        print(f"取得場地{venueRow['name']}上映電影")
        hallRows = [] #(數位 國)音速小子 3
        dic_moviesLen = len(dic_movies)
        print(f"共{dic_moviesLen}部電影")
        for dic_movie in dic_movies:
            #分辨電影版本
            hall_name = re.search(r'^\((.*?)\)(.*+)', dic_movie['strText'], re.DOTALL) 
            #分辨電影名稱
            movie_name = hall_name.group(2) if hall_name and hall_name.group() else ""
            hallRow = hall.checkHall({
                "venue_id": venueRow["id"],
                "name": hall_name.group(1) if hall_name and hall_name.group() else "",
                "code": dic_movie["strValue"]
            })
            hallRows.append(hallRow)
            search_movie = next((item for item in movieRows if item["name"] == movie_name), None)
            if(search_movie is not None):
                venue.addMovie(venueRow["id"], search_movie["id"])
                dates = GetLstDicDate(venueRow, hallRow) #選擇電影
                dateRows = []
                for date in dates:
                    dateRow = movie.addDate(search_movie, date["strValue"].replace("/","-"))
                    dateRows.append(dateRow)
                    times = GetLstDicSession(venueRow, hallRow, date["strValue"]) #選擇日期
                    timeRows = []
                    for time in times:
                        timeRow = timeable.checkTime({
                            "name": time["strText"]
                        })
                        timeRows.append(timeRow)
                        hall.addDateTime(hallRow["id"], dateRow["id"], timeRow["id"])
    print("威秀電影資料輸入完成")
#提取威秀影城資料庫
def getVenues(): 
    data = GetLstDicCinema()
    return [{
        "name": item['strText'],
        "code": item['strValue']
    } for item in data]

#提取各威秀影城的電影資料庫
def GetLstDicMovie(venue):
    try:
        response = requests.get(URL + "/VsWeb/api/GetLstDicMovie?cinema=" + venue['code'])
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        print(err)

#提取各威秀影城電影播映日期資料庫
def GetLstDicDate(venue, hall):
    try:
        response = requests.get(URL + "/VsWeb/api/GetLstDicDate?cinema=" + venue['code'] + "&movie=" + hall["code"])
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        print(err)

#提取各威秀影城電影播映時間資料庫
def GetLstDicSession(venue, hall, date):
    try:
        response = requests.get(URL + "/VsWeb/api/GetLstDicSession?cinema=" + venue['code'] + "&movie=" + hall["code"] + "&date=" + date)
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        print(err)

#提取各威秀影城該電影詳細資料資料庫
def getMoviesDetail():
    try:
        movies = []
        response = requests.get(URL + "/vsweb/film/index.aspx")
        pageSection = re.findall(r'<section\sclass="pagebar">(.*?)<\/section', response.text, re.DOTALL)
        pages = re.findall(r'<a.*?>(\d+)<', pageSection[0], re.DOTALL)
        print(f"共{len(pages)}頁")
        for page in pages:
            print(f"第{page}頁")
            response = requests.get(URL + "/vsweb/film/index.aspx?p=" + page)
            movieSection = re.findall(r'<ul\sclass="movieList">(.*?)<\/ul>', response.text, re.DOTALL)
            movielis = re.findall(r'<li>(.*?)<\/li>', movieSection[0], re.DOTALL)
            movielisLen = len(movielis)
            for index, li in enumerate(movielis):
                print(f"取得電影資料[{(index+1)}/{movielisLen}]")
                movie = re.findall(r'h2><a\shref="(.*?)"', li, re.DOTALL)
                detailPage = requests.get(URL + "/vsweb/film/" + movie[0])
                detail = re.search(r'<section\sclass="movieDetail".*?>(.*?)<\/section', detailPage.text, re.DOTALL)
                detailHtml = detail.group(1) if detail and detail.group else ""
                name = re.search(r'<h1>(.*?)<\/h1>', detailHtml, re.DOTALL)
                name_en =re.search(r'<h2>(.*?)<\/h2>', detailHtml, re.DOTALL)
                release_time = re.search(r'<time>上映日期：(.*?)<\/time>', detailHtml, re.DOTALL)
                image = re.search(r'<img\ssrc="..(.*?)"', detailHtml, re.DOTALL)
                director = re.search(r'<td>導演：<\/td>.*?<p>(.*?)<', detailHtml, re.DOTALL)
                description = re.search(r'bbsArticle">(.*?)<\/div>', detailPage.text, re.DOTALL)
                movies.append({
                    "name": name.group(1) if name and name.group() else "",
                    "name_en": name_en.group(1) if name_en and name_en.group() else "",
                    "release_time": release_time.group(1) if release_time and release_time.group() else "",
                    "image": URL + "/vsweb" + image.group(1) if image and image.group() else "",
                    "director": director.group(1) if director and director.group() else "",
                    "description": description.group(1) if description and description.group() else "",
                    "vscinemas": 1
                })
        return movies
    except requests.exceptions.ConnectionError as err:
        print(err)

def GetLstDicCinema():
    try:
        response = requests.get(URL + "/VsWeb/api/GetLstDicCinema")
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        print(err)
