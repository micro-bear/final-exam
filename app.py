import showTime
import vscinemas
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkcalendar import Calendar
import company
import venue
import db
from PIL import ImageTk, Image
from urllib.request import urlopen

brands = [
        vscinemas,
        showTime,
    ]

def getData():
    for brand in brands:
        brand.run() #執行爬蟲的資料庫

# getData()

window = tk.Tk()
window.title('電影資訊查詢系統')
window.geometry('1280x640')

#配合卷軸功能的設定左半邊顯示畫面
canvas = tk.Canvas(window)
canvas.place(relx=0, rely=0, relwidth=0.5, relheight=1)

#設定左半邊卷軸功能
scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

#新增一個左半邊視窗
FormFrame = tk.Frame(canvas, background='#343434')
canvas.create_window((0, 0), window=FormFrame, anchor="nw")

#設定卷軸高度
def configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
FormFrame.bind("<Configure>", configure_canvas)

#配合卷軸功能的設定右半邊顯示畫面
contentCanvas = tk.Canvas(window)
contentCanvas.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

#設定右半邊卷軸功能
contentScrollbar = tk.Scrollbar(contentCanvas, orient="vertical", command=contentCanvas.yview)
contentScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
contentCanvas.configure(yscrollcommand=contentScrollbar.set)

#新增一個右半邊視窗
contentFrame = tk.Frame(contentCanvas, background='#565656')
contentCanvas.create_window((0, 0), window=contentFrame, anchor="nw")

#設定卷軸高度
def content_canvas(event):
    contentCanvas.configure(scrollregion=contentCanvas.bbox("all"))
contentFrame.bind("<Configure>", content_canvas)

#設定標題
dateLabel = tk.Label(FormFrame, text='1. 選擇看電影日期')
dateLabel.grid(column=0, row=0)

#設定日期選擇器
calendar = Calendar(FormFrame, selectmode="day", date_pattern="yyyy-mm-dd")
calendar.grid(column=0, row=1)

#設定標題勾選影城名稱
venueLabel = tk.Label(FormFrame, text='2. 選擇場館')
venueLabel.grid(column=0, row=2)

check_vars = []

#提取資料庫公司資料
companies = company.selectCompany()

#依據資料庫分類顯示畫面
for companyIndex, companyItem in enumerate(companies):
    tk.Label(FormFrame, text=companyItem['name']).grid(column=(0 + companyIndex), row=3)
    venues = venue.getVenueByCompanyId(companyItem['id'])
    for venueIndex, venueItem in enumerate(venues):
        var = tk.IntVar()
        check_vars.append(var)
        tk.Checkbutton(FormFrame, text=venueItem['name'], onvalue=venueItem['id'], variable=var).grid(column=(0 + companyIndex), row=(4+venueIndex))

