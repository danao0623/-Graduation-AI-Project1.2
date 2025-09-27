from models.model_list import Project, UseCase, Actor, UserAccount, user_project
from init_db import get_async_session_context
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

class ProjectController:

    @staticmethod
    async def add_project(
        name: str,
        description: str,
        architecture: str,
        frontend_language: str,
        frontend_platform: str,
        frontend_library: str,
        backend_language: str,
        backend_platform: str,
        backend_library: str,
        use_case_ids: Optional[List[int]] = None,
        actor_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None,
    ) -> Project:
        async with get_async_session_context() as session:
            project = Project(
                name=name,
                description=description,
                architecture=architecture,
                frontend_language=frontend_language,
                frontend_platform=frontend_platform,
                frontend_library=frontend_library,
                backend_language=backend_language,
                backend_platform=backend_platform,
                backend_library=backend_library,
            )
            session.add(project)
            await session.flush()
            await session.refresh(project)

            # 更新 UseCase 的 project_id
            if use_case_ids:
                for uc_id in use_case_ids:
                    use_case = await session.get(UseCase, uc_id)
                    if use_case:
                        use_case.project_id = project.id

            # 更新 Actor 的 project_id
            if actor_ids:
                for a_id in actor_ids:
                    actor = await session.get(Actor, a_id)
                    if actor:
                        actor.project_id = project.id

            if user_id is not None:
                result = await session.execute(
                    select(UserAccount).options(selectinload(UserAccount.projects)).where(UserAccount.id == user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    user.projects.append(project)

            await session.commit()
            return project

    @staticmethod
    async def delete_project(
        id: int = None,
        name: str = None
    ) -> None:
        async with get_async_session_context() as session:
            result = await session.execute(
                select(Project).where((Project.id == id) | (Project.name == name))
            )
            project = result.scalars().first()
            if project:
                await session.delete(project)
                await session.commit()

    @staticmethod
    async def update_project(
        id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        architecture: Optional[str] = None,
        frontend_language: Optional[str] = None,
        frontend_platform: Optional[str] = None,
        frontend_library: Optional[str] = None,
        backend_language: Optional[str] = None,
        backend_platform: Optional[str] = None,
        backend_library: Optional[str] = None,
    ) -> None:
        async with get_async_session_context() as session:
            project = await session.get(Project, id)
            if not project:
                return
            if name is not None:
                project.name = name
            if description is not None:
                project.description = description
            if architecture is not None:
                project.architecture = architecture
            if frontend_language is not None:
                project.frontend_language = frontend_language
            if frontend_platform is not None:
                project.frontend_platform = frontend_platform
            if frontend_library is not None:
                project.frontend_library = frontend_library
            if backend_language is not None:
                project.backend_language = backend_language
            if backend_platform is not None:
                project.backend_platform = backend_platform
            if backend_library is not None:
                project.backend_library = backend_library
            await session.commit()

    @staticmethod
    async def select_all() -> List[Project]:
        async with get_async_session_context() as session:
            result = await session.execute(
                select(Project).options(selectinload(Project.actors))
            )
            return result.scalars().all()

    @staticmethod
    async def select_project(
        id: int = None,
        name: str = None
    ) -> Optional[Project]:
        async with get_async_session_context() as session:
            query = select(Project).options(selectinload(Project.actors))
            if id is not None:
                query = query.where(Project.id == id)
            elif name is not None:
                query = query.where(Project.name == name)
            result = await session.execute(query)
            return result.scalars().first()

    @staticmethod
    async def get_projects_by_user_id(user_id: int):
        async with get_async_session_context() as session:
            result = await session.execute(
                select(Project).join(user_project).where(user_project.c.user_id == user_id)
            )
            projects = result.scalars().all()
            return projects