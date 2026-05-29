import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "puter_bridge",
    path=os.path.dirname(os.path.abspath(__file__))
)

def puter_bridge(messages=None, tools=None, model="gpt-4o-mini", request_id=None, command=None, key=None):
    """
    Puter Bridge that handles Google Login and AI Requests.
    """
    component_value = _component_func(
        messages=messages,
        tools=tools,
        model=model,
        request_id=request_id,
        command=command,
        key=key,
        default=None
    )
    return component_value
