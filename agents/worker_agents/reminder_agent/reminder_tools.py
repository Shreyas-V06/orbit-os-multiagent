from initializers.initialize_db import initialize_db
from initializers.initialize_llm import *
from schemas.reminder_schemas import ReminderBase
from bson import ObjectId
from langchain_core.tools import tool
from auth.utilities import get_user_id
db=initialize_db()


def get_reminder_by_id(reminder_id):

    _id=ObjectId(reminder_id)
    collection=db.reminders
    reminder=collection.find_one({"_id":_id})
    return reminder


def create_reminder_base(reminder_object:ReminderBase):
    collection=db.reminders
    user_id=user_id=ObjectId(get_user_id())
    reminder_name=reminder_object.reminder_name
    reminder_duedate=reminder_object.reminder_duedate

    if(reminder_duedate==None):
        reminder_duedate= time_today()

    reminder={"user_id":user_id,"reminder_name":reminder_name,"reminder_duedate":reminder_duedate}
    collection.insert_one(reminder)

def get_reminders_base():
    user_id=ObjectId(get_user_id())
    collection=db.reminders
    reminder_list=collection.find({"user_id":user_id})
    return list(reminder_list)


def update_reminder_base(reminder_object:ReminderBase):
    collection=db.reminders
    reminder_id=ObjectId(reminder_object.reminder_id)
    user_id=ObjectId(get_user_id())
  
    reminder_name=reminder_object.reminder_name
    reminder_duedate=reminder_object.reminder_duedate

    if(reminder_name==None):
        reminder_name = get_reminder_by_id(reminder_object.reminder_id)['reminder_name']
    if(reminder_duedate==None):
        reminder_duedate= get_reminder_by_id(reminder_object.reminder_id)['reminder_duedate']


    reminder={"user_id":user_id,"reminder_name":reminder_name,"reminder_duedate":reminder_duedate}
    updates={"$set":reminder}
    collection.update_one({"_id":reminder_id},updates)


def delete_reminder_base(reminder_object:ReminderBase):
    collection=db.reminders
    reminder_id=ObjectId(reminder_object.reminder_id)
    collection.delete_one({"_id":reminder_id})

@tool
def create_reminder_tool(query:str):

    """Creates a new reminder task for the user. Use this tool whenever the user wants to create a task/reminder
  You must include all the details:
    You must include all the following fields.
   
  reminder_name: name of the reminder
  reminder_duedate: (if not mentioned do not include)
  reminder_checkbox: (if not mentioned do not include)
  
  """

    llm=initialize_parserllm()
    llm_wso=llm.with_structured_output(ReminderBase)
    reminder_object = llm_wso.invoke(query)
    create_reminder_base(reminder_object)

    return "Created Sucessfully"

@tool
def update_reminder_tool(query:str):

    """
  Updates an already existing reminder task for the user. Use this tool whenever the user wants to update a task/reminder.
  You must pass in the following fields:

  reminder_id: unique id of the reminder, it is a mandatory field which wont be provided by user
  you must fetch it by calling get_reminders tool
  reminder_name, reminder_duedate , reminder_checkbox as per changes

 Make necessary changes to the fields required and fill the unchanged fields with old details

    """

    llm=initialize_parserllm()
    llm_wso=llm.with_structured_output(ReminderBase)
    reminder_object = llm_wso.invoke(query)
    update_reminder_base(reminder_object)

    return "Updated Sucessfully"

@tool 
def get_reminders_tool():

    """ this tool returns list of all the reminders created,
    Use this function whenever you want to get details of the reminders for
    searching for the details of a specific reminder such as reminder_id

    """

    all_reminders=get_reminders_base()
    return all_reminders

@tool
def delete_reminder_tool(reminder_id: str):

    """
    This tool will delete the reminder. 
    It accepts the reminder_id of the task as the parameter.
    user will never pass reminder_id so call get_reminders function to get the required reminder_id
    """
    llm = initialize_parserllm()
    llm_wso = llm.with_structured_output(ReminderBase)
    reminder_object = llm_wso.invoke(reminder_id)
    delete_reminder_base(reminder_object)
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


