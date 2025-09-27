from models.model_list import Object
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class ObjectController:

    @staticmethod
    async def add_object(name: str,
                         obj_type: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            obj = Object(
                name=name,
                type=obj_type
            )
            session.add(obj)
            await session.commit()

    @staticmethod
    async def delete_object(object_id: Optional[int] = None,
                            name: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            query = select(Object)
            if object_id is not None:
                query = query.where(Object.object_id == object_id)
            elif name is not None:
                query = query.where(Object.name == name)
            result = await session.execute(query)
            obj = result.scalars().first()
            if obj:
                await session.delete(obj)
                await session.commit()

    @staticmethod
    async def update_object(object_id: int,
                            name: Optional[str] = None,
                            obj_type: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            obj = await session.get(Object, object_id)
            if not obj:
                return
            if name is not None:
                obj.name = name
            if obj_type is not None:
                obj.type = obj_type
            await session.commit()

    @staticmethod
    async def select_all() -> List[Object]:
        async with get_async_session_context() as session:
            result = await session.execute(select(Object))
            return result.scalars().all()

    @staticmethod
    async def select_object(object_id: Optional[int] = None,
                              name: Optional[str] = None) -> Optional[Object]:
        async with get_async_session_context() as session:
            query = select(Object)
            if object_id is not None:
                query = query.where(Object.object_id == object_id)
            if name is not None:
                query = query.where(Object.name == name)
            result = await session.execute(query)
            return result.scalars().first()