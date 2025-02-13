from fastapi import FastAPI
from app.controller.image_controller import router as image_router
from app.controller.text_controller import router as text_router

app = FastAPI(title="FastAPI OpenAI App")

# Include the routes
app.include_router(image_router)
app.include_router(text_router)

@app.get("/")
async def root():
    return {"message": "FastAPI OpenAI API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)