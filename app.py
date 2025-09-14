from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="Ticket to Ride API")

@app.get("/")
def read_root():
    return {"message": "Ticket to Ride Backend API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/test")
def test():
    return {"message": "API is working", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
