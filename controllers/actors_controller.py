from models.model_list import Actor
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class ActorController:

    @staticmethod
    async def add_actor(
        name: str,
        project_id: int
    ) -> Optional[Actor]:
        async with get_async_session_context() as session:
            result =await session.execute(
                select(Actor).where(
                    Actor.name == name,
                    Actor.project_id == project_id
                )
            )
            existing_actor = result.scalars().first()
            if existing_actor:
                return None
            actor = Actor(name=name, project_id=project_id)
            session.add(actor)
            await session.commit()
            await session.refresh(actor)
            return actor

    @staticmethod
    async def delete_actor(
        actor_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> None:
        async with get_async_session_context() as session:
            query = select(Actor)
            if actor_id is not None:
                query = query.where(Actor.actor_id == actor_id)
            elif name is not None:
                query = query.where(Actor.name == name)
            result = await session.execute(query)
            actor = result.scalars().first()
            if actor:
                await session.delete(actor)
                await session.commit()

    @staticmethod
    async def update_actor(
        actor_id: int,
        name: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> None:
        async with get_async_session_context() as session:
            actor = await session.get(Actor, actor_id)
            if not actor:
                return
            if name is not None:
                actor.name = name
            if project_id is not None:
                actor.project_id = project_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[Actor]:
        async with get_async_session_context() as session:
            result = await session.execute(select(Actor))
            return result.scalars().all()

    @staticmethod
    async def select_actor(
        actor_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[Actor]:
        async with get_async_session_context() as session:
            query = select(Actor)
            if actor_id is not None:
                query = query.where(Actor.actor_id == actor_id)
            elif name is not None:
                query = query.where(Actor.name == name)
            result = await session.execute(query)
            return result.scalars().first()
    
    @staticmethod
    async def get_actors_by_project(project_id: int) -> List[Actor]:
        """
        根據 project_id 獲取所有 Actor
        """
        async with get_async_session_context() as session:
            result = await session.execute(
                select(Actor).where(Actor.project_id == project_id)
            )
            return result.scalars().all()