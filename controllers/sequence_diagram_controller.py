from models.model_list import SequenceDiagram
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class SequenceDiagramController:

    @staticmethod
    async def add_sequence_diagram(robustness_diagram_id: int) -> None:
        async with get_async_session_context() as session:
            sd = SequenceDiagram(
                robustness_diagram_id=robustness_diagram_id
            )
            session.add(sd)
            await session.commit()

    @staticmethod
    async def delete_sequence_diagram(sequence_diagram_id: Optional[int] = None,
                                       robustness_diagram_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(SequenceDiagram)
            if sequence_diagram_id is not None:
                query = query.where(SequenceDiagram.sequence_diagram_id == sequence_diagram_id)
            elif robustness_diagram_id is not None:
                query = query.where(SequenceDiagram.robustness_diagram_id == robustness_diagram_id)
            result = await session.execute(query)
            sd = result.scalars().first()
            if sd:
                await session.delete(sd)
                await session.commit()

    @staticmethod
    async def update_sequence_diagram(sequence_diagram_id: int,
                                      robustness_diagram_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            sd = await session.get(SequenceDiagram, sequence_diagram_id)
            if not sd:
                return
            if robustness_diagram_id is not None:
                sd.robustness_diagram_id = robustness_diagram_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[SequenceDiagram]:
        async with get_async_session_context() as session:
            result = await session.execute(select(SequenceDiagram))
            return result.scalars().all()

    @staticmethod
    async def select_sequence_diagram(sequence_diagram_id: Optional[int] = None,
                                      robustness_diagram_id: Optional[int] = None) -> Optional[SequenceDiagram]:
        async with get_async_session_context() as session:
            query = select(SequenceDiagram)
            if sequence_diagram_id is not None:
                query = query.where(SequenceDiagram.sequence_diagram_id == sequence_diagram_id)
            if robustness_diagram_id is not None:
                query = query.where(SequenceDiagram.robustness_diagram_id == robustness_diagram_id)
            result = await session.execute(query)
            return result.scalars().first()