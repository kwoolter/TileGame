import logging
import controller


def main():

    logging.basicConfig(level = logging.WARN)

    c = controller.Controller()
    c.run()

    return

if __name__ == "__main__":
    main()
    exit(0)