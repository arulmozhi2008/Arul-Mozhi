import json
from pathlib import Path
from fastapi import APIRouter,Depends,Form,HTTPException,Request,status
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config import settings
from app.crud import create_user,get_all_users,get_user,update_user_plan
from app.database import get_db
from app.schemas import FeedbackRequest,UserInput,WorkoutPlan
from app.services.gemini_service import GeminiServiceError,generate_nutrition_tip_with_flash,generate_workout_gemini,update_workout_plan

router=APIRouter()
templates=Jinja2Templates(directory=Path(__file__).resolve().parent/"templates")
def page(request,template,**ctx): return templates.TemplateResponse(request=request,name=template,context=ctx)

@router.get("/",response_class=HTMLResponse)
def home(request:Request): return page(request,"index.html")

@router.post("/generate-workout")
async def generate_workout(request: Request, db: Session = Depends(get_db)):
    try:
        print("step1")
        data = await request.json()
        print("DATA:", data)
        u = UserInput(
            user_id=str(data.get('user_id') or '01').zfill(2),
            name=str(data.get('name') or 'Test'),
            age=int(data.get('age') or 22),
            weight_kg=float(data.get('weight_kg') or 70),
            height_cm=float(data.get('height_cm') or 170),
            goal=str(data.get('goal') or 'Weight loss'),
            intensity=str(data.get('intensity') or 'Low'),
            experience=str(data.get('experience') or 'Beginner')
        )
    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}
    try:
        plan = generate_workout_gemini(u);
        tip = generate_nutrition_tip_with_flash(u)
        saved = u
        return page(
            request,
            "result.html",
            user=saved,
            workout_plan=plan,
            nutrition_tip=tip,
            message=None)
    except GeminiServiceError as e: 
        print("GEMINI ERROR:", e) 
        return page(request,"index.html",error=str(e))
    except Exception as e:
         print("GENERAL ERROR:", e)
         return page(request,"index.html",error=f"Unexpected server error: {e}")

@router.post("/submit-feedback",response_class=HTMLResponse)
def submit_feedback(request:Request,user_id:str=Form(...),feedback:str=Form(...),db:Session=Depends(get_db)):
    try: data=FeedbackRequest(user_id=user_id,feedback_type=feedback, comment=comment)
    except ValidationError: raise HTTPException(422,"Feedback is invalid.")
    user=get_user(db,data.user_id)
    if not user: 
        from app.models import User
        user = User(user_id=data.user_id,name="Demo User",age=25,weight_kg=70,goal="general",intensity="medium",experience="beginner")
        db.add(user)
        db.commit()
        db.refresh(user)
    try:
        profile=UserInput(user_id=user.user_id,name=user.name,age=user.age,weight_kg=user.weight_kg,goal=user.goal,intensity=user.intensity,experience=user.experience)
        original=WorkoutPlan.model_validate_json(user.original_plan)
        revised=update_workout_plan(profile,original,data.feedback)
        update_user_plan(db,user,revised.plan.model_dump_json(),data.feedback)
        return page(request,"result.html",user=user,workout_plan=revised.plan,nutrition_tip=json.loads(user.nutrition_tip),message=revised.change_summary)
    except GeminiServiceError as e:
        return page(request,"result.html",user=user,workout_plan=WorkoutPlan.model_validate_json(user.updated_plan or user.original_plan),nutrition_tip=json.loads(user.nutrition_tip),message=str(e))
    except Exception as e:
        return page(request,"result.html",user=user,workout_plan=WorkoutPlan.model_validate_json(user.updated_plan or user.original_plan),nutrition_tip=json.loads(user.nutrition_tip),message=f"Could not update plan: {e}")

@router.get("/api/users/{user_id}")
def api_user(user_id:str,db:Session=Depends(get_db)):
    u=get_user(db,user_id)
    if not u: raise HTTPException(404,"User not found.")
    return {"user_id":u.user_id,"name":u.name,"age":u.age,"weight_kg":u.weight_kg,"goal":u.goal,
            "intensity":u.intensity,"experience":u.experience,"original_plan":json.loads(u.original_plan),
            "updated_plan":json.loads(u.updated_plan) if u.updated_plan else None,
            "nutrition_tip":json.loads(u.nutrition_tip),"last_feedback":u.last_feedback}

@router.get("/admin/login",response_class=HTMLResponse)
def admin_login(request:Request): return page(request,"admin_login.html")
@router.post("/admin/login")
def admin_login_post(request:Request,token:str=Form(...)):
    if token!=settings.admin_token: return page(request,"admin_login.html",error="Invalid admin token.")
    request.session["admin_authenticated"]=True
    return RedirectResponse("/view-all-users",status_code=status.HTTP_303_SEE_OTHER)
@router.post("/admin/logout")
def admin_logout(request:Request):
    request.session.clear(); return RedirectResponse("/",status_code=303)
@router.get("/view-all-users",response_class=HTMLResponse)
def view_all_users(request:Request,db:Session=Depends(get_db)):
    if not request.session.get("admin_authenticated"): return RedirectResponse("/admin/login",status_code=303)
    return page(request,"all_users.html",users=get_all_users(db))
