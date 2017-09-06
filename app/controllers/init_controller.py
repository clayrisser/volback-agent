from cement.core.controller import CementBaseController, expose
from app.services.borg_service import Borg

class InitController(CementBaseController):
    class Meta:
        label = 'init'
        description = 'Init borg repo'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['extra_arguments'], {
                'action': 'store',
                'nargs': '*',
                'help': 'Borg repo path'
            })
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if len(pargs.extra_arguments) <= 0:
            exit('Missing borg repo')
        return Borg.init(pargs.extra_arguments[0])
