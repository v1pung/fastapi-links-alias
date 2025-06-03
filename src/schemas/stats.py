from pydantic import BaseModel, ConfigDict


class StatsResponse(BaseModel):
    link: str
    orig_link: str
    last_hour_clicks: int
    last_day_clicks: int

    model_config = ConfigDict(from_attributes=True)