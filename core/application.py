from nicegui import app
from core.environment import Environment
from core.database import Database
from core.logger import AbstractLogger

class Application:  
    @staticmethod
    def initialize():
        Environment.initialize()

        async def handle_startup():
            try:
                await Database.initialize()
            except Exception as e:      
                logger: AbstractLogger = Environment.logger("SYSTEM")
                logger.error(f"Failed to initialize application: {e}".replace("\n", ""))    

        async def handle_shutdown():
            await Database.dispose_engine()

        app.on_startup(handle_startup)
        app.on_shutdown(handle_shutdown)
        
