from initializers.initialize_db import initialize_db
from initializers.initialize_llm import *
from schemas.todo_schemas import TodoBase
from bson import ObjectId
from langchain_core.tools import tool
db=initialize_db()


def get_todo_by_id(todo_id):

    _id=ObjectId(todo_id)
    collection=db.todos
    todo=collection.find_one({"_id":_id})
    return todo


def create_todo_base(todo_object:TodoBase):
    collection=db.todos
    user_id=user_id=ObjectId('68600e91dbfd7b77a1e5cc97')
    todo_name=todo_object.todo_name
    todo_checkbox=todo_object.todo_checkbox
    todo_duedate=todo_object.todo_duedate

 
    if(todo_checkbox==None):
        todo_checkbox = False
    if(todo_duedate==None):
        todo_duedate= time_today()

    todo={"user_id":user_id,"todo_name":todo_name,"todo_checkbox":todo_checkbox,"todo_duedate":todo_duedate}
    collection.insert_one(todo)

def get_todos_base():
    user_id=ObjectId('68600e91dbfd7b77a1e5cc97')
    collection=db.todos
    todo_list=collection.find({"user_id":user_id})
    return list(todo_list)


def update_todo_base(todo_object:TodoBase):
    collection=db.todos
    todo_id=ObjectId(todo_object.todo_id)
    user_id=ObjectId('68600e91dbfd7b77a1e5cc97')
  
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


@tool
def time_today():
    """
    Returns the current date and time.
"""
    from datetime import datetime
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d")
    }


