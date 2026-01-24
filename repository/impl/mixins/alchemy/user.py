
from db.models import User
from schema.dto import UserDTO



class SQLAlchemyUserRepositoryMixin:
     mixin_model = User
     
     async def method_only_for_user(self, *args, **kwargs) -> UserDTO:
          """некоторый блок кода этого метода"""