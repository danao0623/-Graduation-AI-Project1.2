import asyncio
from read.usecase_read import UseCaseReader  # ← 請確認檔名是 usecase_read.py 而非 usecase_reader.py

async def main():
    try:
        user_input = input("請輸入想查詢的 UseCase ID：")
        use_case_id = int(user_input)
    except ValueError:
        print("❌ 請輸入有效的整數 ID。")
        return

    result = await UseCaseReader.get_use_case_with_actors(use_case_id=use_case_id)

    if result is None:
        print("❌ 查無此 UseCase")
        return

    print(f"\n✅ UseCase：{result['use_case_name']} (ID: {result['use_case_id']})")
    print("關聯的 Actors：")
    if not result["actors"]:
        print("（無關聯）")
    for actor in result["actors"]:
        print(f"- {actor['actor_name']} (ID: {actor['actor_id']})")

if __name__ == "__main__":
    asyncio.run(main())
3