from __future__ import annotations

from typing import Any, Callable, Optional, Union

from nicegui.binding import BindableProperty
from nicegui.elements.tabs import Tabs, Tab, TabPanel
from nicegui.events import ClickEventArguments, ValueChangeEventArguments, handle_event

class TogglableTabs(Tabs):
    SWITCH_PROP: str = 'model-switch'
    switch = BindableProperty(on_change=lambda sender, value: sender._on_switch_change(value))

    def __init__(self, *,
                 value: Union[TogglableTab, TabPanel, None] = None,
                 on_change: Optional[Callable[..., Any]] = None,
                 on_switch_change: Optional[Callable[..., Any]] = None,
                 switch: bool = True) -> None:

        super().__init__(value=value, on_change=on_change)
       
        self.switch = switch
        self._props[self.SWITCH_PROP] = self._switch_to_model_switch(switch)
        self._switch_change_handlers = on_switch_change
        self._current_tab = value

    def _on_switch_change(self, switch: bool) -> None:
        args = ValueChangeEventArguments(sender=self, client=self.client, value=switch)
        handle_event(self._switch_change_handlers, args)
    
    def _switch_to_model_switch(self, switch: bool) -> Any:
        return switch    

class TogglableTab(Tab):
    def __init__(self, 
                 name: str, 
                 label: Optional[str] = None, 
                 icon: Optional[str] = None,
                 on_click: Optional[Callable[..., Any]] = None
                 ) -> None:
        
        super().__init__(name=name, label=label, icon=icon)       
        self.callback = on_click

        def handle_click(e: ClickEventArguments) -> None:
            handle_event(self.callback, ClickEventArguments(sender=self, client=self.client))
            if self.tabs._current_tab == self._props['name']:
                self.tabs.switch = not self.tabs.switch
            else:
                self.tabs.switch = True
            self.tabs._current_tab = self._props['name']               
        
        self.on('click', handle_click, [])


