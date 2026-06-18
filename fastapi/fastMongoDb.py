from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# MongoDB setup
# Note: In a real app, keep your connection string in an environment variable!
mongo_client = MongoClient("")
db = mongo_client["todo_app"]
todos_collection = db["todos"]

# Check MongoDB connection
try:
    mongo_client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Define a Pydantic model for Todo
class Todo(BaseModel):
    title: str
    completed: bool = False

# Helper function to serialize MongoDB documents
def serialize_todo(todo):
    """Converts MongoDB _id to string and returns a clean dict."""
    if todo is None:
        return None
    # Convert the ObjectId to a string and store it in 'id'
    todo["id"] = str(todo.get("_id"))
    # Remove the original _id key so JSON encoder doesn't crash
    if "_id" in todo:
        del todo["_id"]
    return todo

@app.get("/")
def root():
    return {"message": "Welcome to the Todo API!"}

@app.post("/todos")
def create_todo(todo: Todo):
    # .dict() is for Pydantic v1; use .model_dump() if using Pydantic v2
    todo_dict = todo.dict()
    
    # MongoDB inserts the document and adds '_id' to todo_dict automatically
    result = todos_collection.insert_one(todo_dict)
    
    # We use our helper to clean up the dict before returning
    # This ensures the 'id' is a string and the 'ObjectId' is gone
    return jsonable_encoder(serialize_todo(todo_dict))

@app.get("/todos")
def get_all_todos():
    todos = []
    # Find all documents and clean each one
    for doc in todos_collection.find():
        todos.append(serialize_todo(doc))
    return jsonable_encoder(todos)

@app.get("/todos/{todo_id}")
def get_todo(todo_id: str):
    try:
        todo = todos_collection.find_one({"_id": ObjectId(todo_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
        
    return jsonable_encoder(serialize_todo(todo))

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    try:
        result = todos_collection.delete_one({"_id": ObjectId(todo_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: str, todo: dict = Body(...)):
    try:
        # Validate the ID format
        todo_id_obj = ObjectId(todo_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Ensure the request body contains valid fields
    if not todo:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # Update the todo in the database
    result = todos_collection.update_one({"_id": todo_id_obj}, {"$set": todo})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Return the updated todo
    updated_todo = todos_collection.find_one({"_id": todo_id_obj})
    return jsonable_encoder(serialize_todo(updated_todo))
