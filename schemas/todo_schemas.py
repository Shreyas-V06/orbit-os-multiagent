from pydantic import Field,BaseModel
from datetime import datetime
from typing import Optional

class TodoBase(BaseModel):
    """
    The following structure is used to create or update any new task, fill the respective fields
    with their values only

     For updating the todos:
      -You must fill the todo_id, and updated fields with the changes.
      The unchanged fields should be filled with their old values itself
      
    """
    todo_id: Optional[str] = Field(None, description="Each todo task is identified by a unique id called todo_id")
    todo_name: Optional[str] = Field(None, description="name of the todo task")
    todo_checkbox: Optional[bool] = Field(None, description="status of the todo task, True -> done, False -> Pending")
    todo_duedate: Optional[datetime] = Field(None, description="due date of the todo")




