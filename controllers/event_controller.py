from models.model_list import Event
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class EventController:

    @staticmethod
    async def add_event(sequence_no: int,
                        type: str,
                        description: str,
                        event_list_id: int) -> None:
        async with get_async_session_context() as session:
            event = Event(
                sequence_no=sequence_no,
                type=type,
                description=description,
                event_list_id=event_list_id
            )
            session.add(event)
            await session.commit()

    @staticmethod
    async def delete_event(event_id: Optional[int] = None,
                            description: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            query = select(Event)
            if event_id is not None:
                query = query.where(Event.event_id == event_id)
            elif description is not None:
                query = query.where(Event.description == description)
            result = await session.execute(query)
            event = result.scalars().first()
            if event:
                await session.delete(event)
                await session.commit()

    @staticmethod
    async def update_event(event_id: int,
                           sequence_no: Optional[int] = None,
                           type: Optional[str] = None,
                           description: Optional[str] = None,
                           event_list_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            event = await session.get(Event, event_id)
            if not event:
                return
            if sequence_no is not None:
                event.sequence_no = sequence_no
            if type is not None:
                event.type = type
            if description is not None:
                event.description = description
            if event_list_id is not None:
                event.event_list_id = event_list_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[Event]:
        async with get_async_session_context() as session:
            result = await session.execute(select(Event))
            return result.scalars().all()

    @staticmethod
    async def select_event(event_id: Optional[int] = None,
                            description: Optional[str] = None) -> Optional[Event]:
        async with get_async_session_context() as session:
            query = select(Event)
            if event_id is not None:
                query = query.where(Event.event_id == event_id)
            if description is not None:
                query = query.where(Event.description == description)
            result = await session.execute(query)
            return result.scalars().first()