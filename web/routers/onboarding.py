from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.gen_session import get_session
from database.utils.DefaultEnum import UserRole
from database.crud.user_crud import UserCrud
from database.crud.onboarding_crud import OnboardingCrud

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role not in [UserRole.ADMIN, UserRole.HADMIN]:
        return RedirectResponse(url="/")

    status = request.query_params.get("status")

    onboardings = await OnboardingCrud.get_all(session)
    return templates.TemplateResponse("onboarding.html", {
        "request": request,
        "onboardings": onboardings,
        "status": status
    })


@router.post("/onboarding/set")
async def create_onboarding(
    request: Request,
    name: str = Form(...),
    start_message_unauthorized: str = Form(...),
    start_message_authorized: str = Form(...),
    phone_request: str = Form(...),
    invalid_phone: str = Form(...),
    fullname_request: str = Form(...),
    invalid_fullname: str = Form(...),
    email_request: str = Form(...),
    invalid_email: str = Form(...),
    speciality_request: str = Form(...),
    invalid_speciality: str = Form(...),
    success_registration: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    if await OnboardingCrud.get_filtered_by_params(session=session, name=name):
        return RedirectResponse(url="/onboarding?status=exists", status_code=303)

    await OnboardingCrud.create(
        name=name,
        session=session,
        start_message_unauthorized=start_message_unauthorized,
        start_message_authorized=start_message_authorized,
        phone_request=phone_request,
        invalid_phone=invalid_phone,
        fullname_request=fullname_request,
        invalid_fullname=invalid_fullname,
        email_request=email_request,
        invalid_email=invalid_email,
        speciality_request=speciality_request,
        invalid_speciality=invalid_speciality,
        success_registration=success_registration
    )
    return RedirectResponse(url="/onboarding?status=created", status_code=303)


@router.post("/onboarding/activate")
async def activate_onboarding(request: Request, onboarding_id: str = Form(...), session: AsyncSession = Depends(get_session)):
    await OnboardingCrud.update(session=session, record_id=onboarding_id, is_active=True)
    return RedirectResponse(url="/onboarding?status=activated", status_code=303)


@router.post("/onboarding/delete")
async def delete_onboarding(request: Request, onboarding_id: str = Form(...), session: AsyncSession = Depends(get_session)):
    await OnboardingCrud.delete(session=session, record_id=onboarding_id)
    return RedirectResponse(url="/onboarding?status=deleted", status_code=303)
