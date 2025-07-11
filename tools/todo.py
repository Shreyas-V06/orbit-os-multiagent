from initializers.initialize_db import initialize_db
from initializers.initialize_llm import *
from schemas.todo import TodoBase
from bson import ObjectId
from langchain_core.tools import tool
from auth.utilities import get_user_id
from fastapi import APIRouter

todo_router=APIRouter()
db=initialize_db()


@todo_router.get('/todos/{todo_id}')
def get_todo_by_id(todo_id):

    _id=ObjectId(todo_id)
    collection=db.todos
    todo=collection.find_one({"_id":_id})
    return todo

@todo_router.post('/todos/')
def create_todo_base(todo_object:TodoBase):
    collection=db.todos
    user_id=ObjectId(get_user_id())
    todo_name=todo_object.todo_name
    todo_checkbox=todo_object.todo_checkbox
    todo_duedate=todo_object.todo_duedate

 
    if(todo_checkbox==None):
        todo_checkbox = False
    if(todo_duedate==None):
        todo_duedate= time_today()

    todo={"user_id":user_id,"todo_name":todo_name,"todo_checkbox":todo_checkbox,"todo_duedate":todo_duedate}
    collection.insert_one(todo)

@todo_router.get('/todos/')
def get_todos_base():
    user_id=ObjectId(get_user_id())
    collection=db.todos
    todo_list=collection.find({"user_id":user_id})
    return list(todo_list)

@todo_router.put('/todos/')
def update_todo_base(todo_object:TodoBase):
    collection=db.todos
    todo_id=ObjectId(todo_object.todo_id)
    user_id=ObjectId(get_user_id())
  
    todo_name=todo_object.todo_name
    todo_checkbox=todo_object.todo_checkbox
    todo_duedate=todo_object.todo_duedate

    if(todo_name==None):
        todo_name = get_todo_by_id(todo_object.todo_id)['todo_name']
    if(todo_checkbox==None):
        todo_checkbox = get_todo_by_id(todo_object.todo_id)['todo_checkbox']
    if(todo_duedate==None):
        todo_duedate= get_todo_by_id(todo_object.todo_id)['todo_duedate']


    todo={"user_id":user_id,"todo_name":todo_name,"todo_checkbox":todo_checkbox,"todo_duedate":todo_duedate}
    updates={"$set":todo}
    collection.update_one({"_id":todo_id},updates)


@todo_router.delete('/todos')
def delete_todo_base(todo_object:TodoBase):
    collection=db.todos
    todo_id=ObjectId(todo_object.todo_id)
    collection.delete_one({"_id":todo_id})

@tool
def create_todo_tool(query:str):

    """Creates a new todo task for the user. Use this tool whenever the user wants to create a task/todo
  You must include all the details:
    You must include all the following fields.
   
  todo_name: name of the todo
  todo_duedate: (if not mentioned do not include)
  todo_checkbox: (if not mentioned do not include)
  
  """

    llm=initialize_parserllm()
    llm_wso=llm.with_structured_output(TodoBase)
    todo_object = llm_wso.invoke(query)
    create_todo_base(todo_object)

    return "Created Sucessfully"

@tool
def update_todo_tool(query:str):

    """
  Updates an already existing todo task for the user. Use this tool whenever the user wants to update a task/todo.
  You must pass in the following fields:

  todo_id: unique id of the todo, it is a mandatory field which wont be provided by user
  you must fetch it by calling get_todos tool
  todo_name, todo_duedate , todo_checkbox as per changes

 Make necessary changes to the fields required and fill the unchanged fields with old details

    """

    llm=initialize_parserllm()
    llm_wso=llm.with_structured_output(TodoBase)
    todo_object = llm_wso.invoke(query)
    update_todo_base(todo_object)

    return "Updated Sucessfully"

@tool 
def get_todos_tool():

    """ this tool returns list of all the todos created,
    Use this function whenever you want to get details of the todos for
    searching for the details of a specific todo such as todo_id

    """

    all_todos=get_todos_base()
    return all_todos

@tool
def delete_todo_tool(todo_id: str):

    """
    This tool will delete the todo. 
    It accepts the todo_id of the task as the parameter.
    user will never pass todo_id so call get_todos function to get the required todo_id
    """
    llm = initialize_parserllm()
    llm_wso = llm.with_structured_output(TodoBase)
    todo_object = llm_wso.invoke(todo_id)
    delete_todo_base(todo_object)
    return "Deleted Sucessfully "


def time_today():
    """
    Returns the current date and time.
    It accepts one parameter called "query".
    This parameter is a dummy parameter, which will be ignored. 

    ALWAYS FILL IT WITH "NOW".
    This function will always return today's time and date.
    regardless of the parameter you pass.

    However whenever user asks you to use dates of "tomorrow",
    "yesterday","five days from now",etc etc.
    Use this tool, identify today's date and perform necessary calculations
    to get the date required.

    Example: required date is tomorrow
    Tool response: today's date is 2025-7-20
    Calculate tomorrow as today's date +1 , hence use 2025-7-21.

"""
    from datetime import datetime
    now = datetime.now()
    return {
        "time now": now.strftime("%H:%M:%S"),
        "today's date": now.strftime("%Y-%m-%d")
    }


