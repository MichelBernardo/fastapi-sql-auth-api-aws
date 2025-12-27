from core.configs import settings
from core.database import engine
import asyncio


async def create_tables() -> None:
    import models.__all_models
    print('Trying to connect to the database...')
    
    retry_count = 10
    while retry_count > 0:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
                await conn.run_sync(settings.DBBaseModel.metadata.create_all)
            print('Tabelas criadas com sucesso.')
            break
        except Exception as e:
            retry_count -= 1
            print(f"Database not yet available... Trying again in 2s ({retry_count} remaining attempts)")
            if retry_count == 0:
                print("We were unable to connect to the database.")
                raise e
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(create_tables())