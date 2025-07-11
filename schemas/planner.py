from pydantic import Field,BaseModel
from datetime import datetime
from typing import List

class ProjectBase(BaseModel):
    
    """
Model for storing or updating a 5-day project task plan.

Each day (day_one to day_five) should contain a list of tasks allocated by the planner agent.
Make sure the LLM assigns tasks to the correct day column based on the plan:

    DAY ONE   -  day_one  
    DAY TWO   -  day_two  
    DAY THREE -  day_three  
    DAY FOUR  -  day_four  
    DAY FIVE  -  day_five

Unchanged fields should retain their existing values during updates.

Example:
    Input from LLM:
        DAY ONE: Research topic, Draft outline  
        DAY TWO: Write introduction  
        DAY THREE: Expand sections  
        DAY FOUR: Review and edit  
        DAY FIVE: Final submission

    Corresponding model fields:
        day_one = ["Research topic", "Draft outline"]
        day_two = ["Write introduction"]
        day_three = ["Expand sections"]
        day_four = ["Review and edit"]
        day_five = ["Final submission"]
"""
    
    project_name: str = Field(None, description="name of the project")
    day_one: List[str] = Field(None,description="all the tasks allocated for day one")
    day_two: List[str] = Field(None,description="all the tasks allocated for day two")
    day_three: List[str] = Field(None,description="all the tasks allocated for day three")
    day_four: List[str] = Field(None,description="all the tasks allocated for day four")
    day_five: List[str] = Field(None,description="all the tasks allocated for day five")


