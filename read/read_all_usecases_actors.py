import asyncio
from init_db import get_async_session_context
from models.model_list import UseCase, Actor
from sqlalchemy.future import select

async def main():
    async with get_async_session_context() as session:
        # 讀出所有 UseCase
        uc_result = await session.execute(select(UseCase))
        use_cases = uc_result.scalars().all()

        # 讀出所有 Actor
        actor_result = await session.execute(select(Actor))
        actors = actor_result.scalars().all()

    # 印出 UseCase 資料
    print("=== UseCases ===")
    for uc in use_cases:
        print(f"""\
use_case_id   : {uc.use_case_id}
name          : {uc.name}
project_id    : {uc.project_id}
description   : {uc.description}
normal_proc   : {uc.normal_process}
exception_proc: {uc.exception_process}
pre_cond      : {uc.pre_condition}
post_cond     : {uc.post_condition}
{'—' * 40}
""")

    # 空一行分隔
    print()

    # 印出 Actor 資料
    print("=== Actors ===")
    for actor in actors:
        print(f"""\
actor_id      : {actor.actor_id}
name          : {actor.name}
project_id    : {actor.project_id}
{'—' * 40}
""")

if __name__ == "__main__":
    asyncio.run(main())

