import asyncio

from service.impl.user import UserService
from service.impl.item import ItemService
from service.impl.market_item import MarketItemService

from repository.builder_configs.types import FilterType, OrderByType


async def call_user_service_methods() -> None:
     service = UserService()
     
     user = await service.get_user_by_id(id=1)
     print(f"User: {user}\n\n")
     
     user_with_sell_items = await service.get_user_with_sell_items(id=1)
     print(f"User with sell items: {user_with_sell_items}\n\n")
     
     users_by_full_name = await service.get_users_by_full_name_of_item(
          full_name="AK-47 | Redline (Field-Tested)"
     )
     print(f"Users who selling item AK-47 | Redline (Field-Tested): {users_by_full_name}")
     
     users_by_category = await service.get_users_by_item_category(category="rifle")
     print(f"User who selling item with categorry 'rifle', sorted by price DESC: {users_by_category}")
     
     
async def call_item_service_methods() -> None:
     service = ItemService()
     
     item = await service.get_item_with_market_items(id=2)
     print(f"Item: {item}\n\n")
     
     items = await service.get_items_of_categories(categories=["rifle", "sniper"])
     print(f"Items: {items}\n")
     

async def call_market_item_service_methods() -> None:
     service = MarketItemService()
     
     items = await service.paginate_market_items(
          categories=["rifle", "pistol"],
          price=150,
          price_filter_type=FilterType.LE,
          price_order_by=OrderByType.DESC,
          limit=2,
          offset=0
     )
     print(f"Items: {items}")


async def main() -> None:
     # await call_user_service_methods() 
     # await call_item_service_methods()
     await call_market_item_service_methods()
      
     
if __name__ == "__main__":
     asyncio.run(main())