from dishka import FromDishka

from dependency.provider import inject_dependency
from schema.dto import MarketItemDTO
from repository.builder_configs.types import OrderByType, FilterType, FilterLogicType
from repository.uow.interface import UnitOfWorkProtocol
from repository.builder_configs.configs import (
     Filter,
     FilterConfig,
     OrderByConfig,
     LazyLoadConfig,
     JoinConfig
)


class MarketItemService:
     
     @inject_dependency
     async def paginate_market_items(
          self,
          uow: FromDishka[UnitOfWorkProtocol],
          categories: list[str] = [],
          full_name: str | None = None,
          wears: list[str] = [],
          price: float | None = None,
          price_filter_type: FilterType | None = None,
          price_order_by: OrderByType | None = None,
     ) -> list[MarketItemDTO]:
          """
               Метод возвращает все продаваемые предметы по определённым фильтрам вместе с продавцами
               
               Возвращаемые данные: 
                    categories=["rifle", "pistol"],
                    price=150,
                    price_filter_type=FilterType.LE,
                    price_order_by=OrderByType.DESC
                    
               [
                    MarketItemDTO(
                         id=16, 
                         item_id=1, 
                         user_id=2, 
                         full_name='AK-47 | Redline (Field-Tested)', 
                         wear='0.21', price=130.0, 
                         item=None, 
                         user=UserDTO(
                              id=2, 
                              username='csgo_queen', 
                              sell_items=[]
                         )
                    ), 
                    MarketItemDTO(
                         id=11, 
                         item_id=1, 
                         user_id=9, 
                         full_name='AK-47 | Redline (Well-Worn)', 
                         wear='0.38', 
                         price=120.75, 
                         item=None, 
                         user=UserDTO(
                              id=9, 
                              username='premium_trader', 
                              sell_items=[]
                         )
                    ), 
                    MarketItemDTO(
                         id=13, 
                         item_id=3, 
                         user_id=3, 
                         full_name='M4A1-S | Cyrex (Factory New)', 
                         wear='0.03', 
                         price=110.25, 
                         item=None, 
                         user=UserDTO(
                              id=3, 
                              username='skin_master', 
                              sell_items=[]
                         )
                    ), 
                    MarketItemDTO(
                         id=3, 
                         item_id=3, 
                         user_id=2, 
                         full_name='M4A1-S | Hyper Beast (Minimal Wear)', 
                         wear='0.07', 
                         price=89.99, 
                         item=None, 
                         user=UserDTO(
                              id=2, 
                              username='csgo_queen', 
                              sell_items=[]
                         )
                    ), 
                    MarketItemDTO(
                         id=8, 
                         item_id=8, 
                         user_id=6, 
                         full_name='USP-S | Orion (Field-Tested)', 
                         wear='0.18', 
                         price=45.2, 
                         item=None, 
                         user=UserDTO(
                              id=6, 
                              username='steam_seller', 
                              sell_items=[]
                         )
                    ), 
                    MarketItemDTO(
                         id=15, 
                         item_id=4,
                         user_id=5, 
                         full_name='Glock-18 | Water Elemental (Field-Tested)', 
                         wear='0.25', 
                         price=15.8, 
                         item=None, 
                         user=UserDTO(
                              id=5, 
                              username='collector_alex', 
                              sell_items=[]
                         )
                    )
               ]
          
          """
          order_by = []
          if price_order_by:
               order_by.append(
                    OrderByConfig(
                         column="price",
                         mode=price_order_by
                    )
               )
          
          filters_for_items_config: list[Filter] = []
          if categories:
               filters_for_items_config.append(
                    Filter(column="category", value=categories, filter_type=FilterType.IN)
               )
               
          filters_for_market_items_config: list[Filter] = []
          if full_name:
               filters_for_market_items_config.append(
                    Filter(column="full_name_vector", value=full_name, filter_type=FilterType.VECTOR_SORT)
               )
          if wears:
               filters_for_market_items_config.append(
                    Filter(column="wear", value=wears, filter_type=FilterType.IN)
               )
          if price and price_filter_type:
               filters_for_market_items_config.append(
                    Filter(column="price", value=price, filter_type=price_filter_type)
               )
               
          items_config: list[FilterConfig] = []
          if filters_for_items_config:
               items_config.append(
                    FilterConfig(filters=filters_for_items_config)
               )
          
          market_items_config: list[FilterConfig] = []
          if filters_for_market_items_config:
               market_items_config.append(
                    FilterConfig(filters=filters_for_market_items_config, mode=FilterLogicType.AND)
               )
          
          async with uow:
               items = await uow.market_item.read(
                    order_by=order_by,
                    loads=[LazyLoadConfig(relationship_strategy="user")],
                    joins=[
                         JoinConfig(
                              table_name="items",
                              filters=items_config
                         )
                    ],
                    filters=market_items_config,
                    is_many=True
               )
               return items if items else []
          