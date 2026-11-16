from datetime import datetime, timezone
from sqlalchemy import create_engine, ForeignKey, String, Integer, Boolean, DateTime, JSON, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.core import settings

class Base(DeclarativeBase): pass
cfg=settings()
engine=create_engine(cfg.database_url,pool_pre_ping=True,
    connect_args={"check_same_thread":False} if cfg.database_url.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=False)
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(String(80),unique=True,index=True)
    email:Mapped[str|None]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
    must_change_password:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Role(Base):
    __tablename__="roles"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(30),unique=True)
class UserRole(Base):
    __tablename__="user_roles"
    __table_args__=(UniqueConstraint("user_id","role_id"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    role_id:Mapped[int]=mapped_column(ForeignKey("roles.id"))
class Department(Base):
    __tablename__="departments"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),unique=True)
class Branch(Base):
    __tablename__="branches"
    id:Mapped[int]=mapped_column(primary_key=True)
    department_id:Mapped[int]=mapped_column(ForeignKey("departments.id"))
    code:Mapped[str]=mapped_column(String(20),unique=True)
    name:Mapped[str]=mapped_column(String(120))
class AcademicYear(Base):
    __tablename__="academic_years"
    id:Mapped[int]=mapped_column(primary_key=True)
    label:Mapped[str]=mapped_column(String(20),unique=True)
    is_active:Mapped[bool]=mapped_column(Boolean,default=False)
class Semester(Base):
    __tablename__="semesters"
    __table_args__=(UniqueConstraint("academic_year_id","number"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    academic_year_id:Mapped[int]=mapped_column(ForeignKey("academic_years.id"))
    number:Mapped[int]=mapped_column(Integer)
class Section(Base):
    __tablename__="sections"
    __table_args__=(UniqueConstraint("branch_id","semester_id","name"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    branch_id:Mapped[int]=mapped_column(ForeignKey("branches.id"))
    semester_id:Mapped[int]=mapped_column(ForeignKey("semesters.id"))
    name:Mapped[str]=mapped_column(String(30))
class Subject(Base):
    __tablename__="subjects"
    id:Mapped[int]=mapped_column(primary_key=True)
    branch_id:Mapped[int]=mapped_column(ForeignKey("branches.id"))
    code:Mapped[str]=mapped_column(String(30),unique=True)
    name:Mapped[str]=mapped_column(String(150))
class Room(Base):
    __tablename__="rooms"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(80),unique=True)
    building:Mapped[str|None]=mapped_column(String(100))
class Student(Base):
    __tablename__="students"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),unique=True)
    enrollment_number:Mapped[str]=mapped_column(String(40),unique=True,index=True)
    full_name:Mapped[str]=mapped_column(String(160))
class Faculty(Base):
    __tablename__="faculty"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),unique=True)
    employee_code:Mapped[str]=mapped_column(String(40),unique=True)
    full_name:Mapped[str]=mapped_column(String(160))
class Enrollment(Base):
    __tablename__="student_enrollments"
    __table_args__=(UniqueConstraint("student_id","section_id"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    student_id:Mapped[int]=mapped_column(ForeignKey("students.id"))
    section_id:Mapped[int]=mapped_column(ForeignKey("sections.id"))
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class RefreshSession(Base):
    __tablename__="refresh_sessions"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    token_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    revoked_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    replaced_by_hash:Mapped[str|None]=mapped_column(String(64))
class RosterImport(Base):
    __tablename__="roster_imports"
    id:Mapped[int]=mapped_column(primary_key=True)
    section_id:Mapped[int]=mapped_column(ForeignKey("sections.id"))
    created_by:Mapped[int]=mapped_column(ForeignKey("users.id"))
    status:Mapped[str]=mapped_column(String(20),default="preview")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class RosterRow(Base):
    __tablename__="roster_import_rows"
    id:Mapped[int]=mapped_column(primary_key=True)
    import_id:Mapped[int]=mapped_column(ForeignKey("roster_imports.id",ondelete="CASCADE"))
    row_number:Mapped[int]=mapped_column(Integer)
    enrollment_number:Mapped[str|None]=mapped_column(String(40))
    full_name:Mapped[str|None]=mapped_column(String(160))
    email:Mapped[str|None]=mapped_column(String(255))
    errors:Mapped[list]=mapped_column(JSON,default=list)
class AuditLog(Base):
    __tablename__="audit_logs"
    id:Mapped[int]=mapped_column(primary_key=True)
    actor_user_id:Mapped[int|None]=mapped_column(ForeignKey("users.id"))
    action:Mapped[str]=mapped_column(String(100))
    entity_type:Mapped[str]=mapped_column(String(80))
    entity_id:Mapped[str|None]=mapped_column(String(80))
    details:Mapped[str|None]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
