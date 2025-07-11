from pydantic import BaseModel,Field
from typing import Literal

class ResponseModel(BaseModel):
    transfer: Literal["todo agent", "document agent","reminder agent","search agent","validator"] = Field(
        description="""
        Determines the appropriate specialist agent to delegate the next step in the workflow.: 

        1.todo agent: when CRUD operations are to be performed on todos 
        2.reminder agent: when CRUD operations are to be performed on reminders
        3.document agent: when questions regarding the uploaded file has to be answered
        4.search agent: when additional information is needed to be searched on the internet
        5.validator: when the question asked is a general question about identity of OrbitOS or any meta data , 
        which requires routing to the supervisor itself , then route it to validator and include your answer ad the 
        justification of routing decision        
        """
    )
    
    order : str =Field(
        description="A clear, specific and context rich instruction for the next specialist agent, explaining what they need to do and what result is expected."
    )

    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )


