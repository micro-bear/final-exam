import db

table_name = "timeables"

def checkTime(data):
    time = getTime(data['name'])
    if(time is None):
        db.insert(table_name, {
            "name": data['name'],
        })
    else :
        return time
    return getTime(data['name'])
    
def getTime(name):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `name` = ?"
    database.execute(sql, [name])
    return database.fetchone()

