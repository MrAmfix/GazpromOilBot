import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database.config import BOT_USERNAME, WEB_HOST
from routers import auth, admins, onboarding, events, message, analytics

app = FastAPI()


templates = Jinja2Templates(directory="web/templates")

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(onboarding.router)
app.include_router(events.router)
app.include_router(message.router)
app.include_router(analytics.router)


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

    if not user_id:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
