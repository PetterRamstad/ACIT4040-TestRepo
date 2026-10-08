from pydantic import BaseModel, Field


class RoomCreate(BaseModel): width:float=Field(gt=0); depth:float=Field(gt=0)
