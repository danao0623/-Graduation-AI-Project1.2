from models.model_list import RobustnessObjects
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class RobustnessObjectsController:

    @staticmethod
    async def add_robustness_object(robustness_diagram_id: int,
                                     object_id: int) -> None:
        async with get_async_session_context() as session:
            ro = RobustnessObjects(
                robustness_diagram_id=robustness_diagram_id,
                object_id=object_id
            )
            session.add(ro)
            await session.commit()

    @staticmethod
    async def delete_robustness_object(robustness_object_id: Optional[int] = None,
                                        robustness_diagram_id: Optional[int] = None,
                                        object_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(RobustnessObjects)
            if robustness_object_id is not None:
                query = query.where(RobustnessObjects.robustness_object_id == robustness_object_id)
            if robustness_diagram_id is not None:
                query = query.where(RobustnessObjects.robustness_diagram_id == robustness_diagram_id)
            if object_id is not None:
                query = query.where(RobustnessObjects.object_id == object_id)
            result = await session.execute(query)
            ro = result.scalars().first()
            if ro:
                await session.delete(ro)
                await session.commit()

    @staticmethod
    async def update_robustness_object(robustness_object_id: int,
                                       robustness_diagram_id: Optional[int] = None,
                                       object_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            ro = await session.get(RobustnessObjects, robustness_object_id)
            if not ro:
                return
            if robustness_diagram_id is not None:
                ro.robustness_diagram_id = robustness_diagram_id
            if object_id is not None:
                ro.object_id = object_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[RobustnessObjects]:
        async with get_async_session_context() as session:
            result = await session.execute(select(RobustnessObjects))
            return result.scalars().all()

    @staticmethod
    async def select_robustness_object(robustness_object_id: Optional[int] = None,
                                       robustness_diagram_id: Optional[int] = None,
                                       object_id: Optional[int] = None) -> Optional[RobustnessObjects]:
        async with get_async_session_context() as session:
            query = select(RobustnessObjects)
            if robustness_object_id is not None:
                query = query.where(RobustnessObjects.robustness_object_id == robustness_object_id)
            if robustness_diagram_id is not None:
                query = query.where(RobustnessObjects.robustness_diagram_id == robustness_diagram_id)
            if object_id is not None:
                query = query.where(RobustnessObjects.object_id == object_id)
            result = await session.execute(query)
            return result.scalars().first()