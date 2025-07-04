from pydantic import Field,BaseModel
from datetime import datetime
from typing import Optional

class ReminderBase(BaseModel):
    """
    The following structure is used to create or update any reminder (either existing or new), fill the respective fields
    with their values only

     For updating the reminder:
      -You must fill the reminder_id, and updated fields with the changes.
      The unchanged fields should be filled with their old values itself
      
    """
    reminder_id: Optional[str] = Field(None, description="Each reminder is identified by a unique id called reminder_id")
    reminder_name: Optional[str] = Field(None, description="name of the reminder")
    reminder_duedate: Optional[datetime] = Field(None, description="trigger date of the reminder")
