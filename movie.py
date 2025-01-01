import db

table_name = "movies"

def checkMovie(data):
    movie = getMovie(data['name'])
    if(movie is None):
        db.insert(table_name, data)
    else:
        update = {}
        if "showtimes" in data:
            update['showtimes'] = data['showtimes']
        if "vscinemas" in data:
            update['vscinemas'] = data['vscinemas']
        db.update(table_name, update, movie['id'])
    return getMovie(data['name'])

def getMovie(name):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `name` = ?"
    database.execute(sql, [name])
    return database.fetchone()

def getDate(movie_id, date):
    table = "movie_date"
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table} Where `movie_id` = ? and `date` = ?;"
    database.execute(sql, [movie_id, date])
    return database.fetchone()

def addDate(movie, date):
    
    search = getDate(movie["id"], date)
    if(search is None):
        db.insert("movie_date", {
            "movie_id": movie["id"],
            "date": date,
        })
        search = getDate(movie["id"], date)

    return search