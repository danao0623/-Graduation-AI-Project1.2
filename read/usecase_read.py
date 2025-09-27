from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from init_db import get_async_session_context
from models.model_list import UseCase, UseCaseActor,Actor

class UseCaseReader:

    @staticmethod
    async def get_use_case_with_actors(
        use_case_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[dict]:
        """
        查詢指定 UseCase 與其關聯 Actor
        - 支援用 use_case_id 或 name 查詢
        - 回傳 dict 結構資料（含 actor 清單）
        """
        async with get_async_session_context() as session:
            query = select(UseCase).options(
                selectinload(UseCase.actors).selectinload(UseCaseActor.actor)
            )

            if use_case_id is not None:
                query = query.where(UseCase.use_case_id == use_case_id)
            elif name is not None:
                query = query.where(UseCase.name == name)
            else:
                return None

            result = await session.execute(query)
            use_case = result.scalars().first()

            if not use_case:
                return None

            return {
                "use_case_id": use_case.use_case_id,
                "use_case_name": use_case.name,
                "actors": [
                    {
                        "actor_id": ua.actor.actor_id,
                        "actor_name": ua.actor.name
                    }
                    for ua in use_case.actors
                ]
            }