#顯示電影時刻表
def showMovieTimeable(event):
    clicked_frame = event.widget
    movie_id = clicked_frame.id
    
    #清空畫面
    for widget in contentFrame.winfo_children():
        widget.destroy()
    print('開始搜尋時間')

    #取得選擇日期
    date = calendar.get_date().replace("/","-")

    #取得勾選影城
    searchVenues = [var.get() for var in check_vars if var.get() != 0]
    print('查詢日期:' + date)
    print('查詢場館:')
    print(searchVenues)
    
    connection, database = db.connect_db()

    #查詢選擇日期及電影ID
    movieDateSql = f"SELECT * FROM `movie_date` Where `movie_id` = ? AND `date` = ?"
    database.execute(movieDateSql, [movie_id, date])
    movieDateIds = [item['id'] for item in database.fetchall()]

    #提取勾選資料
    venueSql = f"SELECT * FROM `venues` Where `id` in ({",".join(map(str, searchVenues))})"
    database.execute(venueSql)
    venues = database.fetchall()
    data = []
    for item in venues:
        itemData = dict(item)

        #提取電影分類的資料表
        hallSql = f"SELECT * FROM halls Where `venue_id` = ?"
        database.execute(hallSql, [item['id']])
        halls = database.fetchall()
        itemData['halls'] = []
        for itemHall in halls:
            itemHallDict = dict(itemHall)

            #透過資料表找尋時刻表
            timeSql = f"SELECT timeables.* FROM `hall_has_movie` LEFT JOIN `timeables` on `timeables`.`id` = `hall_has_movie`.`timeable_id` Where `hall_id` = ? AND `movie_date_id` in ({",".join(map(str, movieDateIds))}) ORDER BY `timeables`.`name`"
            database.execute(timeSql, [itemHallDict['id']])
            itemHallDict['times'] = database.fetchall()
            if len(itemHallDict['times']) > 0 :
                itemData['halls'].append(itemHallDict)
        data.append(itemData)
        
    #顯示時刻表
    i = 0
    for item in data:
        timeFrame = tk.Frame(contentFrame)
        venueLabel = tk.Label(timeFrame, text=item['name'])
        if len(item['halls']) > 0:
            venueLabel.grid(column= 0, row = 0, columnspan= len(item['halls']))
            j = 0
            for hall in item['halls']:
                hallLabel = tk.Label(timeFrame, text=hall['name'])
                hallLabel.grid(column=j, row = 1)
                k = 0
                for time in hall['times']:
                    timeLabel = tk.Label(timeFrame, text=time['name'])
                    timeLabel.grid(column=j, row= (k + 2))
                    k = k + 1
                j = j + 1
            timeFrame.grid(column = (i + 4), row = 0)
            i = i + 1


photo_cache = []

#顯示電影
def searchMovies():
    #清除右邊畫面
    for widget in contentFrame.winfo_children():
        widget.destroy()
    print('開始搜尋')
    #取得選擇日期
    date = calendar.get_date().replace("/","-")
    #取得勾選影城
    venues = [var.get() for var in check_vars if var.get() != 0]
    print('查詢日期:' + date)
    print('查詢場館:')
    print(venues)
    connection, database = db.connect_db()
    #顯示該影城上映電影
    sql = f"SELECT movies.* FROM `venue_has_movie` Left Join `movies` on `movies`.`id` = `venue_has_movie`.`movie_id` Where `venue_id` in ({",".join(map(str, venues))}) Group By movie_id Order by movie_id;"
    database.execute(sql)
    venue_has_movies = database.fetchall()
    #顯示勾選日期有的電影
    dateSql = f"SELECT * FROM `movie_date` Where `date` = '{date}'"
    database.execute(dateSql)
    movieDates = [item['movie_id'] for item in database.fetchall()]
    movies = []
    i = 0
    j = 0
    for item in venue_has_movies:
        if(item['id'] in movieDates ):
            movies.append(item)
            movieFrame = tk.Frame(contentFrame)
            movieFrame.id = item['id']
            movieFrame.pack_propagate(False)
            #建立圖片
            photo = ImageTk.PhotoImage(Image.open(urlopen(item['image'])).resize((150, 300)))
            photo_cache.append(photo)
            movieImage = tk.Label(
                movieFrame,
                image=photo,
                text="",
                bg="lightgray",
                width=100,
                height=200
            )
            movieImage.id = item['id']
            movieImage.grid(column=0,row=0)
            #建立名稱
            movieName = tk.Label(movieFrame, text=item['name'])
            movieName.id = item['id']
            movieName.grid(column=0, row=1)
            movieFrame.grid(column = (i + 4), row = j)
            #綁定時刻表顯示該影片資訊
            movieImage.bind("<Button-1>", showMovieTimeable)
            movieName.bind("<Button-1>", showMovieTimeable)
            movieFrame.bind("<Button-1>", showMovieTimeable)
            if(i == 2):
                i = 0
                j = j + 1
            else:
                i = i + 1
    return movies

#新增查詢按鈕
tk.Button(FormFrame, text='查詢', command = searchMovies).grid(column=3, row=0)

window.mainloop()