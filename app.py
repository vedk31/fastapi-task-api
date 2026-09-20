from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal, Base
from models import TaskModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str
    done: bool = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, Ved"}

@app.post("/tasks")
def create_task(task: Task, db: Session = Depends(get_db)):
    db_task = TaskModel(title=task.title, done=task.done)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        return {"error": "Task not found"}
    db_task.title = task.title
    db_task.done = task.done
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        return {"error": "Task not found"}
    db.delete(db_task)
    db.commit()
    return {"deleted": task_id}