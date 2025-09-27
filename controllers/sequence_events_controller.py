from models.model_list import SequenceEvent
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class SequenceEventController:

    @staticmethod
    async def add_sequence_event(sequence_diagram_name: str,
                                 sequence_no:int,
                                 event_type: str,
                                 parameters: str
                                ) -> None:
        async with get_async_session_context() as session:
            se = SequenceEvent(
                sequence_diagram_name=sequence_diagram_name,
                sequence_no=sequence_no,
                event_type=event_type,
                parameters=parameters
            )
            session.add(se)
            await session.commit()

    @staticmethod
    async def delete_sequence_event(sequence_eventsID: Optional[int] = None,
                                    sequence_diagram_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(SequenceEvent)
            if sequence_eventsID is not None:
                query = query.where(SequenceEvent.sequence_eventsID == sequence_eventsID)
            elif sequence_diagram_id is not None:
                query = query.where(SequenceEvent.sequence_diagram_id == sequence_diagram_id)
            result = await session.execute(query)
            se = result.scalars().first()
            if se:
                await session.delete(se)
                await session.commit()

    @staticmethod
    async def update_sequence_event(sequence_eventsID: int,
                                    sequence_diagram_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            se = await session.get(SequenceEvent, sequence_eventsID)
            if not se:
                return
            if sequence_diagram_id is not None:
                se.sequence_diagram_id = sequence_diagram_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[SequenceEvent]:
        async with get_async_session_context() as session:
            result = await session.execute(select(SequenceEvent))
            return result.scalars().all()

    @staticmethod
    async def select_sequence_event(sequence_eventsID: Optional[int] = None,
                                    sequence_diagram_id: Optional[int] = None) -> Optional[SequenceEvent]:
        async with get_async_session_context() as session:
            query = select(SequenceEvent)
            if sequence_eventsID is not None:
                query = query.where(SequenceEvent.sequence_eventsID == sequence_eventsID)
            if sequence_diagram_id is not None:
                query = query.where(SequenceEvent.sequence_diagram_id == sequence_diagram_id)
            result = await session.execute(query)
            return result.scalars().first()
