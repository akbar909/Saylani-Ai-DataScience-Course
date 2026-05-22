from fastapi import FastAPI
import random
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get('/welcome')
def welcome():
    return {"message": "Welcome to FastAPI!"}

@app.get('/add')
def add():
    return {"add ": 2 + 3}

@app.get('/subtract')
def subtract():
    return {"subtract": 5 - 2}

@app.get('/multiply')
def multiply():
    return {"multiply": 3 * 4}

@app.get('/divide')
def divide():
    return {"divide": 8 / 2}

@app.get('/modulus')
def modulus():
    return {"modulus": 10 % 3}

@app.get('/power')
def power():
    return {"power": 2 ** 3}

@app.get('/greet/{name}')
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get('/random')
def randnum():
    return {"random_number": random.randint(1, 100)}