import requests
import json
import venue
import company
import movie
import hall
import timeable
from datetime import datetime
import pytz

URL = "https://capi.showtimes.com.tw"

NAME = "秀泰"

def run():
    print("開始抓取秀泰影城電影")
    print("1.新增公司")
    brandRow = company.checkCompany(NAME)
    print("新增公司完成")
    print("2.取得場地")
    venues = getVenues()
    venuesLen = len(venues)
    venueRows = []
    venueObject = {}
    for index, item in enumerate(venues):
        print(f"新增場地[{(index+1)}/{venuesLen}]")
        venueRow = venue.checkVenue(brandRow['id'], item)
        venueRows.append(venueRow)
        venueObject[venueRow['id']] = item['venueIds']
    print("新增場地完成")
    print("3.取得電影資料")
    movies = getMovies()
    movieRows = []
    moviesLen = len(movies)
    for index, item in enumerate(movies):
        print(f"新增電影[{(index+1)}/{moviesLen}]")
        movieRows.append(movie.checkMovie(item))

    data = getBootstrap()
    for movieRow in movieRows:
        movieDetail = getMovieDetail(movieRow['showtimes'])

        for item in movieDetail['payload']['venues']:
            for id, venueObjectItem in venueObject.items():
                if(item['id'] in venueObjectItem):
                    venue.addMovie(id, movieRow['id'])
            
        events = movieDetail['payload']['events']
        for date in list(set([datetime.strptime(item['startedAt'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d") for item in events])):
            dateRow = movie.addDate(movieRow, date)
        
        # print(movieDetail)
            if(len(movieDetail['payload']['programs']) > 0):
                # for venue_id in movieDetail['payload']['programs'][0]['meta']['availableCorporationIds']:
                #     venueDetail = venue.getVenueById(venue_id)
                    
                hallRows = []
                for hallItem in [{
                    "corporationId": item['corporationId'],
                    "code": item['programId'],
                    "name": item['meta']['format'],
                    "time": item['startedAt']
                } for item in events]:
                    venueDetail = venue.getVenueById(hallItem['corporationId'])

                    hallRow = hall.checkHall({
                        "venue_id": venueDetail['id'],
                        "name": hallItem['name'],
                        "code": hallItem["code"]
                    })
                    time = datetime.strptime(hallItem["time"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).strftime("%H:%M")
                    timeRow = timeable.checkTime({
                        "name": time
                    })
                    hall.addDateTime(hallRow["id"], dateRow["id"], timeRow["id"])
                    hallRows.append(hallRow)
    print("秀泰電影資料輸入完成")

def getVenues():
    data = getBootstrap()
    return [{
        "name": item['name'],
        "code": item['id'],
        "venueIds": item['venueIds']
    } for item in data['payload']['corporations']]

def getMovies():
    data = getBootstrap()
    return [{
        "name": item['name'],
        "name_en": item['nameAlternative'],
        "release_time": datetime.strptime(item['availableAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d"),
        "image": item['coverImagePortrait']['url'],
        "director": item['meta']['directors'][0],
        "description": item['description'],
        "showtimes": item['id']
    } for item in data['payload']['programs']]

def getBootstrap():
    try:
        data = {
            'status': True,
            'message': "",
            'data': ''
        }
        response = requests.get(URL + "/1/app/bootstrap")
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        data['status'] = False
        data['message'] = f"無法連接網站：{err}" 

def getMovieDetail(id):
    try:
        data = {
            'status': True,
            'message': "",
            'data': ''
        }
        response = requests.get(URL + "/1/events/listForProgram/" + id + "?date=" + datetime.today().strftime("%Y-%m-%d"))
        data = json.loads(response.text)
        return data
    except requests.exceptions.ConnectionError as err:
        data['status'] = False
        data['message'] = f"無法連接網站：{err}" 
        