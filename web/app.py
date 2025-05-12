import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database.config import BOT_USERNAME, WEB_HOST, WEB_PORT
from routers import auth, admins, onboarding, events, message, analytics, files

app = FastAPI()


templates = Jinja2Templates(directory="web/templates")

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(onboarding.router)
app.include_router(events.router)
app.include_router(message.router)
app.include_router(analytics.router)
app.include_router(files.router)


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "bot_username": BOT_USERNAME,
        "web_host": WEB_HOST
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username", "Пользователь")
    photo_url = request.cookies.get("photo_url", "")

    if not user_id:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username,
        "photo_url": photo_url
    })


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=WEB_PORT)
