# read_usecases.py
import asyncio
from controllers.usecase_controller import UseCaseController

async def main():
    # 取得所有 UseCase
    use_cases = await UseCaseController.list_use_cases()
    # 印出每筆記錄的欄位
    for uc in use_cases:
        print(f"""\
use_case_id: {uc.use_case_id}
name       : {uc.name}
project_id : {uc.project_id}
description: {uc.description}
normal_proc: {uc.normal_process}
exception_proc: {uc.exception_process}
pre_cond   : {uc.pre_condition}
post_cond  : {uc.post_condition}
{'—'*40}
""")

if __name__ == "__main__":
    asyncio.run(main())
