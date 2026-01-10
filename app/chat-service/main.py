from fastapi import FastAPI

app = FastAPI(title="Chat Service")

@app.get("/")
def read_root():
    return {"message": "Chat Service Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)