from models.model_list import Method
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class MethodController:
    @staticmethod
    async def add_method(name: str,
                         parameters: str,
                         visibility: str,
                         return_type: str,
                         object_id: int) -> None:
        async with get_async_session_context() as session:
            method = Method(
                name=name,
                parameters=parameters,
                visibility=visibility,
                return_type=return_type,
                object_id=object_id
            )
            session.add(method)
            await session.commit()

    @staticmethod
    async def delete_method(method_id: Optional[int] = None,
                            name: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            query = select(Method)
            if method_id is not None:
                query = query.where(Method.method_id == method_id)
            elif name is not None:
                query = query.where(Method.name == name)
            result = await session.execute(query)
            method = result.scalars().first()
            if method:
                await session.delete(method)
                await session.commit()

    @staticmethod
    async def update_method(method_id: int,
                            name: Optional[str] = None,
                            parameters: Optional[str] = None,
                            visibility: Optional[str] = None,
                            return_type: Optional[str] = None
                            ) -> None:
        async with get_async_session_context() as session:
            method = await session.get(Method, method_id)
            if not method:
                return
            if name is not None:
                method.name = name
            if parameters is not None:
                method.parameters = parameters
            if visibility is not None:
                method.visibility = visibility
            if return_type is not None:
                method.return_type = return_type
            await session.commit()

    @staticmethod
    async def select_all() -> List[Method]:
        async with get_async_session_context() as session:
            result = await session.execute(select(Method))
            return result.scalars().all()

    @staticmethod
    async def select_method(method_id: Optional[int] = None,
                            name: Optional[str] = None) -> Optional[Method]:
        async with get_async_session_context() as session:
            query = select(Method)
            if method_id is not None:
                query = query.where(Method.method_id == method_id)
            elif name is not None:
                query = query.where(Method.name == name)
            result = await session.execute(query)
            return result.scalars().first()