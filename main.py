from typing import Dict
from fastapi import FastAPI, status, Response, Request
from fastapi.encoders import jsonable_encoder
import sqlalchemy

app = FastAPI(debug=True)
engine = sqlalchemy.create_engine(
    "sqlite:///./test.db", echo=True, connect_args={"check_same_thread": False}
)
connection = engine.connect()

metadata = sqlalchemy.MetaData()


task_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("task_description", sqlalchemy.String),
)

metadata.create_all(engine)


def insert_tasks(task_description: str) -> None:
    query = task_table.insert().values(task_description=task_description)
    connection.execute(query)


def show_tasks() -> Dict[int, Dict[str, str | int]]:
    query = task_table.select()
    result = connection.execute(query).fetchall()
    return {
        idx: {"Id": record[0], "Description": record[1]}
        for idx, record in enumerate(result)
    }


@app.get("/")
def health(response: Response):
    response.status_code = status.HTTP_200_OK
    return jsonable_encoder({"Route Working": response.status_code})


@app.post("/tasks")
async def add_tasks(request: Request, response: Response):
    form_data = await request.form()
    task_description = form_data.get("task_description")
    insert_tasks(task_description=task_description)
    response.status_code = status.HTTP_201_CREATED
    return jsonable_encoder({"Task Created!": response.status_code})


@app.get("/tasks")
def tasks(response: Response):
    response.status_code = status.HTTP_200_OK
    return jsonable_encoder(show_tasks())
