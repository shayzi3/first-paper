from typing import Protocol

from schema.dto import UserDTO



class UserRepositoryMixinProtocol(Protocol):
     
     
     async def method_only_for_user(self, *args, **kwargs) -> UserDTO:
          raise NotImplementedError