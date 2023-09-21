from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()


# Модель для задачи (используем Pydantic)
class Task(BaseModel):
    title: str
    description: str
    status: bool


# Список задач в памяти (для примера)
tasks = []


# Получение списка всех задач
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks


# Получение задачи по идентификатору
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return tasks[task_id]


# Добавление новой задачи
@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    tasks.append(task)
    return task


# Обновление задачи по идентификатору
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task):
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    tasks[task_id] = updated_task
    return updated_task


# Удаление задачи по идентификатору
@app.delete("/tasks/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    deleted_task = tasks.pop(task_id)
    return deleted_task
