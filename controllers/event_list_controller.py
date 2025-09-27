from models.model_list import EventList
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class EventListController:

    @staticmethod
    async def add_event_list(list_type: str,
                             use_case_id: int) -> None:
        async with get_async_session_context() as session:
            event_list = EventList(
                type=list_type,
                use_case_id=use_case_id
            )
            session.add(event_list)
            await session.commit()
            return event_list

    @staticmethod
    async def delete_event_list(event_list_id: Optional[int] = None,
                                list_type: Optional[str] = None) -> None:
        async with get_async_session_context() as session:
            query = select(EventList)
            if event_list_id is not None:
                query = query.where(EventList.event_list_id == event_list_id)
            elif list_type is not None:
                query = query.where(EventList.type == list_type)
            result = await session.execute(query)
            event_list = result.scalars().first()
            if event_list:
                await session.delete(event_list)
                await session.commit()

    @staticmethod
    async def update_event_list(event_list_id: int,
                                list_type: Optional[str] = None,
                                use_case_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            event_list = await session.get(EventList, event_list_id)
            if not event_list:
                return
            if list_type is not None:
                event_list.type = list_type
            if use_case_id is not None:
                event_list.use_case_id = use_case_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[EventList]:
        async with get_async_session_context() as session:
            result = await session.execute(select(EventList))
            return result.scalars().all()

    @staticmethod
    async def select_event_list(event_list_id: Optional[int] = None,
                                list_type: Optional[str] = None) -> Optional[EventList]:
        async with get_async_session_context() as session:
            query = select(EventList)
            if event_list_id is not None:
                query = query.where(EventList.event_list_id == event_list_id)
            if list_type is not None:
                query = query.where(EventList.type == list_type)
            result = await session.execute(query)
            return result.scalars().first()