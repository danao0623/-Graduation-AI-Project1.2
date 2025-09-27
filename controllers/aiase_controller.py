from models.model_list import UseCase,EventList,Event
from init_db import get_async_session_context
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
class AiaseController:

    @staticmethod
    async def get_events_by_usecase(use_case_id: int):
        async with get_async_session_context() as session:
            stmt = (
                select(UseCase)
                .options(
                    selectinload(UseCase.event_lists)
                    .selectinload(EventList.events)
                )
                .where(UseCase.id == use_case_id)
            )
            result = await session.execute(stmt)
            usecase = result.scalars().first()

            if not usecase:
                return {"error": "找不到指定的 UseCase"}

            events_data = []
            for el in usecase.event_lists:
                for e in el.events:
                    events_data.append({
                        "event_id": e.id,
                        "sequence_no": e.sequence_no,
                        "type": e.type,
                        "description": e.description,
                        "event_list_id": el.id,
                        "event_list_type": el.type,
                        "use_case_id": usecase.id,
                        "use_case_name": usecase.name
                    })

            return events_data

    @staticmethod
    async def get_event_summary_by_project(project_id: int):
        """根據 project_id 輸出所有 UseCase 及其事件摘要（依 event_list_type 分組）"""
        async with get_async_session_context() as session:
            stmt = (
                select(UseCase)
                .options(
                    selectinload(UseCase.event_lists)
                    .selectinload(EventList.events)
                )
                .where(UseCase.project_id == project_id)
            )
            result = await session.execute(stmt)
            usecases = result.scalars().all()

            summary_list = []
            for uc in usecases:
                # 動態收集所有 event_list_type
                event_summary = {}
                for el in uc.event_lists:
                    # 依 event_list_type 分組
                    event_type = el.type or "未分類"
                    # 事件依序號排序
                    event_items = [
                        {
                            "event_id": e.id,
                            "sequence_no": e.sequence_no,
                            "type": e.type,
                            "description": e.description
                        }
                        for e in sorted(el.events, key=lambda x: x.sequence_no)
                    ]
                    event_summary[event_type] = {"事件列表": event_items}
                summary_list.append({
                    "use_case_id": uc.id,
                    "use_case_name": uc.name,
                    "event_summary": event_summary
                })
            return summary_list