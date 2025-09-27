from nicegui import ui,events,app
from controllers.actors_controller import ActorController

class view123:

    def __init__(self):
        self.actorlist = []
        self.row_data = []
        self.master_grid = None
    
    async def display(self):
        ui.label('This is a test view').classes('text-2xl')
        self.actorlist = await ActorController().select_all()
        ui.button('Test Button', on_click= self.on_click ).classes('bg-blue-500 text-white p-2 rounded')
        self.master_grid = ui.aggrid({
                    'columnDefs': [
                        {'headerName': 'id', 'field': 'use_case_name', 'flex': 1},
                        {'headerName': 'name', 'field': 'description', 'flex': 2},
                    ],
                    'rowData':None,
                    'rowSelection': 'single'
        }).classes("w-full h-64")
    
    def on_click(self):
        for actor in self.actorlist:
            print(f"id: {actor.id}, name: {actor.name}")
        self.row_data = [{'use_case_name': actor.name, 'description': actor.id} for actor in self.actorlist]
        self.master_grid.options['rowData'] = self.row_data
        self.master_grid.update()
