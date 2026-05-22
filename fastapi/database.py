import sqlite3
from fastapi import HTTPException

# Initilization the DB conn
def get_db():
    conn = sqlite3.connect("todo.db")
    # print(conn)
    conn.row_factory = sqlite3.Row
    # print(conn)
    return conn

# Establishing a DB connection 
conn = get_db()

#Create the DB table
conn.execute(""" CREATE TABLE IF NOT EXISTS TODO ( id INTEGER PRIMARY KEY AUTOINCREMENT,
task TEXT NOT NULL ) """)

conn.commit()

# Closing the DB Connection
conn.close()



# Create Todo List Items in DB

def create_todo_items(task: str):
    conn = get_db()
    query = conn.execute(" INSERT INTO TODO (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

    return True


def get_todo_items():
    conn = get_db()
    query = conn.execute("SELECT * FROM TODO ").fetchall()
    conn.close()

    return query

def update_todo_items(task, todo_id):
    conn = get_db()
    query = conn.execute("UPDATE TODO SET task=? WHERE id=?", (task, todo_id))
    if query.rowcount == 0:
        raise HTTPException(status_code=404, detail='Task Not Found')

    conn.commit()
    conn.close()

    return True

def delete_todo_items(todo_id):

    conn = get_db()
    query = conn.execute("DELETE FROM TODO WHERE id = ?",(todo_id,))
    if query.rowcount == 0:
        raise HTTPException(status_code=404, detail='Task Not Found')
    conn.commit()
    conn.close()

    return True
