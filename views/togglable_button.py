import asyncio
from typing import Any, Callable, Optional

from nicegui.events import ClickEventArguments, handle_event
from nicegui.elements.mixins.color_elements import BackgroundColorElement
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

class TogglableButton(TextElement, DisableableElement, BackgroundColorElement, ValueElement):
    def __init__(self, 
                 text: str = '', *, 
                 value: bool = True,
                 on_click: Optional[Callable[..., Any]] = None, 
                 on_value_change: Optional[Callable[..., Any]] = None,
                 true_color: Optional[str] = None,
                 false_color: Optional[str] = None,
                 true_icon: Optional[str] = None,
                 false_icon: Optional[str] = None,
                 ) -> None:

        super().__init__(tag='q-btn',
                         text=text, value=value, background_color=true_color, on_value_change=on_value_change)

        if true_color:
            self._props['true_color'] = true_color
        if false_color:
            self._props['false_color'] = false_color
        if true_icon:
            self._props['true_icon'] = true_icon
        if false_icon:
            self._props['false_icon'] = false_icon
        
        self.callback = on_click

        def handle_click(e: ClickEventArguments) -> None:
            handle_event(self.callback, ClickEventArguments(sender=self, client=self.client))
            
            self.value = not self.value
            if self.value:
                self._props['color'] =  self._props['true_color'] if 'true_color' in self._props else 'primary'
                self._props['icon'] = self._props['true_icon'] if 'true_icon' in self._props else None
            else:
                self._props['color'] =  self._props['false_color'] if 'false_color' in self._props else 'primary'
                self._props['icon'] = self._props['false_icon'] if 'false_icon' in self._props else None
        
        self.on('click', handle_click, [])    
        self._update()

    def _update(self):
        if self.value:
            self._props['color'] =  self._props['true_color'] if 'true_color' in self._props else 'primary'
            self._props['icon'] = self._props['true_icon'] if 'true_icon' in self._props else None
        else:
            self._props['color'] =  self._props['false_color'] if 'false_color' in self._props else 'primary'
            self._props['icon'] = self._props['false_icon'] if 'false_icon' in self._props else None

    def _text_to_model_text(self, text: str) -> None:
        self._props['label'] = text

    async def clicked(self) -> None:
        """Wait until the button is clicked."""
        event = asyncio.Event()
        self.on('click', event.set, [])
        await self.client.connected()
        await event.wait()
