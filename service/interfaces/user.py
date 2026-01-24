from typing import Protocol

from schema.dto import UserDTO



class UserServiceProtocol(Protocol):
     
     async def get_user_by_id(self, id: int, *args, **kwargs) -> UserDTO:
          """Метод возвращает пользователя по его id"""
          raise NotImplementedError
     
     async def get_user_with_sell_items(self, id: int, *args, **kwargs) -> UserDTO:
          """Метод возвращает пользователя вместе с предметами, которые он продаёт"""
          raise NotImplementedError
     
     async def get_users_by_item_category(self, category: str, *args, **kwargs) -> list[UserDTO]:
          """Метод возвращает всех пользователей, которые продают определённую `category` с сортировкой по стоимости(DESC)"""
          raise NotImplementedError
     
     async def get_users_by_full_name_of_item(self, full_name: str, *args, **kwargs) -> list[UserDTO]:
          """Метод возвращает всех пользователей кто продаёт предмет `full_name`"""
          raise NotImplementedError