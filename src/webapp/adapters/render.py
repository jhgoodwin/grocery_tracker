from functools import wraps
from fastapi import Request
from fastapi.templating import Jinja2Templates

class RenderDecorator:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def __call__(self, template_name: str):
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                data = await func(request, *args, **kwargs)
                if request.headers.get("HX-Request") == "true":
                    return self.templates.TemplateResponse(request, template_name, {"request": request, **data})
                return data
            return wrapper
        return decorator
