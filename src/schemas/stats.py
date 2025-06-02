from pydantic import BaseModel


class StatsResponse(BaseModel):
    link: str
    orig_link: str
    last_hour_clicks: int
    last_day_clicks: int
