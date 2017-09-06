from cement.core.foundation import CementApp
from config import NAME, BANNER
from controllers import (
    BaseController,
    CreateController,
    InitController,
    CleanController
)

class App(CementApp):
    class Meta:
        label = NAME
        base_controller = BaseController
        handlers = [
            CleanController,
            CreateController,
            InitController
        ]

def main():
    with App() as app:
        print(BANNER)
        app.run()

if __name__ == '__main__':
    main()
