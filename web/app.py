import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth, admins, onboarding, events, message, analytics

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(onboarding.router)
app.include_router(events.router)
app.include_router(message.router)
app.include_router(analytics.router)


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username", "Пользователь")

    if not user_id:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
