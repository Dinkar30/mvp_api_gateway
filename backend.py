from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "the backend service is working"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/data")
async def get_data():
    return {"id": "1", "service": "Backend "}

@app.post("/test-post")
async def test_post(data: dict):
    return {"received":data}