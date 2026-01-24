import inspect

from typing import TYPE_CHECKING, TypeVar, ParamSpec, Callable
from dishka import Provider, Scope, provide, make_async_container

from repository.uow.interface import UnitOfWorkProtocol
from repository.uow.impl.alchemy import UnitOfWorkSQLAlchemy
from service.interfaces.user import UserServiceProtocol

if TYPE_CHECKING:
     from service.impl.user import UserService


T = TypeVar("T")
P = ParamSpec("P")

class MainProvider(Provider):
     
     @provide(scope=Scope.REQUEST)
     def uow_impl(self) -> UnitOfWorkProtocol:
          return UnitOfWorkSQLAlchemy()
     
     @provide(scope=Scope.REQUEST)
     def user_service_impl(self) -> UserServiceProtocol:
          return UserService()
     
     
async_di_container = make_async_container(MainProvider())


def inject_dependency(func: Callable[P, T]) -> Callable[P, T]:
     async def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
          signature = inspect.signature(func)
          
          for arg, param in signature.parameters.items():
               if hasattr(param.annotation, "__args__"):
                    args_types = param.annotation.__args__
                    
                    if args_types:
                         async with async_di_container() as container:
                              di = await container.get(args_types[0])
                              if di and arg not in kwargs:
                                   kwargs[arg] = di
          return await func(self, *args, **kwargs)
     return wrapper