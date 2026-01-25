from dishka import FromDishka

from schema.dto import ItemDTO
from repository.uow.interface import UnitOfWorkProtocol
from repository.builder_configs.configs import (
     Filter,
     FilterConfig,
     LazyLoadConfig
)
from repository.builder_configs.types import FilterType
from dependency.provider import inject_dependency



class ItemService:
     
     @inject_dependency
     async def get_item_with_market_items(
          self,
          id: int,
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> ItemDTO | None:
          """
               Метод возвращает предмет, который имеет список продаваемых предметов соответственно.
               
               Возвращаемые данные: id = 2
               id=2 
               short_name='awp' 
               category='sniper' 
               market_items=[
                    MarketItemDTO(
                         id=2, 
                         item_id=2, 
                         user_id=1, 
                         full_name='AWP | Dragon Lore (Factory New)', 
                         wear='0.01', 
                         price=12500.0, 
                         item=None, 
                         user=None
                    ), 
                    MarketItemDTO(
                         id=12, 
                         item_id=2, 
                         user_id=10, 
                         full_name='AWP | Asiimov (Field-Tested)', 
                         wear='0.22', 
                         price=65.4, 
                         item=None, 
                         user=None
                    )
               ]
          """
          async with uow:
               item = await uow.item.read(
                    filters=[FilterConfig(filters=[Filter(column="id", value=id)])],
                    loads=[LazyLoadConfig(relationship_strategy="market_items")]
               )
               return item
     
     @inject_dependency
     async def get_items_of_categories(
          self,
          categories: list[str],
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> list[ItemDTO]:
          """
               Метод возвращает предметы определённых категорий
               
               Возвращаемые данные: categories = ["rifle", "sniper"]
               [
                    ItemDTO(
                         id=1, 
                         short_name='ak47', 
                         category='rifle', 
                         market_items=[]
                    ), 
                    ItemDTO(
                         id=2, 
                         short_name='awp', 
                         category='sniper',
                         market_items=[]
                    ), 
                    ItemDTO(
                         id=3, 
                         short_name='m4a1s', 
                         category='rifle', 
                         market_items=[]
                    ), 
                    ItemDTO(
                         id=9, 
                         short_name='ak47_redline', 
                         category='rifle', 
                         market_items=[]
                    ), 
                    ItemDTO(
                         id=10, 
                         short_name='awp_dragonlore',
                         category='sniper', 
                         market_items=[]
                    )
               ]
          """
          async with uow:
               items = await uow.item.read(
                    filters=[FilterConfig(filters=[Filter(column="category", value=categories, filter_type=FilterType.IN)])],
                    is_many=True
               )
               return items