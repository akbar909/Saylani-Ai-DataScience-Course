from fastapi import FastAPI, HTTPException
from database import create_todo_items, get_todo_items, update_todo_items, delete_todo_items

app = FastAPI()

@app.get("/")
def health_check():
    return {
        "Message":"API Run Sucessfully"
    }

@app.post("/v1/todo")
def create_task(task:str):
   
   #step 01 : Getting Create Module for task
    task_create = create_todo_items(task)
    if task_create:

        return {
            "Message" : "Task Added Successfully."
        }
    
   
@app.get("/v1/todo")
def get_task():
    itemsFetch = get_todo_items()
    # print("Items", itemsFetch)
    return {
        "Message" : "Items Fetch successfully",
         "Items" : itemsFetch 
    }


@app.put("/v1/todo/")
def update_task(todo_id: int, task: str):

    result = update_todo_items(task, todo_id)

    if result:
        return {
        "Message" : "Task Updated Succuessfully"
    }

@app.delete("/v1/todo/")
def delete_task(todo_id):

    result = delete_todo_items(todo_id)

    if result:

        return {
        "Message" : "Task Deleted Succuessfully"
    }