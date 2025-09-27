from models.model_list import UseCaseActor
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class UseCaseActorController:

    @staticmethod
    async def add_association(use_case_id: int, actors: List[dict]) -> None:
        async with get_async_session_context() as session:
            for actor in actors:
                # 確保 Actor 包含必要屬性
                if "id" not in actor:
                    print(f"Error: Missing 'id' for actor {actor}")
                    continue
            
                # 新增關聯
                assoc = UseCaseActor(
                    use_case_id=use_case_id,
                    actor_id=actor["id"]
                )
                session.add(assoc)
            await session.commit()


    @staticmethod
    async def delete_association(use_case_id: Optional[int] = None,
                                 actor_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(UseCaseActor)
            if use_case_id is not None and actor_id is not None:
                query = query.where(
                    (UseCaseActor.use_case_id == use_case_id) &
                    (UseCaseActor.actor_id == actor_id)
                )
            elif use_case_id is not None:
                query = query.where(UseCaseActor.use_case_id == use_case_id)
            elif actor_id is not None:
                query = query.where(UseCaseActor.actor_id == actor_id)
            result = await session.execute(query)
            assoc = result.scalars().first()
            if assoc:
                await session.delete(assoc)
                await session.commit()

    @staticmethod
    async def select_all() -> List[UseCaseActor]:
        async with get_async_session_context() as session:
            result = await session.execute(select(UseCaseActor))
            return result.scalars().all()

    @staticmethod
    async def select_association(use_case_id: Optional[int] = None,
                                 actor_id: Optional[int] = None) -> Optional[UseCaseActor]:
        async with get_async_session_context() as session:
            query = select(UseCaseActor)
            if use_case_id is not None:
                query = query.where(UseCaseActor.use_case_id == use_case_id)
            if actor_id is not None:
                query = query.where(UseCaseActor.actor_id == actor_id)
            result = await session.execute(query)
            return result.scalars().first()