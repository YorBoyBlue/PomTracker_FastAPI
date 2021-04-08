import uvicorn

if __name__ == '__main__':
    uvicorn.run("pom_tracker.main:app", host="127.0.0.1", port=1988, log_level="info")
