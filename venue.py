import db

table_name = "venues"

def checkVenue(company_id, data):
    venue = getVenue(data['name'])
    if(venue is None):
        db.insert(table_name, {
            "company_id": company_id,
            "name": data['name'],
            "code": data['code']
        })
    else:
        return venue
    return getVenue(data['name'])

def getVenue(name):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `name` = ?"
    database.execute(sql, [name])
    return database.fetchone()

def getVenueById(code):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `code` = ?"
    database.execute(sql, [code])
    return database.fetchone()

def getVenueByCompanyId(company_id):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `company_id` = ?"
    database.execute(sql, [company_id])
    return database.fetchall()

def addMovie(venue_id, move_Id):
    table = "venue_has_movie"
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table} Where `venue_id` = ? and `movie_Id` = ?;"
    database.execute(sql, [venue_id, move_Id])
    search = database.fetchone()
    if(search is None):
        db.insert(table, {
            "venue_id": venue_id,
            "movie_Id": move_Id,
        })