from models.model_list import UserAccount
from sqlalchemy.future import select
from typing import List
from core.database import Database
from init_db import get_async_session_context

class UserAccountControler:

    @classmethod
    async def add_user_account(cls, account: str, password: str) -> None:
        async with get_async_session_context() as session:
            user_account = UserAccount(
                account=account,
                password=password,
            )
            session.add(user_account)
            await session.commit()

        
    @classmethod
    async def delete_user_account(cls, id: int = None, account: str = None, email: str = None) -> None:
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserAccount).where((UserAccount.id == id) | (UserAccount.account == account) | (UserAccount.email == email))
            )
            user_account = result.scalars().first()
            await session.delete(user_account)
            await session.commit()

    @classmethod
    async def update_user_account(cls, id: int, account: str = None, password: str = None,) -> None:
        async with get_async_session_context() as session:
            user_account = await session.get(UserAccount, id)
            if account is not None:
                user_account.account = account
            if password is not None:
                user_account.password = password                                        
            await session.commit()                              

    @classmethod
    async def select_all(cls, ) -> List[UserAccount]:
        async with get_async_session_context() as session:
            result = await session.execute(select(UserAccount))
            user_accounts = result.scalars().all()
            return user_accounts

    @classmethod
    async def select_user_account(cls, id: int = None, account: str = None, email: str = None) -> UserAccount:
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserAccount).where((UserAccount.id == id) | (UserAccount.account == account))
            )
            user_account = result.scalars().first()
            return user_account                  