import start


def test_mainloop():
    loop = start.LoopState()
    loop.loop_once()


def test_main():
    start.main()