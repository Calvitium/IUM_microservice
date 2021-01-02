from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import uvicorn
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory='templates')

bucket = []  # elements as a tuple of (product_id, count)
pagination_iterator = 1


@app.get("/")
def root(request: Request, message: str = "Wybierz sobie jakiś produkt do zakupienia"):
    with sqlite3.connect('db.db') as connection:
        cursor = connection.cursor()
        products_db = cursor.execute(
            f"SELECT id, name, price FROM products LIMIT 20 OFFSET {20 * pagination_iterator}").fetchall()

    products_dictionary = [{"id": product[0], "name": product[1], "price": product[2]} for product in products_db]

    return templates.TemplateResponse("root_template.html",
                                      {"request": request, "message": message, "products": products_dictionary})


@app.post("/add_to_cart")
async def add_to_cart(
        request: Request,
        product_id: int = Form(default=-1),
        num_products: int = Form(default=-1),
        product_name: str = Form(default=-1),
        add_to_cart: str = Form(default=-1),
):
    bucket.append({"id": product_id, "count": num_products, "name": product_name, "price": add_to_cart})
    print(bucket)
    return RedirectResponse(url="/?message=Dodano do koszyka")


@app.get("/cart")
async def cart(request: Request):
    with sqlite3.connect('db.db') as connection:
        cursor = connection.cursor()
        companies_tuples = cursor.execute(f"SELECT name FROM companies").fetchall()
        cities_tuples = cursor.execute(f"SELECT name FROM cities").fetchall()

    products_dicts = [{"id": product[0], "name": product[1], "price": product[2]} for product in products_db]
    #
    # "products": {"name": string, "count": number, "price": number},
    # "cities": [string],
    # "dcompanies": [string]
    # }
    # W
    # products
    # id
    # jeszcze.
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
