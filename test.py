from main import DataBase

db = DataBase()
result = db.search_customer(("", "", "b"))
print(result)