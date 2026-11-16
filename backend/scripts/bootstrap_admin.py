import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core import settings,hash_password
from app.db import SessionLocal,User,Role,UserRole
def main():
    cfg=settings()
    if not cfg.bootstrap_admin_email or not cfg.bootstrap_admin_password: raise SystemExit("Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD.")
    if len(cfg.bootstrap_admin_password)<16: raise SystemExit("Bootstrap password must be at least 16 characters.")
    db=SessionLocal()
    try:
        if db.query(UserRole).join(Role).filter(Role.name=="admin").first(): raise SystemExit("Administrator already exists.")
        email=cfg.bootstrap_admin_email.strip().lower()
        if db.query(User).filter((User.email==email)|(User.username==email)).first(): raise SystemExit("Account already exists.")
        role=db.query(Role).filter_by(name="admin").first()
        if not role: raise SystemExit("Run seed_roles.py first.")
        user=User(username=email,email=email,password_hash=hash_password(cfg.bootstrap_admin_password),must_change_password=True)
        db.add(user); db.flush(); db.add(UserRole(user_id=user.id,role_id=role.id)); db.commit()
        print(f"Created administrator {email}; change password after first login.")
    finally: db.close()
if __name__=="__main__": main()
