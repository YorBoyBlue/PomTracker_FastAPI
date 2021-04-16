from fastapi.templating import Jinja2Templates


class TemplateManager:
    templates: Jinja2Templates

    def __init__(self):
        self.templates = Jinja2Templates(directory="pom_tracker/views")

    def get(self):
        return self.templates


tm = TemplateManager()
