from pydantic import BaseModel

class TableRow(BaseModel):
    description: str
    quantity: int
    price: float

class HtmlContent(BaseModel):
    html: str