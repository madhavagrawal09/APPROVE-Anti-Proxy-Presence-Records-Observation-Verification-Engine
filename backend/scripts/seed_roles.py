import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.db import SessionLocal,Role
def main():
    db=SessionLocal()
    try:
        for name in ("admin","faculty","student"):
            if not db.query(Role).filter_by(name=name).first(): db.add(Role(name=name))
        db.commit()
    finally: db.close()
if __name__=="__main__": main()
