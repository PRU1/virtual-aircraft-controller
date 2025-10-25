from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import shutil

app = FastAPI()

FILE_DIR = "data/" # where to store files
os.makedirs(FILE_DIR, exist_ok = True) # make sure the directory exists

def process_file(file_path : str):
    return f"the file read is {file_path}"

# read and process file from directory
@app.get("/process/{file_name}")
def process_existing_file(filename : str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": filename, "result": result}

# allow uploads from frontend
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)): # async load means if the server is bogged down, it can handle other requests first.
    file_path = os.path.join(FILE_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"detail": f"File '{file.filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    


'''
# OLD 
# Pydantic model to define the structure of a ToDo item
class ToDoItem(BaseModel):
    id: int
    title: str
    description: str = None

# Simulating an in-memory database with a dictionary
to_do_list = {}

# CRUD Operations

# Create a new to-do item
@app.post("/todos/", response_model=ToDoItem)
def create_todo_item(todo_item: ToDoItem):
    if todo_item.id in to_do_list:
        raise HTTPException(status_code=400, detail="To-do item already exists")
    to_do_list[todo_item.id] = todo_item
    return todo_item

# Get a single to-do item by ID
@app.get("/todos/{todo_id}", response_model=ToDoItem)
def read_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    return to_do_list[todo_id]

# Update an existing to-do item
@app.put("/todos/{todo_id}", response_model=ToDoItem)
def update_todo_item(todo_id: int, todo_item: ToDoItem):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    to_do_list[todo_id] = todo_item
    return todo_item

# Delete a to-do item
@app.delete("/todos/{todo_id}")
def delete_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    del to_do_list[todo_id]
    return {"detail": "To-do item deleted"}
'''
from pydantic import BaseModel
import os

app = FastAPI()

FILE_DIR = "data/" # where to store files

def process_file(file_path : str):
    return f"the file read is {file_path}"

# read and process file from directory
@app.get("/process/{file_name}")
def process_existing_file(filename : str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    result = process_file(file_path)
    return {"filename": filename, "result": result}

# allow uploads from frontend
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)): # async load means if the server is bogged down, it can handle other requests first.
    file_path = os.path.join(FILE_DIR, file.filename)
    return {"detail": f"file {file.filename} uploaded yippiee"}
    


'''
# OLD 
# Pydantic model to define the structure of a ToDo item
class ToDoItem(BaseModel):
    id: int
    title: str
    description: str = None

# Simulating an in-memory database with a dictionary
to_do_list = {}

# CRUD Operations

# Create a new to-do item
@app.post("/todos/", response_model=ToDoItem)
def create_todo_item(todo_item: ToDoItem):
    if todo_item.id in to_do_list:
        raise HTTPException(status_code=400, detail="To-do item already exists")
    to_do_list[todo_item.id] = todo_item
    return todo_item

# Get a single to-do item by ID
@app.get("/todos/{todo_id}", response_model=ToDoItem)
def read_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    return to_do_list[todo_id]

# Update an existing to-do item
@app.put("/todos/{todo_id}", response_model=ToDoItem)
def update_todo_item(todo_id: int, todo_item: ToDoItem):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    to_do_list[todo_id] = todo_item
    return todo_item

# Delete a to-do item
@app.delete("/todos/{todo_id}")
def delete_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    del to_do_list[todo_id]
    return {"detail": "To-do item deleted"}
'''