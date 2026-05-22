from fastapi import FastAPI, HTTPException
from fastapi import create_todo, get_todo, update_todo, delete_todo
from pydantic import BaseModel

app = FastAPI() 

@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do API!"}

@app.post("/todos/")
def create_todo(todo: create_todo):
    return {"message": "To-Do item created successfully.", "todo": todo}
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    return {"message": f"Details of To-Do item with ID {todo_id}."}
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: update_todo):
    return {"message": f"To-Do item with ID {todo_id} updated successfully.", "updated_todo": todo}
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    return {"message": f"To-Do item with ID {todo_id} deleted successfully."}
