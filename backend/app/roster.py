from io import BytesIO
from openpyxl import load_workbook

def parse_roster(content:bytes)->list[dict]:
    try: book=load_workbook(BytesIO(content),read_only=True,data_only=True)
    except Exception as exc: raise ValueError("Workbook could not be read") from exc
    sheet=book.active; iterator=sheet.iter_rows(values_only=True); header=next(iterator,None)
    if not header: raise ValueError("Workbook is empty")
    columns={str(v).strip().lower():i for i,v in enumerate(header) if v is not None}
    missing={"enrollment_number","full_name"}-columns.keys()
    if missing: raise ValueError("Missing required columns: "+", ".join(sorted(missing)))
    result=[]
    for n,values in enumerate(iterator,start=2):
        if not any(v is not None and str(v).strip() for v in values): continue
        def cell(key):
            i=columns.get(key)
            return values[i] if i is not None and i<len(values) else None
        result.append({"row_number":n,
          "enrollment_number":str(cell("enrollment_number")).strip() if cell("enrollment_number") is not None else None,
          "full_name":str(cell("full_name")).strip() if cell("full_name") is not None else None,
          "email":str(cell("email")).strip().lower() if cell("email") is not None else None})
    book.close(); return result

def validate_roster(rows:list[dict],existing:set[str])->list[dict]:
    seen=set(); output=[]
    for source in rows:
        row=dict(source); errors=[]; enrollment=row.get("enrollment_number")
        if not enrollment: errors.append("Enrollment number is required")
        elif enrollment in seen: errors.append("Duplicate enrollment number in workbook")
        elif enrollment in existing: errors.append("Enrollment number already exists")
        if enrollment: seen.add(enrollment)
        if not row.get("full_name"): errors.append("Full name is required")
        email=row.get("email")
        if email and ("@" not in email or email.startswith("@") or email.endswith("@")): errors.append("Email address is invalid")
        row["errors"]=errors; output.append(row)
    return output
