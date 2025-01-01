import db

table_name = "companies"

def checkCompany(name):
    company = getCompany(name)
    if(company is None):
        db.insert(table_name, {
            "name": name
        })
    else :
        return company
    return getCompany(name)
    
def getCompany(name):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name} Where `name` = ?"
    database.execute(sql, [name])
    return database.fetchone()

def selectCompany(data = {}):
    connection, database = db.connect_db()
    sql = f"SELECT * FROM {table_name}"
    if(data):
        sql += sql + " Where " + " AND ".join([f"{key} = ?" for key, value in data.items()])
    database.execute(sql, data)
    return database.fetchall()
