from datetime import datetime,timedelta,timezone
import secrets
import jwt
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from app.core import settings,hash_password,verify_password,new_refresh_token,hash_token,access_token,decode_access
from app.db import *
from app.roster import parse_roster,validate_roster

cfg=settings(); app=FastAPI(title=cfg.app_name,version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=cfg.allowed_origins,allow_credentials=True,
    allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["Authorization","Content-Type"])
bearer=HTTPBearer(auto_error=False)
def roles(db,user_id): return [r[0] for r in db.query(Role.name).join(UserRole).filter(UserRole.user_id==user_id).all()]
def current_user(auth:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not auth: raise HTTPException(401,"Authentication required")
    try: uid=int(decode_access(auth.credentials)["sub"])
    except (jwt.PyJWTError,ValueError,KeyError): raise HTTPException(401,"Invalid or expired access token")
    user=db.get(User,uid)
    if not user or not user.is_active: raise HTTPException(401,"Account unavailable")
    return user
def admin(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if "admin" not in roles(db,user.id): raise HTTPException(403,"Administrator role required")
    return user
def tokens(db,user):
    refresh=new_refresh_token(); db.add(RefreshSession(user_id=user.id,token_hash=hash_token(refresh),
        expires_at=datetime.now(timezone.utc)+timedelta(days=cfg.refresh_token_days)))
    access=access_token(user.id,roles(db,user.id),user.must_change_password); db.commit()
    return {"access_token":access,"refresh_token":refresh,"token_type":"bearer",
        "expires_in":cfg.access_token_minutes*60,"must_change_password":user.must_change_password}
class Login(BaseModel):
    username:str=Field(min_length=1,max_length=80); password:str=Field(min_length=1,max_length=256)
class Refresh(BaseModel): refresh_token:str
class PasswordChange(BaseModel):
    current_password:str; new_password:str=Field(min_length=12,max_length=128)
@app.get("/health")
def health(): return {"status":"ok","service":"approve-api"}
@app.post(cfg.api_v1_prefix+"/auth/login")
def login(data:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter_by(username=data.username).first()
    if not user or not user.is_active or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid username or password")
    return tokens(db,user)
@app.post(cfg.api_v1_prefix+"/auth/refresh")
def refresh(data:Refresh,db:Session=Depends(get_db)):
    old=hash_token(data.refresh_token); session=db.query(RefreshSession).filter_by(token_hash=old).with_for_update().first()
    now=datetime.now(timezone.utc)
    if not session or session.revoked_at or session.expires_at.replace(tzinfo=timezone.utc)<=now:
        if session and session.revoked_at:
            db.query(RefreshSession).filter_by(user_id=session.user_id).update({"revoked_at":now}); db.commit()
        raise HTTPException(401,"Refresh token invalid or expired")
    user=db.get(User,session.user_id)
    if not user or not user.is_active: raise HTTPException(401,"Account unavailable")
    new=new_refresh_token(); new_hash=hash_token(new); session.revoked_at=now; session.replaced_by_hash=new_hash
    db.add(RefreshSession(user_id=user.id,token_hash=new_hash,expires_at=now+timedelta(days=cfg.refresh_token_days)))
    access=access_token(user.id,roles(db,user.id),user.must_change_password); db.commit()
    return {"access_token":access,"refresh_token":new,"token_type":"bearer","expires_in":cfg.access_token_minutes*60,"must_change_password":user.must_change_password}
@app.post(cfg.api_v1_prefix+"/auth/logout")
def logout(data:Refresh,db:Session=Depends(get_db),user:User=Depends(current_user)):
    item=db.query(RefreshSession).filter_by(user_id=user.id,token_hash=hash_token(data.refresh_token)).first()
    if item and not item.revoked_at: item.revoked_at=datetime.now(timezone.utc); db.commit()
    return {"message":"Logged out"}
@app.get(cfg.api_v1_prefix+"/auth/me")
def me(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return {"id":user.id,"username":user.username,"email":user.email,"roles":roles(db,user.id),"must_change_password":user.must_change_password}
@app.post(cfg.api_v1_prefix+"/auth/change-password")
def change_password(data:PasswordChange,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not verify_password(data.current_password,user.password_hash): raise HTTPException(400,"Current password is incorrect")
    if data.current_password==data.new_password: raise HTTPException(400,"New password must differ")
    user.password_hash=hash_password(data.new_password); user.must_change_password=False
    db.query(RefreshSession).filter(RefreshSession.user_id==user.id,RefreshSession.revoked_at.is_(None)).update({"revoked_at":datetime.now(timezone.utc)})
    db.commit(); return {"message":"Password changed; sign in again"}
@app.post(cfg.api_v1_prefix+"/departments")
def department(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    name=str(data.get("name","")).strip()
    if len(name)<2 or len(name)>120: raise HTTPException(422,"Department name must contain 2–120 characters")
    obj=Department(name=name); db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"name":obj.name}
@app.post(cfg.api_v1_prefix+"/branches")
def branch(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    dep=db.get(Department,data.get("department_id"))
    if not dep: raise HTTPException(404,"Department not found")
    obj=Branch(department_id=dep.id,code=str(data.get("code","")).strip(),name=str(data.get("name","")).strip())
    if not obj.code or not obj.name: raise HTTPException(422,"Branch code and name are required")
    db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"code":obj.code,"name":obj.name}
@app.post(cfg.api_v1_prefix+"/academic-years")
def academic_year(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    if data.get("is_active"): db.query(AcademicYear).update({"is_active":False})
    obj=AcademicYear(label=str(data.get("label","")).strip(),is_active=bool(data.get("is_active",False)))
    db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"label":obj.label}
@app.post(cfg.api_v1_prefix+"/semesters")
def semester(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    if not db.get(AcademicYear,data.get("academic_year_id")): raise HTTPException(404,"Academic year not found")
    obj=Semester(academic_year_id=data["academic_year_id"],number=int(data["number"]))
    if not 1<=obj.number<=12: raise HTTPException(422,"Semester number must be 1–12")
    db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"number":obj.number}
@app.post(cfg.api_v1_prefix+"/sections")
def section(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    if not db.get(Branch,data.get("branch_id")) or not db.get(Semester,data.get("semester_id")): raise HTTPException(404,"Branch or semester not found")
    obj=Section(branch_id=data["branch_id"],semester_id=data["semester_id"],name=str(data.get("name","")).strip())
    db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"name":obj.name}
@app.post(cfg.api_v1_prefix+"/subjects")
def subject(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    if not db.get(Branch,data.get("branch_id")): raise HTTPException(404,"Branch not found")
    obj=Subject(branch_id=data["branch_id"],code=data["code"],name=data["name"]); db.add(obj); db.commit(); db.refresh(obj)
    return {"id":obj.id,"code":obj.code,"name":obj.name}
@app.post(cfg.api_v1_prefix+"/rooms")
def room(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    obj=Room(name=data["name"],building=data.get("building")); db.add(obj); db.commit(); db.refresh(obj); return {"id":obj.id,"name":obj.name}
@app.post(cfg.api_v1_prefix+"/admin/faculty")
def faculty(data:dict,db:Session=Depends(get_db),actor:User=Depends(admin)):
    username=str(data.get("username","")).strip(); code=str(data.get("employee_code","")).strip(); name=str(data.get("full_name","")).strip()
    if not username or not code or not name: raise HTTPException(422,"username, employee_code and full_name are required")
    if db.query(User).filter_by(username=username).first() or db.query(Faculty).filter_by(employee_code=code).first(): raise HTTPException(409,"Username or employee code already exists")
    role=db.query(Role).filter_by(name="faculty").first()
    if not role: raise HTTPException(500,"Run seed_roles.py first")
    temp=secrets.token_urlsafe(16); user=User(username=username,email=data.get("email"),password_hash=hash_password(temp),must_change_password=True)
    db.add(user); db.flush(); db.add(UserRole(user_id=user.id,role_id=role.id)); db.add(Faculty(user_id=user.id,employee_code=code,full_name=name))
    db.add(AuditLog(actor_user_id=actor.id,action="faculty.provision",entity_type="faculty",details=f"employee_code={code}"))
    db.commit(); return {"user_id":user.id,"username":username,"temporary_password":temp,"must_change_password":True}
@app.post(cfg.api_v1_prefix+"/admin/roster-imports/preview")
async def roster_preview(section_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),actor:User=Depends(admin)):
    if not db.get(Section,section_id): raise HTTPException(404,"Section not found")
    if not file.filename or not file.filename.lower().endswith((".xlsx",".xlsm")): raise HTTPException(415,"Upload an .xlsx or .xlsm workbook")
    content=await file.read(5_000_001)
    if len(content)>5_000_000: raise HTTPException(413,"Workbook exceeds 5 MB")
    try: parsed=parse_roster(content)
    except ValueError as exc: raise HTTPException(422,str(exc))
    existing={x[0] for x in db.query(Student.enrollment_number).all()}; checked=validate_roster(parsed,existing)
    batch=RosterImport(section_id=section_id,created_by=actor.id,status="preview"); db.add(batch); db.flush(); errors=[]
    for row in checked:
        db.add(RosterRow(import_id=batch.id,row_number=row["row_number"],enrollment_number=row["enrollment_number"],full_name=row["full_name"],email=row["email"],errors=row["errors"]))
        if row["errors"]: errors.append({"row":row["row_number"],"errors":row["errors"]})
    db.add(AuditLog(actor_user_id=actor.id,action="roster.preview",entity_type="roster_import",entity_id=str(batch.id),details=f"rows={len(checked)}"))
    db.commit(); valid=sum(not x["errors"] for x in checked)
    return {"import_id":batch.id,"total_rows":len(checked),"valid_rows":valid,"invalid_rows":len(checked)-valid,"errors":errors}
@app.get(cfg.api_v1_prefix+"/admin/roster-imports/{import_id}")
def roster_detail(import_id:int,db:Session=Depends(get_db),actor:User=Depends(admin)):
    batch=db.get(RosterImport,import_id)
    if not batch: raise HTTPException(404,"Import not found")
    rows=db.query(RosterRow).filter_by(import_id=import_id).order_by(RosterRow.row_number).all()
    return {"import_id":batch.id,"status":batch.status,"rows":[{"row":r.row_number,"enrollment_number":r.enrollment_number,"full_name":r.full_name,"email":r.email,"errors":r.errors} for r in rows]}
@app.post(cfg.api_v1_prefix+"/admin/roster-imports/{import_id}/confirm")
def confirm_roster(import_id:int,db:Session=Depends(get_db),actor:User=Depends(admin)):
    batch=db.query(RosterImport).filter_by(id=import_id).with_for_update().first()
    if not batch or batch.status!="preview": raise HTTPException(404,"Pending preview import not found")
    rows=db.query(RosterRow).filter_by(import_id=import_id).order_by(RosterRow.row_number).with_for_update().all()
    if not rows or any(r.errors for r in rows): raise HTTPException(409,"Import is empty or contains validation errors")
    if any(db.query(Student).filter_by(enrollment_number=r.enrollment_number).first() for r in rows): raise HTTPException(409,"Enrollment conflict after preview; create a new preview")
    role=db.query(Role).filter_by(name="student").first()
    if not role: raise HTTPException(500,"Run seed_roles.py first")
    credentials=[]
    try:
        for row in rows:
            temp=secrets.token_urlsafe(16); user=User(username=row.enrollment_number,email=row.email,password_hash=hash_password(temp),must_change_password=True)
            db.add(user); db.flush(); db.add(UserRole(user_id=user.id,role_id=role.id))
            student=Student(user_id=user.id,enrollment_number=row.enrollment_number,full_name=row.full_name); db.add(student); db.flush()
            db.add(Enrollment(student_id=student.id,section_id=batch.section_id)); credentials.append({"username":row.enrollment_number,"temporary_password":temp})
        batch.status="confirmed"; db.add(AuditLog(actor_user_id=actor.id,action="roster.confirm",entity_type="roster_import",entity_id=str(import_id),details=f"created_students={len(credentials)}")); db.commit()
    except Exception: db.rollback(); raise
    return {"import_id":import_id,"created_students":len(credentials),"credentials":credentials}
