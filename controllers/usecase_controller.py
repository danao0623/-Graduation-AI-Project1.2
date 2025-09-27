from models.model_list import UseCase, Project
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class UseCaseController:
    @staticmethod
    async def add_use_case(
        name: str,
        description: str,
        project_id: int,
        normal_process: Optional[str] = None,
        exception_process: Optional[str] = None,
        pre_condition: Optional[str] = None,
        post_condition: Optional[str] = None,
        trigger_condition: Optional[str] = None
    ) -> Optional[UseCase]:
        """
        新增 UseCase 並設定對應的 project_id 外鍵
        若同一 project_id 下 usecase.name 重複則回傳已存在的 usecase
        """
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UseCase).where(
                    UseCase.name == name,
                    UseCase.project_id == project_id
                )
            )
            existing_use_case = result.scalars().first()
            if existing_use_case:
                return existing_use_case  # 回傳已存在的 usecase
            use_case = UseCase(
                name=name,
                description=description,
                normal_process=normal_process,
                exception_process=exception_process,
                pre_condition=pre_condition,
                post_condition=post_condition,
                trigger_condition=trigger_condition,
                project_id=project_id
            )
            session.add(use_case)
            await session.commit()
            await session.refresh(use_case)
            return use_case

    @staticmethod
    async def update_use_case(
        use_case_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        normal_process: Optional[str] = None,
        exception_process: Optional[str] = None,
        pre_condition: Optional[str] = None,
        post_condition: Optional[str] = None,
        trigger_condition: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Optional[UseCase]:
        """
        更新 UseCase 屬性，包括可修改的各欄位及 project_id
        """
        async with get_async_session_context() as session:
            use_case = await session.get(UseCase, use_case_id)
            if not use_case:
                return None
            if name is not None:
                use_case.name = name
            if description is not None:
                use_case.description = description
            if normal_process is not None:
                use_case.normal_process = normal_process
            if exception_process is not None:
                use_case.exception_process = exception_process
            if pre_condition is not None:
                use_case.pre_condition = pre_condition
            if post_condition is not None:
                use_case.post_condition = post_condition
            if trigger_condition is not None:
                use_case.trigger_condition = trigger_condition
            if project_id is not None:
                use_case.project_id = project_id
            await session.commit()
            await session.refresh(use_case)
            return use_case

    @staticmethod
    async def delete_use_case(
        use_case_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        刪除 UseCase，透過 use_case_id 或 name 定位
        """
        async with get_async_session_context() as session:
            query = select(UseCase)
            if use_case_id is not None:
                query = query.where(UseCase.use_case_id == use_case_id)
            elif name is not None:
                query = query.where(UseCase.name == name)
            else:
                return False
            result = await session.execute(query)
            use_case = result.scalars().first()
            if not use_case:
                return False
            await session.delete(use_case)
            await session.commit()
            return True

    @staticmethod
    async def get_use_case(
        use_case_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[UseCase]:
        """
        取得單一 UseCase，透過 use_case_id 或 name 查詢
        """
        async with get_async_session_context() as session:
            query = select(UseCase)
            if use_case_id is not None:
                query = query.where(UseCase.use_case_id == use_case_id)
            elif name is not None:
                query = query.where(UseCase.name == name)
            else:
                return None
            result = await session.execute(query)
            return result.scalars().first()
        

    @staticmethod
    async def get_use_case_by_project(project_id: int) -> List[UseCase]:
        """
        根據 project_id 獲取所有 UseCase
        """
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UseCase).where(UseCase.project_id == project_id)
            )
            return result.scalars().all()

    @staticmethod
    async def list_use_cases() -> List[UseCase]:
        """
        列出所有 UseCase
        """
        async with get_async_session_context() as session:
            result = await session.execute(select(UseCase))
            return result.scalars().all()
