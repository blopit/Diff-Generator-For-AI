@app.get("/items/")
async def read_items():
    return {"message": "Hello World"} 