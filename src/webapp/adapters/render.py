from functools import wraps
from datetime import datetime
from fastapi import Request
from fastapi.templating import Jinja2Templates

class RenderDecorator:
    def __init__(self, templates_dir: str):
        self.templates = Jinja2Templates(directory=templates_dir)

    def __call__(self, template_name: str, *, always: bool = False):
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                data = await func(request, *args, **kwargs)
                if not isinstance(data, dict):
                    data = {}
                data["request"] = request
                data["now"] = lambda: datetime.now()
                if always or request.headers.get("HX-Request") == "true":
                    return self.templates.TemplateResponse(request, template_name, data)
                return data
            return wrapper
        return decorator
