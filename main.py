import csv
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # ← wildcard: all origins allowed
    allow_methods=["GET"],          # ← only GET; use ["*"] to allow all methods
    allow_headers=["*"],            # ← all request headers permitted
    allow_credentials=False,        # ← set True only if you need cookies/auth
)

# Pydantic model for a student record
class Student(BaseModel):
    studentId: int
    class_: str

    class Config:
        fields = {
            'class_': 'class'
        }


# Load CSV into memory at startup
def load_students(csv_path: str) -> List[Student]:
    students: List[Student] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert studentId to int
            sid = int(row['studentId'])
            cls = row['class']
            students.append(Student(studentId=sid, class_=cls))
    return students

# In-memory store of all students
STUDENTS = load_students("q-fastapi.csv")

def func(student: Student):
    s = student.__dict__
    s["class"] = s.pop("class_")
    return s

@app.get("/api", response_model=dict)
def get_students(
    class_: List[str] = Query(
        default=[],
        alias="class",
    )
):    
    if class_:
        filtered = [s for s in STUDENTS if s.class_ in class_]
    else:
        filtered = STUDENTS
    
    filtered = map(func, filtered)

    return {"students": filtered}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
