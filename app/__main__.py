from cement.core.foundation import CementApp
from config import NAME, BANNER
from controllers import (
    BackupController,
    BaseController
)

class App(CementApp):
    class Meta:
        label = NAME
        base_controller = BaseController
        handlers = [
            BackupController
        ]

def main():
    with App() as app:
        print(BANNER)
        app.run()

if __name__ == '__main__':
    main()
