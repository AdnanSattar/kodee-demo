import importlib
import inspect
import os
import sys
from typing import Any, Dict, List

from app.utils.logger.logger import Logger

logger = Logger()


async def compile_function_metadata(current_handler_dir: str) -> List[Dict[str, Any]]:
    tools = []
    functions_dir = os.path.join(current_handler_dir, "functions")

    if not os.path.isdir(functions_dir):
        logger.log(f"Functions directory not found: {functions_dir}")
        return tools

    added_path = False
    if functions_dir not in sys.path:
        sys.path.insert(0, functions_dir)
        added_path = True

    function_files = [
        f[:-3]
        for f in os.listdir(functions_dir)
        if f.endswith(".py") and not f.startswith("__")
    ]

    for module_name in function_files:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if hasattr(obj, "meta"):
                for meta_info in obj.meta:
                    tools.append({"type": "function", "function": meta_info})

    if added_path:
        try:
            sys.path.remove(functions_dir)
        except ValueError:
            pass

    return tools


async def compile_function_map(current_handler_dir: str) -> Dict[str, Any]:
    function_map = {}
    functions_dir = os.path.join(current_handler_dir, "functions")

    if not os.path.isdir(functions_dir):
        logger.log(f"Functions directory not found: {functions_dir}")
        return function_map

    added_path = False
    if functions_dir not in sys.path:
        sys.path.insert(0, functions_dir)
        added_path = True

    function_files = [
        f[:-3]
        for f in os.listdir(functions_dir)
        if f.endswith(".py") and not f.startswith("__")
    ]

    for module_name in function_files:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if hasattr(obj, "meta"):
                function_map[name] = obj

    if added_path:
        try:
            sys.path.remove(functions_dir)
        except ValueError:
            pass

    return function_map
