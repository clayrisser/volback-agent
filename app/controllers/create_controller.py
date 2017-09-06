import os
from cement.core.controller import CementBaseController, expose
from app.services.borg_service import Borg

class CreateController(CementBaseController):
    class Meta:
        label = 'create'
        description = 'Create borg repo'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-p', '--path'], {
                'action': 'store',
                'dest': 'repo_path',
                'help': 'Borg repo path'
            }),
            (['-n', '--name'], {
                'action': 'store',
                'dest': 'backup_name',
                'help': 'Name of borg backup'
            }),
            (['-v', '--verbose'], {
                'action': 'store_true',
                'dest': 'verbose',
                'help': 'Verbose output'
            }),
            (['extra_arguments'], {
                'action': 'store',
                'nargs': '*',
                'help': 'Location to backup'
            })
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        repo_path = None
        if pargs.repo_path:
            repo_path = pargs.repo_path
        elif 'BORG_REPO' in os.environ:
            repo_path = os.environ['BORG_REPO']
        else:
            exit('Missing repo path')
        borg = Borg(repo_path, verbose=pargs.verbose)
        return borg.create(pargs.extra_arguments[0], pargs.backup_name)
