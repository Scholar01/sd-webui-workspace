import json
import os.path
from dataclasses import dataclass, field
from modules.ui import paste_symbol, save_style_symbol
from modules.ui_components import ToolButton
from modules.scripts import basedir
from .util import *


@dataclass
class StableDiffusionWorkSpace:
    blocks: gr.Blocks = field(default_factory=gr.Blocks, repr=False)
    tabs: list[gr.Tab] = field(default_factory=list, repr=False)
    components: list[gr.components.IOComponent] = field(default_factory=list, repr=False)
    filename: str = field(default=os.path.join(basedir(), 'workspace.json'))

    def setup_components(self, blocks):
        """
        当ui组件加载完成之后, 建立需要的事件关联
        """
        self.blocks = blocks
        self.tabs = get_tabs(blocks)
        self.components.clear()

        ids = []
        for tab in self.tabs:
            ids.extend(get_all_elem_id(tab))

        components = self.blocks.blocks.values()
        self.components = [c for c in components if c.elem_id in ids]
        # self.components_dict = {c.elem_id: c for c in components if c.elem_id in ids}
        # self.components = list(self.components_dict.values())

    def setup_ui(self):
        """
        初始化ui
        """
        if self.blocks is None or self.blocks.blocks == {}:
            return

        quick_settings: gr.Row = list(self.blocks.blocks.values())[0]
        assert quick_settings.elem_id == 'quicksettings'

        quick_settings.parent.__enter__()

        btn_import = ToolButton(value=paste_symbol, elem_id=self.elem_id('import'), tooltip='import workspace')
        btn_save = ToolButton(value=save_style_symbol, elem_id=self.elem_id('save'), tooltip='save workspace')

        quick_settings.add_child(btn_import)
        quick_settings.add_child(btn_save)
        btn_save.click(fn=self.on_save, inputs=self.components, outputs=None)
        btn_import.click(fn=self.on_load, inputs=None, outputs=self.components)
        quick_settings.parent.__exit__()

    def elem_id(self, elem_id):
        return f'workflow_{elem_id}'

    def on_save(self, *args):
        result = {}
        for i, arg in enumerate(args):
            component = self.components[i]
            value = component_to_value(component, arg)
            result[component.elem_id] = {
                'elem_type': str(component),
                'value': value
            }

        js = json.dumps(result, indent=4)
        with open(self.filename, 'w', encoding='utf8') as f:
            f.write(js)
        print('save workspace success')

    def on_load(self):
        result = []
        if not os.path.exists(self.filename):
            result = [gr.update() for g in range(len(self.components))]
        else:
            workflows = json.load(open(self.filename, encoding='utf8'))
            for component in self.components:
                if component.elem_id in workflows:
                    flow = workflows[component.elem_id]
                    value = flow_to_component(flow)
                    result.append(gr.update(value=value))
                else:
                    result.append(gr.update())
        return result
