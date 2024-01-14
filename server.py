import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "modules.api:app", host="0.0.0.0", port=8000, reload=True, access_log=True
    )
