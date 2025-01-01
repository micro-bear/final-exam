import db

table_name = "halls"

def checkHall(data):
    company = getHall(data['code'], data["venue_id"])
    if(company is None):
        db.insert(table_name, {
            "venue_id": data["venue_id"],
            "name": data['name'],
            'code': data['code']
        })
    else :
        return company
    return getHall(data['code'], data["venue_id"])
    
def getHall(code, venue_id):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `code` = ? AND `venue_id` = ?"
    database.execute(sql, [code, venue_id])
    return database.fetchone()

def addDateTime(hall_id, movie_date_id, timeable_id):
    table = "hall_has_movie"
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table} Where `hall_id` = ? and `movie_date_id` = ? and `timeable_id` = ?;"
    database.execute(sql, [hall_id, movie_date_id, timeable_id])
    search = database.fetchone()
    if(search is None):
        search = db.insert(table, {
            "hall_id": hall_id,
            "movie_date_id": movie_date_id,
            "timeable_id": timeable_id
        })

    return search