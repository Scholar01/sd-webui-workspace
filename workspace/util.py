from itertools import chain

import PIL.Image
import base64
import gradio as gr
import numpy as np
from modules import ui_components
from pandas import DataFrame

exclude_tabs = [
    'tab_settings',
    'tab_extensions',
]

exclude_components = [
    gr.Tab,
    gr.Row,
    gr.Column,
    gr.Group,
    gr.Blocks,
    gr.Accordion,
    gr.Tabs,
    gr.TabItem,
    gr.Box,
    gr.Button,
    ui_components.FormRow,
    ui_components.FormColumn,
    ui_components.FormGroup,
    ui_components.ToolButton,
]


def get_tabs(blocks):
    tabs = []
    for key, block in blocks.blocks.items():
        if hasattr(block, "elem_id") \
                and block.elem_id \
                and block.elem_id.startswith("tab_") \
                and block.elem_id not in exclude_tabs:
            tabs.append(block)
    return tabs


def get_all_elem_id(component):
    elem_ids = []
    if getattr(component, 'elem_id', None) is not None:
        # 判断是否在exclude_components中
        if not any([isinstance(component, c) for c in exclude_components]):
            elem_ids.append(component.elem_id)
    if hasattr(component, 'children'):
        elem_ids.extend(chain(*[get_all_elem_id(c) for c in component.children]))
    return elem_ids


def parse_image(component, value):
    if not value:
        return value
    if component.tool == 'editor':
        image = value
    else:
        image = value.get('image', None)
    mode = 'RGB'
    if component.type == 'numpy':
        image = PIL.Image.fromarray(image)
        width = image.width
        height = image.height
        mode = image.mode
        data = base64.b64encode(image.tobytes()).decode('utf-8')
        # width = image.shape[1]
        # height = image.shape[0]
        # data = base64.b64encode(image.tobytes()).decode('utf-8')

    elif component.type == 'pil':
        width = image.width
        height = image.height
        mode = image.mode
        data = base64.b64encode(image.tobytes()).decode('utf-8')

    else:
        width = 0
        height = 0
        data = value

    return {
        'width': width,
        'height': height,
        'type': component.type,
        'mode': mode,
        'data': data,
    }


def to_image(value):
    if not value:
        return value
    type = value.get('type', None)
    image = value.get('data', None)
    width = value.get('width', 0)
    height = value.get('height', 0)
    mode = value.get('mode', 'RGB')
    if type == 'numpy' or type == 'pil':
        image = base64.b64decode(image)
        image = PIL.Image.frombytes(mode, (width, height), image)
        if type == 'numpy':
            image = np.asarray(image)

    return image


def component_to_value(component, value):
    if isinstance(value, DataFrame):
        return value.to_dict()

    if isinstance(component, gr.Image):
        value = parse_image(component, value)

    if isinstance(component, gr.Dropdown):
        if component.type == 'index':
            value = component.choices[value]

    if isinstance(component, gr.Radio):
        if component.type == 'index':
            value = component.choices[value][-1]

    return value


def flow_to_component(flow):
    value = flow['value']
    elem_type = flow['elem_type']

    if elem_type == 'dataframe':
        value = DataFrame.from_dict(value)

    if elem_type == 'image' and value:
        value = to_image(value)

    if elem_type == 'gallery' and value:
        if isinstance(value, list):
            value = [v['name'] for v in value]

    return value
