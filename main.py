from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "root_template.html",
        {"request": request, "message": "Hello world!"}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
