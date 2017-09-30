import os
from cement.core.controller import CementBaseController, expose
from app.services.volback_service import Volback
from app.exceptions.volback_exceptions import (
    RepoPathNotFound
)

class RestoreController(CementBaseController):
    class Meta:
        label = 'restore'
        description = 'Restore volume'
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
            (['-t', '--time'], {
                'action': 'store',
                'dest': 'restore_time',
                'help': 'Volback restore time'
            }),
            (['-c', '--containers'], {
                'action': 'store',
                'dest': 'container_ids',
                'help': 'Comma separated list of containers to restore'
            }),
            (['-m', '--mounts'], {
                'action': 'store',
                'dest': 'mount_destinations',
                'help': 'Comma separated list of mount destinations to restore'
            }),
            (['-a', '--all'], {
                'action': 'store_true',
                'dest': 'restore_all',
                'help': 'Restore all containers'
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
        restore_time = os.environ['RESTORE_TIME'] if 'RESTORE_TIME' in os.environ else None
        if pargs.restore_time:
            restore_time = pargs.restore_time
        container_ids = os.environ['CONTAINER_IDS'].split(',') if 'CONTAINER_IDS' in os.environ else None
        if pargs.container_ids:
            container_ids = pargs.container_ids.split(',')
        mount_destinations = os.environ['MOUNT_DESTINATIONS'].split(',') if 'MOUNT_DESTINATIONS' in os.environ else None
        if pargs.mount_destinations:
            mount_destinations = pargs.mount_destinations.split(',')
        restore_all = os.environ['RESTORE_ALL'] if 'RESTORE_ALL' in os.environ else None
        if pargs.verbose:
            restore_all = pargs.restore_all
        verbose = os.environ['VERBOSE'] if 'VERBOSE' in os.environ else None
        if pargs.verbose:
            verbose = pargs.verbose
        volback = Volback(repo, passphrase=passphrase, verbose=verbose)
        volback.restore(
            container_ids=container_ids,
            mount_destinations=mount_destinations,
            restore_time=restore_time,
            restore_all=restore_all
        )
