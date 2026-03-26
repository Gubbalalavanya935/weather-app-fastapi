from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import os

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# 🔐 Get API key from environment (Render)
API_KEY = os.getenv("API_KEY")


# Home Page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={"weather": None}
    )


# 🔍 Search Weather (7-day forecast)
@app.post("/", response_class=HTMLResponse)
def get_weather(request: Request, city: str = Form(...)):
    try:
        if not API_KEY:
            return templates.TemplateResponse(
                request,
                "index.html",
                context={"weather": {"error": "API key not configured on server"}}
            )

        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
        response = requests.get(url)
        data = response.json()

        # ❌ API error handling
        if "error" in data:
            return templates.TemplateResponse(
                request,
                "index.html",
                context={"weather": {"error": data["error"]["message"]}}
            )

        current = data["current"]

        forecast = []
        for day in data["forecast"]["forecastday"]:
            forecast.append({
                "date": day["date"],
                "temp": day["day"]["avgtemp_c"],
                "condition": day["day"]["condition"]["text"],
                "icon": day["day"]["condition"]["icon"]
            })

        weather = {
            "city": data["location"]["name"],
            "temp": current["temp_c"],
            "humidity": current["humidity"],
            "desc": current["condition"]["text"],
            "icon": current["condition"]["icon"],
            "forecast": forecast
        }

        return templates.TemplateResponse(
            request,
            "index.html",
            context={"weather": weather}
        )

    except Exception as e:
        print("ERROR:", e)
        return templates.TemplateResponse(
            request,
            "index.html",
            context={"weather": {"error": "Something went wrong"}}
        )


# 📍 Location Weather
@app.get("/location", response_class=HTMLResponse)
def location(request: Request, lat: float, lon: float):
    try:
        if not API_KEY:
            return templates.TemplateResponse(
                request,
                "index.html",
                context={"weather": {"error": "API key not configured"}}
            )

        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7"
        data = requests.get(url).json()

        current = data["current"]

        forecast = []
        for day in data["forecast"]["forecastday"]:
            forecast.append({
                "date": day["date"],
                "temp": day["day"]["avgtemp_c"],
                "condition": day["day"]["condition"]["text"],
                "icon": day["day"]["condition"]["icon"]
            })

        weather = {
            "city": data["location"]["name"],
            "temp": current["temp_c"],
            "humidity": current["humidity"],
            "desc": current["condition"]["text"],
            "icon": current["condition"]["icon"],
            "forecast": forecast
        }

        return templates.TemplateResponse(
            request,
            "index.html",
            context={"weather": weather}
        )

    except Exception as e:
        print("ERROR:", e)
        return templates.TemplateResponse(
            request,
            "index.html",
            context={"weather": {"error": "Location fetch failed"}}
        )