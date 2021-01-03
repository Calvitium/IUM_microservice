from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from datetime import datetime
from constants import months
import calendar
import uvicorn
import sqlite3
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory='templates')

bucket = []  # elements as a tuple of (product_id, count)
pagination_iterator = 0


@app.get("/")
@app.post("/")
def root(request: Request, message: str = "Wybierz sobie jakiś produkt do zakupienia"):
    with sqlite3.connect('db.db') as connection:
        products_db = connection.execute(
            f"SELECT id, name, price FROM products LIMIT 20 OFFSET {20 * pagination_iterator}"
        ).fetchall()

    products_dictionary = [{"id": product[0], "name": product[1], "price": product[2]} for product in products_db]

    return templates.TemplateResponse(
        "root_template.html",
        {"request": request, "message": message, "products": products_dictionary}
    )


@app.post("/add_to_cart")
async def add_to_cart(
        product_id: int = Form(default=-1),
        num_products: int = Form(default=-1),
):
    with sqlite3.connect('db.db') as connection:
        product_db = connection.execute(f"SELECT name, price FROM products WHERE id={product_id}").fetchone()

    product = {"id": product_id, "count": num_products, "name": product_db[0], "price": product_db[1]}
    index: int

    try:
        index = bucket.index(product)
    except ValueError:
        bucket.append(product)
        print(bucket)
        return RedirectResponse(url=f"/?message=Dodano do koszyka produkt {product_db[0]} w ilości {num_products}")

    bucket[index]['count'] += num_products
    print(bucket)

    return RedirectResponse(url=f"/?message=Dodano do koszyka produkt {product_db[0]} w ilości {num_products}")


@app.post("/cart/{product_id}")
def delete_from_cart(product_id: int = -1):
    try:
        to_delete = next(item for item in bucket if item['id'] == product_id)
        bucket.remove(to_delete)
    except StopIteration:
        pass

    return RedirectResponse(url="/cart")


@app.post("/cart")
@app.get("/cart")
async def cart(request: Request):
    with sqlite3.connect('db.db') as connection:
        companies_tuples = connection.execute(f"SELECT name FROM companies").fetchall()
        cities_tuples = connection.execute(f"SELECT name FROM cities").fetchall()

    companies = [company[0] for company in companies_tuples]
    cities = [city[0] for city in cities_tuples]

    return templates.TemplateResponse(
        "cart_template.html",
        {"request": request, "products": bucket, "cities": cities, "dcompanies": companies}
    )


@app.get("/summary")
def summarize(
        request: Request,
        city: str = Form(default=""),
        street: str = Form(default=""),
        dcompany: str = Form(default="DHL")
):
    company = sqlite3.connect('db.db').execute(f"SELECT id FROM companies WHERE name='{dcompany}'").fetchone()[0]
    today = datetime.today()

    records = [
        {
            'city': city,
            'street': street,
            'delivery_company': company,
            'purchase_day': today.day,
            'purchase_month': months[today.month],
            'purchase_hour': today.hour,
            'purchase_weekday': calendar.day_name[today.weekday()],
            'category': sqlite3.connect('db.db').execute(
                f"SELECT category FROM products WHERE id={item['id']}"
            ).fetchone()[0],
        } for item in bucket]

    delivery_time = max([predict_delivery_time(record) for record in records])

    bucket.clear()

    return templates.TemplateResponse(
        "confirmation_template.html",
        {"request": request, "delivery_time": delivery_time}
    )


def predict_delivery_time(record):
    print(record)
    return 24


@app.get("/prev")
def decrement_pagination():
    global pagination_iterator

    pagination_iterator -= 0 if pagination_iterator <= 0 else 1

    return RedirectResponse(url="/?message=Wybierz sobie coś do kupienia")


@app.get("/next")
def increment_pagination():
    global pagination_iterator

    pagination_iterator += 1

    return RedirectResponse(url="/?message=Wybierz sobie coś do kupienia")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
