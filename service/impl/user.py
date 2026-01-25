from dishka import FromDishka

from repository.uow.interface import UnitOfWorkProtocol
from schema.dto import UserDTO
from dependency.provider import inject_dependency
from repository.builder_configs.configs import (
     FilterConfig,
     Filter,
     LazyLoadConfig,
     JoinConfig,
     OrderByConfig,
     ColumnConfig
)
from repository.builder_configs.types import OrderByType



class UserService:
     
     @inject_dependency
     async def get_user_by_id(
          self, 
          id: int,
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> UserDTO | None:
          """
               Метод возвращает пользователя по его id
               
               Возвращаемые данные: id = 1
                    id=1 username='trader_john' sell_items=[]
          """
          async with uow:
               user = await uow.user.read(
                    filters=[FilterConfig(filters=[Filter(column="id", value=id)])]
               )
               return user
     
     @inject_dependency
     async def get_user_with_sell_items(
          self, 
          id: int,
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> UserDTO | None:
          """
               Метод возвращает пользователя вместе с предметами, которые он продаёт
               
               Возвращаемые данные: id = 1
                    id=1 username='trader_john' sell_items=[
                         MarketItemDTO(
                              id=1, 
                              item_id=1, 
                              user_id=1, 
                              full_name='AK-47 | Redline (Field-Tested)', 
                              wear='0.15', price=150.5, 
                              item=None, 
                              user=None
                         ), 
                         MarketItemDTO(
                              id=2, 
                              item_id=2, 
                              user_id=1, 
                              ull_name='AWP | Dragon Lore (Factory New)', 
                              wear='0.01', 
                              price=12500.0, 
                              item=None, 
                              user=None
                         )
                    ]
          """
          async with uow:
               user_with_items = await uow.user.read(
                    filters=[FilterConfig(filters=[Filter(column="id", value=id)])],
                    loads=[LazyLoadConfig(relationship_strategy="sell_items")]
               )
               return user_with_items
          
          
     @inject_dependency
     async def get_users_by_full_name_of_item(
          self,
          full_name: str,
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> list[UserDTO]:
          """
               Метод возвращает всех пользователей кто продаёт предмет `full_name` и все предметы, которые они продают.
               
               Возвращаемые данные: full_name = "AK-47 | Redline (Field-Tested)"
                    [
                         UserDTO(
                              id=1, 
                              username='trader_john', 
                              sell_items=[
                                   MarketItemDTO(
                                        id=1, 
                                        item_id=1, 
                                        user_id=1, 
                                        full_name='AK-47 | Redline (Field-Tested)', 
                                        wear='0.15', 
                                        price=150.5, 
                                        item=ItemDTO(
                                             id=1, 
                                             short_name='ak47', 
                                             category='rifle', 
                                             market_items=[]
                                        ), 
                                        user=None
                                   ), 
                                   MarketItemDTO(
                                        id=2, 
                                        item_id=2, 
                                        user_id=1, 
                                        full_name='AWP | Dragon Lore (Factory New)', 
                                        wear='0.01', 
                                        price=12500.0, 
                                        item=ItemDTO(
                                             id=2, 
                                             short_name='awp', 
                                             category='sniper', 
                                             market_items=[]
                                        ), 
                                        user=None
                                   )
                              ]
                         ), 
                         UserDTO(
                              id=2, 
                              username='csgo_queen', 
                              sell_items=[
                                   MarketItemDTO(
                                        id=3, 
                                        item_id=3, 
                                        user_id=2, 
                                        full_name='M4A1-S | Hyper Beast (Minimal Wear)',
                                        wear='0.07', 
                                        price=89.99, 
                                        item=ItemDTO(
                                             id=3, 
                                             short_name='m4a1s', 
                                             category='rifle', 
                                             market_items=[]), 
                                             user=None
                                        ), 
                                        MarketItemDTO(
                                             id=4, 
                                             item_id=6, 
                                             user_id=2, f
                                             ull_name='★ Karambit | Doppler (Factory New)', 
                                             wear='0.02', 
                                             price=1850.75, 
                                             item=ItemDTO(
                                                  id=6, 
                                                  short_name='knife_karambit', 
                                                  category='knife', market_items=[]
                                             ), 
                                             user=None
                                        ), 
                                        MarketItemDTO(
                                             id=16, 
                                             item_id=1, 
                                             user_id=2, 
                                             full_name='AK-47 | Redline (Field-Tested)', 
                                             wear='0.21', 
                                             price=130.0, 
                                             item=ItemDTO(
                                                  id=1, 
                                                  short_name='ak47', 
                                                  category='rifle', 
                                                  market_items=[]
                                             ), 
                                             user=None
                                        )
                                   ]
                              )
                    ]
          
          """
          async with uow:
               users = await uow.user.read(
                    joins=[
                         JoinConfig(
                              table_name="market_items",
                              filters=[FilterConfig(filters=[Filter(column="full_name", value=full_name)])]
                         )
                    ],
                    loads=[
                         LazyLoadConfig(relationship_strategy="sell_items.item")   
                    ],
                    is_many=True # аргумент позваоляет возвращать все полученные данные из бд
               )
               return users
          
          
     @inject_dependency
     async def get_users_by_item_category(
          self,
          category: str,
          uow: FromDishka[UnitOfWorkProtocol]
     ) -> list[UserDTO]:
          """
               Метод возвращает всех пользователей, которые продают определённую `category` с сортировкой по стоимости(DESC)
               
               Возвращаемые данные: category = "rifle"
                    [
                         {'username': 'gaming_vault', 'full_name': 'AK-47 | Redline (Minimal Wear)', 'price': 180.9, 'category': 'rifle'}, 
                         {'username': 'trader_john', 'full_name': 'AK-47 | Redline (Field-Tested)', 'price': 150.5, 'category': 'rifle'}, 
                         {'username': 'csgo_queen', 'full_name': 'AK-47 | Redline (Field-Tested)', 'price': 130.0, 'category': 'rifle'}, 
                         {'username': 'premium_trader', 'full_name': 'AK-47 | Redline (Well-Worn)', 'price': 120.75, 'category': 'rifle'}, 
                         {'username': 'skin_master', 'full_name': 'M4A1-S | Cyrex (Factory New)', 'price': 110.25, 'category': 'rifle'}, 
                         {'username': 'csgo_queen', 'full_name': 'M4A1-S | Hyper Beast (Minimal Wear)', 'price': 89.99, 'category': 'rifle'}
                    ]
          """
          async with uow:
               users = await uow.user.read(
                    joins=[
                         JoinConfig(
                              table_name="market_items",
                              order_by=[OrderByConfig(column="price", mode=OrderByType.DESC)],
                              columns=[ColumnConfig(column="full_name"), ColumnConfig(column="price")]
                         ),
                         JoinConfig(
                              table_name="items",
                              filters=[FilterConfig(filters=[Filter(column="category", value=category)])],
                              columns=[ColumnConfig(column="category")]
                         )
                    ],
                    columns=[ColumnConfig(column="username")],
                    is_many=True
               )
               return users