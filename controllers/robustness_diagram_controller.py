from models.model_list import RobustnessDiagram
from init_db import get_async_session_context
from sqlalchemy.future import select
from typing import List, Optional

class RobustnessDiagramController:

    @staticmethod
    async def add_robustness_diagram(description: str,
                                     use_case_id: int) -> None:
        async with get_async_session_context() as session:
            rd = RobustnessDiagram(
                description=description,
                use_case_id=use_case_id
            )
            session.add(rd)
            await session.commit()

    @staticmethod
    async def delete_robustness_diagram(robustness_diagram_id: Optional[int] = None,
                                        use_case_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            query = select(RobustnessDiagram)
            if robustness_diagram_id is not None:
                query = query.where(RobustnessDiagram.robustness_diagram_id == robustness_diagram_id)
            elif use_case_id is not None:
                query = query.where(RobustnessDiagram.use_case_id == use_case_id)
            result = await session.execute(query)
            rd = result.scalars().first()
            if rd:
                await session.delete(rd)
                await session.commit()

    @staticmethod
    async def update_robustness_diagram(robustness_diagram_id: int,
                                        description: Optional[str] = None,
                                        use_case_id: Optional[int] = None) -> None:
        async with get_async_session_context() as session:
            rd = await session.get(RobustnessDiagram, robustness_diagram_id)
            if not rd:
                return
            if description is not None:
                rd.description = description
            if use_case_id is not None:
                rd.use_case_id = use_case_id
            await session.commit()

    @staticmethod
    async def select_all() -> List[RobustnessDiagram]:
        async with get_async_session_context() as session:
            result = await session.execute(select(RobustnessDiagram))
            return result.scalars().all()

    @staticmethod
    async def select_robustness_diagram(robustness_diagram_id: Optional[int] = None,
                                        use_case_id: Optional[int] = None) -> Optional[RobustnessDiagram]:
        async with get_async_session_context() as session:
            query = select(RobustnessDiagram)
            if robustness_diagram_id is not None:
                query = query.where(RobustnessDiagram.robustness_diagram_id == robustness_diagram_id)
            if use_case_id is not None:
                query = query.where(RobustnessDiagram.use_case_id == use_case_id)
            result = await session.execute(query)
            return result.scalars().first()