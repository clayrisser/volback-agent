import os
from cement.core.controller import CementBaseController, expose
from app.services.volback_service import Volback
from app.exceptions.volback_exceptions import (
    RepoPathNotFound
)

class BackupController(CementBaseController):
    class Meta:
        label = 'backup'
        description = 'Backup volume'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-r', '--repo'], {
                'action': 'store',
                'dest': 'repo',
                'help': 'Volback repo path'
            }),
            (['-p', '--passphrase'], {
                'action': 'store',
                'dest': 'passphrase',
                'help': 'Volback encryption passphrase'
            }),
            (['-c', '--containers'], {
                'action': 'store',
                'dest': 'container_ids',
                'help': 'Comma separated list of containers to backup'
            }),
            (['-m', '--mounts'], {
                'action': 'store',
                'dest': 'mount_destinations',
                'help': 'Comma separated list of mount destinations to backup'
            }),
            (['-v', '--verbose'], {
                'action': 'store_true',
                'dest': 'verbose',
                'help': 'Verbose output'
            })
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        repo = os.environ['REPO'] if 'REPO' in os.environ else None
        if pargs.repo:
            repo = pargs.repo
        if not repo:
            raise RepoPathNotFound()
        passphrase = os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else None
        if pargs.passphrase:
            passphrase = pargs.passphrase
        container_ids = os.environ['CONTAINER_IDS'].split(',') if 'CONTAINER_IDS' in os.environ else None
        if pargs.container_ids:
            container_ids = pargs.container_ids.split(',')
        mount_destinations = os.environ['MOUNT_DESTINATIONS'].split(',') if 'MOUNT_DESTINATIONS' in os.environ else None
        if pargs.mount_destinations:
            mount_destinations = pargs.mount_destinations.split(',')
        verbose = os.environ['VERBOSE'] if 'VERBOSE' in os.environ else None
        if pargs.verbose:
            verbose = pargs.verbose
        volback = Volback(repo, passphrase=passphrase, verbose=verbose)
        volback.backup(
            container_ids=container_ids,
            mount_destinations=mount_destinations
        )
