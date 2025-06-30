from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models,schema

def get_task_by_user(db: Session,user: models.User):
    return db.query(models.Task).filter(models.Task.owner_id == user.id).all()

def create_tasks(db:Session, task: schema.TaskCreate, user: models.User):
    db_task = models.Task(**task.dict(),owner_id = user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task_by_id(db:Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

# def delete_task(db:Session,task_id:int):
#     task = get_task(db,task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail={"message":"No Data Found"})
#     if task:
#         db.delete(task)
#         db.commit()
#         return True

def delete_task(db: Session, task_id: int,user: models.User):
    try:
        task = get_task_by_id(db, task_id)
        if not task or task.owner_id != user.id:
            raise HTTPException(status_code=404, detail={"message": "No Data Found"})
        db.delete(task)
        db.commit()
        return "Deleted successfully"
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{str(e)}")


def update_task(db:Session,task_id: int,updated_data: schema.TaskCreate,user: models.User):
    try:
        task = get_task_by_id(db,task_id)
        if not task or task.owner_id != user.id:
            raise HTTPException(status_code=404,detail="Task not found")
        task.title = updated_data.title
        task.description = updated_data.description
        task.completed = updated_data.completed
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        print(f"Error while updating task with id {task_id}: {e}")
        raise HTTPException(status_code=404,detail=f"Internal server error: {str(e)}")