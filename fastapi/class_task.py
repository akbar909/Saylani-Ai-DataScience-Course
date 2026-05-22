from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory data store
items: Dict[int, dict] = {}

class Item(BaseModel):
	name: str
	description: str = None
	price: float

# Create
@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item):
	if item_id in items:
		raise HTTPException(status_code=400, detail="Item already exists")
	items[item_id] = item.dict()
	return {"item_id": item_id, "item": items[item_id]}

# Read
@app.get("/items/{item_id}")
def read_item(item_id: int):
	if item_id not in items:
		raise HTTPException(status_code=404, detail="Item not found")
	return {"item_id": item_id, "item": items[item_id]}

# Update
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
	if item_id not in items:
		raise HTTPException(status_code=404, detail="Item not found")
	items[item_id] = item.dict()
	return {"item_id": item_id, "item": items[item_id]}

# Delete
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
	if item_id not in items:
		raise HTTPException(status_code=404, detail="Item not found")
	deleted = items.pop(item_id)
	return {"item_id": item_id, "deleted": deleted}

