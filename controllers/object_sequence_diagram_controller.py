from models.model_list import ObjectSequenceDiagram
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class ObjectSequenceDiagramController:

    @staticmethod
    async def add_object_sequence_diagram(object_id: int,
                                           sequence_diagram_id: int) -> None:
        async with get_async_session_context() as session:
            osd = ObjectSequenceDiagram(
                object_id=object_id,
                sequence_diagram_id=sequence_diagram_id
            )
            session.add(osd)
            await session.commit()

    @staticmethod
    async def delete_object_sequence_diagram(object_id: Optional[int] = None,
                                              sequence_diagram_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(ObjectSequenceDiagram)
            if object_id is not None:
                query = query.where(ObjectSequenceDiagram.object_id == object_id)
            if sequence_diagram_id is not None:
                query = query.where(ObjectSequenceDiagram.sequence_diagram_id == sequence_diagram_id)
            result = await session.execute(query)
            osd = result.scalars().first()
            if osd:
                await session.delete(osd)
                await session.commit()

    @staticmethod
    async def select_all() -> List[ObjectSequenceDiagram]:
        async with get_async_session_context() as session:
            result = await session.execute(select(ObjectSequenceDiagram))
            return result.scalars().all()

    @staticmethod
    async def select_object_sequence_diagram(object_id: Optional[int] = None,
                                              sequence_diagram_id: Optional[int] = None) -> Optional[ObjectSequenceDiagram]:
        async with get_async_session_context() as session:
            query = select(ObjectSequenceDiagram)
            if object_id is not None:
                query = query.where(ObjectSequenceDiagram.object_id == object_id)
            if sequence_diagram_id is not None:
                query = query.where(ObjectSequenceDiagram.sequence_diagram_id == sequence_diagram_id)
            result = await session.execute(query)
            return result.scalars().first()
