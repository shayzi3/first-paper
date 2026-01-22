
from db.models import session
from schema.dto import ItemWearDTO
from repository.interface import RepositoryProtocol
from repository.builder_configs.configs import (
     FilterConfig,
     Filter,
     LazyLoadConfig,
     ColumnConfig
)
from repository.builder_configs.types import FilterType




class ItemWearService:
     
     def __init__(self, repository: RepositoryProtocol):
          self.repository = repository
     
     async def get_item(self, id: int) -> ItemWearDTO:
          async with session() as s:
               item = await self.repository.read(
                    session=s,
                    filter=[
                         FilterConfig(filters=[Filter(column="id", value=id, filter_type=FilterType.EQ)])
                    ],
                    columns=[ColumnConfig(column="item")],
                    # load=[LazyLoadConfig(relationship_strategy="item.collections")]
               )
               print(item.item, item.item.collections)
               return item