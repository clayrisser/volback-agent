from cement.core.foundation import CementApp
from config import NAME, BANNER
from controllers import (
    BackupController,
    BaseController,
    RestoreController
)

class App(CementApp):
    class Meta:
        label = NAME
        base_controller = BaseController
        handlers = [
            BackupController,
            RestoreController
        ]

def main():
    with App() as app:
        print(BANNER)
        try:
            app.run()
        except BaseException as e:
            if not hasattr(e, 'known') or not e.known:
                raise e
            if not hasattr(e, 'level'):
                return app.log.error(e.message + '\n')
            if e.level == 'warning':
                return app.log.warning(e.message + '\n')
            return app.log.error(e.message + '\n')

if __name__ == '__main__':
    main()
