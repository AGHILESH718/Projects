from fastapi import FastAPI,Depends,HTTPException,status,Security
from .database import Base,engine,SessionLocal
from sqlalchemy.orm import Session
from . import schema,crud,models
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,APIKeyHeader
from .auth import hash_password,verify_password,create_access_token,decode

Base.metadata.create_all(bind = engine)

app = FastAPI()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
api_key_header = APIKeyHeader(name="Authorization")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#login, register & jwt-protected routes
def get_currrent_user(token: str = Depends(api_key_header),db: Session = Depends(get_db)):
    try:
        username = decode(token)
        if username is None:
            raise HTTPException(status_code=404,detail="Invalid token")
        user = db.query(models.User).filter(models.User.Username == username).first()
        if user is None:
            raise HTTPException(status_code=404,detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal server error: {str(e)}")



#login, register & jwt-protected routes
#Register
@app.post("/new-register",response_model=schema.UserOut)
def register(user: schema.UserCreate,db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.Username == user.Username).first()
        if db_user:
            raise HTTPException(status_code=404,detail="User already exist")
        hash_pwd = hash_password(user.Password)
        new_user = models.User(Username = user.Username, Password = hash_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Iternal sever error: {str(e)}")
    
#login
@app.post("/login",response_model=schema.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.Username == form_data.username).first()
    if not user or not verify_password(form_data.password,user.Password):
        raise HTTPException(status_code=404,detail="Username or Password are wrong")
    print("USERNAME:", form_data.username)
    print("PASSWORD:", form_data.password)
    try:
        token = create_access_token({"sub": user.Username})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal server error: {str(e)}")


# get method
@app.get("/tasks",response_model=list[schema.TaskOut])
def read_tasks(current_user: models.User = Depends(get_currrent_user),db:Session =Depends(get_db)):
    try:
        return crud.get_task_by_user(db,current_user)
    except Exception as e:
        raise HTTPException(status_code=404,detail=f"Internal error: {str(e)}")

# post method
@app.post("/tasks", response_model=schema.TaskOut)
def create_task(task: schema.TaskCreate,current_user: models.User = Depends(get_currrent_user),db: Session = Depends(get_db)):
    try:
        return crud.create_tasks(db, task, current_user)   
    except Exception as e:
        print("Error while creating task",e)
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/tasks/{task_id}",response_model=schema.TaskOut)
def get_task(task_id: int, current_user: models.User = Depends(get_currrent_user), db: Session = Depends(get_db)):
    try:
        task = crud.get_task_by_id(db,task_id)
        if not task or task.owner_id != current_user.id:
            raise HTTPException(status_code=404,detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Interna; server error: {str(e)}") 
    

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int, db: Session = Depends(get_db),current_user: models.User = Depends(get_currrent_user)):
    try:
        print(f"Deleting task with ID: {task_id}")
        task = crud.delete_task(db, task_id,current_user)
        return "Deleted Successfully"
    except HTTPException as err:
        raise err
    except Exception as e:
        raise HTTPException(status_code=404,detail=f"Internal server error: {str(e)}")
   
@app.put("/tasks/{task_id}")
def update_task(task_id: int,updated_data: schema.TaskCreate,current_user: models.User = Depends(get_currrent_user),db: Session = Depends(get_db)):
     try:
         task = crud.update_task(db,task_id,updated_data,current_user)
         return {"message": "Updated Successfully","data": task}
     except Exception as e:
         raise HTTPException(status_code=404,detail=f"Internal error: {str(e)}")
     

# register     
@app.post("/register",response_model=schema.UserOut)
def register(user: schema.UserCreate,db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.Username == user.Username).first()
        if db_user:
            raise HTTPException(status_code=404,detail="Username already exist")
        hashed = hash_password(user.Password)
        new_user = models.User(Username = user.Username, Password = hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal error: {str(e)}")
    

#login
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.Username == form_data.username).first()
        if not user or not verify_password(form_data.password,user.Password):
            raise HTTPException(status_code=404,detail="Username or Password are wrong")
        token = create_access_token(data={"sub": user.Username})
        return {"access_token":token, "token type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")