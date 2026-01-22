import asyncio

from service.impl.test_service import ItemWearService
from repository.sqlalchemy_repo.item_wear import ItemWearSQLAlchemyRepository

def main():
     result = ItemWearService(
          repository=ItemWearSQLAlchemyRepository()
     )
     asyncio.run(result.get_item(id=1))
     

if __name__ == "__main__":
     main()