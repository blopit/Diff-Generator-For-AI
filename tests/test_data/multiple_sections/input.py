from fastapi import FastAPI

@app.get("/items/")
async def read_items():
    return {"message": "Hello World"}

@app.post("/users/")
async def create_user():
    return {"message": "User created"}

# rest of the file 