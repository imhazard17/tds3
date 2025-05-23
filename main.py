import csv
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    studentId: int
    class_: str = Field(alias="class")

    class Config:
        populate_by_name = True
        json_schema_extra = {"students": [{"class": "example_class", "studentId": "example_studentId"}]}


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

STUDENTS = load_students("q-fastapi.csv")

@app.get("/api", response_model=dict)
def get_students(class_: Optional[List[str]] = Query(None, alias="class")):
    if class_:
        filtered = [s for s in STUDENTS if s.class_ in class_]
    else:
        filtered = STUDENTS

    return {"students": [
        student.model_dump(by_alias=True)
        for student in filtered
    ]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
