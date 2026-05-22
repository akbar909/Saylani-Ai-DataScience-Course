
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()


# Enable CORS for all origins (for development; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory student storage
from typing import Dict

students: Dict[int, dict] = {}
student_id_counter = 1


class Student(BaseModel):
    """Pydantic model for student data."""
    name: str
    age: int


@app.get("/", tags=["Root"])
def root() -> dict:
    """Root endpoint for API health check."""
    return {"message": "Student Management API"}



@app.post("/students/add", tags=["Students"])
def add_student(student: Student) -> dict:
    """Add a new student."""
    global student_id_counter
    student_data = student.dict()
    student_id = student_id_counter
    students[student_id] = {"id": student_id, **student_data}
    student_id_counter += 1
    return {"message": f"Student {student.name} of age {student.age} added successfully.", "student_id": student_id}



@app.get("/students/{student_id}", tags=["Students"])
def get_student(student_id: int) -> dict:
    """Retrieve student details by ID."""
    student = students.get(student_id)
    if not student:
        return {"detail": "Student not found."}
    return student


from typing import Optional

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None


@app.put("/students/update/{student_id}", tags=["Students"])
def update_student(student_id: int, student: StudentUpdate) -> dict:
    """Update student details by ID."""
    if student_id not in students:
        return {"detail": "Student not found."}
    update_data = student.dict(exclude_unset=True)
    students[student_id].update(update_data)
    return {"message": f"Student {student_id} updated successfully."}



@app.delete("/students/delete/{student_id}", tags=["Students"])
def delete_student(student_id: int) -> dict:
    """Delete a student by ID."""
    if student_id not in students:
        return {"detail": "Student not found."}
    del students[student_id]
    return {"message": f"Student {student_id} deleted successfully."}


# Endpoint to list all students
@app.get("/students", tags=["Students"])
def list_students() -> dict:
    """List all students."""
    return {"students": list(students.values())}