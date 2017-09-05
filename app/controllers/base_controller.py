from cement.core.controller import CementBaseController, expose

class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'A foundation made with cement'

    @expose(hide=True)
    def default(self):
        return
