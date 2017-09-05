from cement.core.controller import CementBaseController, expose
from app.services import clean_service

class CleanController(CementBaseController):
    class Meta:
        label = 'clean'
        description = 'Clean dotfiles'
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        return clean_service.clean()
