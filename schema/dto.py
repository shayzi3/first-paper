from pydantic import BaseModel




class UserDTO(BaseModel):
     id: int
     username: str
     
     sell_items: list["MarketItemDTO"] = []
     
     
class ItemDTO(BaseModel):
     id: int
     short_name: str
     category: str
     
     market_items: list["MarketItemDTO"] = []
     

class MarketItemDTO(BaseModel):
     id: int
     item_id: int
     user_id: int
     full_name: str
     wear: str
     price: float
     
     item: ItemDTO
     user: UserDTO