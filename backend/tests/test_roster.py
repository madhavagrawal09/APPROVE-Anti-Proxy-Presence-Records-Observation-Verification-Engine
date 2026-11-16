from app.roster import validate_roster
def test_roster_required_fields_and_duplicate_detection():
    rows=[{"row_number":2,"enrollment_number":"A1","full_name":"One","email":None},
          {"row_number":3,"enrollment_number":"A1","full_name":"Two","email":None},
          {"row_number":4,"enrollment_number":None,"full_name":"","email":None}]
    result=validate_roster(rows,set())
    assert result[0]["errors"]==[]
    assert "Duplicate enrollment number in workbook" in result[1]["errors"]
    assert "Enrollment number is required" in result[2]["errors"]
    assert "Full name is required" in result[2]["errors"]
def test_roster_existing_enrollment_and_email_validation():
    row={"row_number":2,"enrollment_number":"OLD","full_name":"Name","email":"bad"}
    errors=validate_roster([row],{"OLD"})[0]["errors"]
    assert "Enrollment number already exists" in errors
    assert "Email address is invalid" in errors
