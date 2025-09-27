import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.actors_controller import ActorController 
import asyncio
import json

async def main():
    actors = await ActorController.select_all()
    for actor in actors:
        data = {
            "id": actor.id,
            "name": actor.name,
            "actor_id": actor.actor_id,
            "use_case_actors": [
                {
                    "use_case_id": uca.use_case_id,
                    "actor_id": uca.actor_id
                }
                for uca in actor.use_case_actors
            ]
        }
        print(json.dumps(data, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())