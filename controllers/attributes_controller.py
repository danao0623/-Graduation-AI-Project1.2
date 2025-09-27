from models.model_list import Attributes
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class AttributeController:

    @staticmethod
    async def add_attribute(name: str, 
                            datatype: str,
                            visibility: str,
                            object_id: int) -> None:
        async with get_async_session_context() as session:
            attribute = Attributes(name=name, datatype=datatype, visibility=visibility, object_id=object_id)
            session.add(attribute)
            await session.commit()

    @staticmethod
    async def delete_attribute(attribute_id: Optional[int] = None,
                               name: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            query = select(Attributes)
            if attribute_id is not None:
                query = query.where(Attributes.attribute_id == attribute_id)
            elif name is not None:
                query = query.where(Attributes.name == name)
            result = await session.execute(query)
            attribute = result.scalars().first()
            if attribute:
                await session.delete(attribute)
                await session.commit()

    @staticmethod
    async def update_attribute(attribute_id: int,
                               name: Optional[str] = None,
                               datatype: Optional[str] = None,
                               visibility: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            attribute = await session.get(Attributes, attribute_id)
            if not attribute:
                return
            if name is not None:
                attribute.name = name
            if datatype is not None:
                attribute.datatype = datatype
            if visibility is not None:
                attribute.visibility = visibility
            await session.commit()

    @staticmethod
    async def select_all() -> List[Attributes]:
        async with get_async_session_context() as session:
            result = await session.execute(select(Attributes))
            return result.scalars().all()

    @staticmethod
    async def select_attribute(attribute_id: Optional[int] = None,
                               name: Optional[str] = None) -> Optional[Attributes]:
        async with get_async_session_context() as session:
            query = select(Attributes)
            if attribute_id is not None:
                query = query.where(Attributes.attribute_id == attribute_id)
            elif name is not None:
                query = query.where(Attributes.name == name)
            result = await session.execute(query)
            return result.scalars().first()