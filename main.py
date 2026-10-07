import base64
import os
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import stripe

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Voeg hier je Stripe Secret Key toe (test-key of live-key)
# Je kunt gratis een account aanmaken op stripe.com
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_jouw_stripe_key_hier")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
  return templates.TemplateResponse(request, "index.html")


@app.post("/generate-store")
async def generate_store(file: UploadFile = File(...)):
  image_bytes = await file.read()
  image_b64 = base64.b64encode(image_bytes).decode("utf-8")
  filename = file.filename

  return {
      "status": "success",
      "product_name": f"Exclusief Item ({filename.split('.')[0]})",
      "price_amount": 4999,  # Bedrag in centen (€ 49,99)
      "price_display": "€ 49,99",
      "old_price": "€ 89,99",
      "description": (
          "Dit unieke product is direct omgetoverd tot een professionele"
          " webshop pagina. Bestel direct en ervaar de snelle levering!"
      ),
      "image": f"data:image/jpeg;base64,{image_b64}",
  }


@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
  data = await request.json()
  product_name = data.get("product_name", "Webshop Product")
  amount = data.get("amount", 4999)

  try:
    # Maak een beveiligde Stripe betaalpagina aan
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": product_name,
                },
                "unit_amount": amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://127.0.0.1:8000/?success=true",
        cancel_url="http://127.0.0.1:8000/?canceled=true",
    )
    return {"url": checkout_session.url}
  except Exception as e:
    return JSONResponse(
        status_code=400,
        content={
            "error": (
                "Betaling kon niet worden gestart. Controleer je Stripe API"
                f" Key. Fout: {str(e)}"
            )
        },
    )