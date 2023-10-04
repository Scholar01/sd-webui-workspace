import gradio as gr
from fastapi import FastAPI
from modules import script_callbacks
from .workspace import StableDiffusionWorkSpace

sd_workflow = StableDiffusionWorkSpace()


def on_app_started(blocks: gr.Blocks, app: FastAPI):
    sd_workflow.setup_components(blocks)
    sd_workflow.setup_ui()


script_callbacks.on_app_started(on_app_started)
