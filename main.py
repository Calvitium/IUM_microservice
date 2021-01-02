from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')

products = [{"name": "God of War", "count": 2, "price": 29.99, "id": 1}, \
                {"name": "Celeste", "count": 3, "price": 9.99, "id": 2}]
cities = ["Warszawa", "Szczecin", "Gdańsk", "Poznań", "Nowa Sól"]
dcompanies = ["DHL","UPS","Fedex"]


@app.get("/")
def root(request: Request):

    return templates.TemplateResponse("cart_template.html",
                                      {"request": request, "message": "Hell world!", "products": products,
                                       "cities": cities,"dcompanies":dcompanies})


@app.post("/add_to_cart")
def add_to_cart(request: Request):
    id = request.forms.get("id")
    print(id)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
