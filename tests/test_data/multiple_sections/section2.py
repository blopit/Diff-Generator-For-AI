@app.post("/users/")
async def create_user():
    return {"message": "User created"} 