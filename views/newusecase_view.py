from nicegui import ui,app
import os
import json
from agents.ai_usecase_actor import ProjectAgent
from agents.ai_usecase_list import UseCaseListAgent
from controllers.actors_controller import ActorController
from controllers.usecase_controller import UseCaseController
from agents.ai_usecase_detail import UseCaseDetail
from views.usecacedetail_view import UseCaseDetailView
from controllers.usecase_actor_controller import UseCaseActorController


class UseCaseView:
    def __init__(self, project_view=None):
        self.actor_grid = None
        self.uc_grid = None
        self.tree_nodes = []
        self.actors = []
        self.usecases = []
        self.ticked_nodes = []
        self.actorstree = []
        self.use_cases = []
        self.maincolum = None
        self.rightcolumn = None
        self.usecasedetail_view = UseCaseDetailView()
        self.project_view  = project_view


    async def display(self) :
        project_id = app.storage.user.get('selected_project',{}).get('id')
        if project_id:
            actors = await ActorController.get_actors_by_project(project_id)
            self.actors = [{'name': actor.name} for actor in actors]
        with ui.column().classes('w-full items-center p-4 gap-4') as maincolum:
            self.maincolum = maincolum

            ui.label('使用案例管理').classes('text-xl font-bold')
            with ui.row().classes('w-full gap-4'):
                with ui.column().classes('w-full'):
                    ui.label('Actors').classes('text-lg font-bold')
                    self.actor_grid = ui.aggrid(options={
                       'columnDefs': [
                            {'headerName': '名稱', 'field': 'name', 'flex': 1}
                        ],
                        'rowData': [{'name': actor['name']}for actor in self.actors],
                        'rowSelection': 'single'
                    }).classes('w-full h-48')
                    self.actor_grid.on('selectionChanged', self.on_actor_selected)

                with ui.column().classes('w-full'):
                    ui.label('Use Case').classes('text-lg font-bold')
                    self.uc_grid = ui.aggrid(options={
                        'columnDefs': [
                            {'headerName': '使用案例名稱', 'field': 'use_case_name', 'flex': 1},
                            {'headerName': '描述', 'field': 'description', 'flex': 2}
                        ],
                        'rowData': [],
                    }).classes('w-full h-64')
                    ui.button('產生usecasedetail', on_click= self.generate_usecase_detail).classes('bg-blue-500 text-white px-4 py-2')
    
    async def display_ai(self):
        with ui.column().classes('w-full items-center p-4 gap-4') as rightcolumn:
            self.rightcolumn = rightcolumn     
            ui.label('AI 模型').classes('text-lg font-bold px-4 py-2')
            with ui.row().classes('gap-4'):
                ui.button('生成 Actor和Usecase',on_click=self.actorsandusecaseai).classes('bg-blue-500 text-white px-4 py-2')
                ui.button('匯入', on_click=self.update_tree).classes('bg-blue-500 text-white px-4 py-2')          

    async def on_actor_selected(self, event):
        selected_rows = await event.sender.get_selected_rows()
        if selected_rows:
            actor_name = selected_rows[0]['name']
            filtered = await self.filter_usecases_for_actor(actor_name)
            print(filtered)
            self.uc_grid.options['rowData'] = filtered
            self.uc_grid.update() 
    
    async def filter_usecases_for_actor(self, actor_name):
        # 根據選擇的 Actor 名稱過濾 Use Cases
        db_usecases = await UseCaseController.get_use_case_by_project(
            app.storage.user.get('selected_project', {}).get('id')
        )
        if db_usecases:
            filtered = []
            for use_case in db_usecases:
                # use_case.actors 是 UseCaseActor 物件的 list
                actor_names = [uca.actor.name for uca in use_case.actors if uca.actor]
                if actor_name in actor_names:
                    filtered.append({
                        "use_case_name": use_case.name,
                        "description": use_case.description,
                        "actor": actor_name
                    })
            return filtered

    async def actorsandusecaseai(self):
        project_name = app.storage.user.get('selected_project',{}).get('name')
        if not project_name:
            ui.notify("not found")
            return
        try:
            ui.notify(f'正在為專案 "{project_name}" 生成 Actor and usecase JSON 字典...', color='blue')
            actor_data = await ProjectAgent.generate_usecase_actors(project_name)
            actors = actor_data.get("use_case_actor",[])
            usecase_data = await UseCaseListAgent.generate_usecase_list(project_name,actors)
            self.actor_grid.options['rowData'] = [{'name': actor['name']} for actor in actors]
            self.usecases = usecase_data.get("use_case_list",[])
            
            ui.notify(f'Actor JSON 字典已生成', color='green')
            data = {
                "actors": actor_data.get("use_case_actor",[]),
                "use_cases": usecase_data.get("use_case_list",[])
            }

            self.actorstree = data.get("actors", [])
            self.use_cases = data.get("use_cases", [])
            print("這是self.actorstree的內容: " + json.dumps(self.actorstree, ensure_ascii=False))
            print("這是self.use_cases的內容: " + json.dumps(self.use_cases, ensure_ascii=False))
            self.tree_nodes.clear() 
            for actor in self.actorstree:
                actor_name = actor["name"]
                children = []

                for uc in self.use_cases:
                    if uc["actor"] == actor_name:
                        children.append({
                            "id": f"{actor_name}_{uc['use_case_name']}",
                            "label": f"{uc['use_case_name']}：{uc['description']}"
                        })

                self.tree_nodes.append({
                    "id": actor_name,
                    "label": actor_name,
                    "children": children
                })

            ui.tree(self.tree_nodes,tick_strategy='leaf',on_tick=lambda e:self.update_ticked(e)).classes('w-full')    

        except Exception as e:
            ui.notify(f'生成失敗：{str(e)}', color='red')    
  
    
    def update_ticked(self,e):
        ticked_items = e.value  # 獲取已勾選的項目
        self.ticked_nodes = ticked_items
        print(f'Ticked items: {ticked_items}') 

    def parse_tick_data(self):
        # 解析已勾選的項目
        actors = {}
        for item in self.ticked_nodes:
            actor, use_case = item.split('_', 1)  # 分割成 Actor 和 Use Case
            if actor not in actors:
                actors[actor] = []
            actors[actor].append({'name': use_case, 'description': f'{actor} 的 {use_case}'})
        return actors

    async def update_tree(self):
        ticked_items = self.ticked_nodes  
        self.uc_grid.clear()
        self.actor_grid.clear()
        print(f'Ticked items: {ticked_items}')

        # 解析勾選的資料，分類為 Actors 和 Use Cases
        structured_data = self.parse_tick_data()
        print(structured_data)

        #根據勾選的資料尋找指定的資料
        selected_actors = set()
        selected_use_cases = []

        for item in ticked_items:
            actor, use_case = item.split('_', 1)
            selected_actors.add(actor)

            # 從 self.use_cases 中尋找匹配的資料
            for uc in self.use_cases:
                if uc["actor"] == actor and uc["use_case_name"] == use_case:
                    selected_use_cases.append(uc)   
                    
        # 從 self.actorstree 中尋找匹配的資料
        matched_actors = [actor for actor in self.actorstree if actor["name"] in selected_actors]     
        # 更新 Actors 資料
        self.usecases = selected_use_cases        

        for actor in matched_actors:
            try:
                project_id = app.storage.user.get('selected_project', {}).get('id')
                await ActorController.add_actor(name=actor["name"],project_id=project_id)
                print(f"Actor {actor['name']} added successfully.")
            except Exception as e:
                print(f"Error adding actor {actor['name']}: {e}")
        
        project_id = app.storage.user.get('selected_project', {}).get('id')
        actors = await ActorController.get_actors_by_project(project_id)
        self.actors = [{'name': actor.name} for actor in actors]
        self.actor_grid.options['rowData'] = self.actors
        self.actor_grid.update() 

        # 打印結果
        print("Matched Actors:")
        print(json.dumps(matched_actors, ensure_ascii=False, indent=4))

        print("Matched Use Cases:")
        print(json.dumps(selected_use_cases, ensure_ascii=False, indent=4)) 
        
        for use_case in selected_use_cases:
            try:
                actor_name = use_case["actor"]
                project_id = app.storage.user.get('selected_project', {}).get('id')
                actors_in_db = await ActorController.get_actors_by_project(project_id)
                actor_obj = next((a for a in actors_in_db if a.name == actor_name), None)

                # 這裡 add_use_case 會回傳已存在的 usecase 或新建的 usecase
                new_use_case = await UseCaseController.add_use_case(
                    name=use_case["use_case_name"],
                    description=use_case["description"],
                    project_id=project_id
                )
                print(f"Use case {use_case['use_case_name']} added or found.")

                # 檢查 usecase 是否已經有這個 actor 關聯
                already_linked = False
                if new_use_case and actor_obj:
                    for uca in new_use_case.actors:
                        if uca.actor_id == actor_obj.id:
                            already_linked = True
                            break

                    if not already_linked:
                        await UseCaseActorController.add_association(
                            use_case_id=new_use_case.id,
                            actors=[{"id": actor_obj.id}]
                        )
                    else:
                        print(f"UseCase '{new_use_case.name}' already linked to actor '{actor_obj.name}'")
            except Exception as e:
                print(f"Error adding use case {use_case['use_case_name']}: {e}")
        
        
        
        SQlite_actor = await ActorController.select_all()
        for u in SQlite_actor:
            print(u.actor_id)
            print(u.name)
        
    async def generate_usecase_detail(self):
        """產生使用案例細節"""
        usecase_detail = UseCaseDetail()

        usecases = []
        for uc in await UseCaseController.get_use_case_by_project(
            app.storage.user.get('selected_project', {}).get('id')):
            actors = [uca.actor.name for uca in uc.actors if uca.actor]
            usecases.append({
                'id': uc.id,
                'use_case_name': uc.name,
                'description': uc.description,
                'actor': actors[0]
            })
            if uc.project_id == app.storage.user.get('selected_project', {}).get('id'):
                if uc.normal_process is None:
                    await usecase_detail.generate(usecase_detail,[usecases[-1]])

        

        self.rightcolumn.clear()
        self.maincolum.clear()
        with self.maincolum:
            await self.usecasedetail_view.display()
        with self.rightcolumn:
            await self.usecasedetail_view.displayrightcolum()
            self.project_view.next_step()




