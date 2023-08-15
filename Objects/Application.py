from Dagger   import *
from Navigator import *
from Parser    import *
from Utilities import *

def main():

    files  = Utility()
    parser = Parser(files())
    dag    = Dagger(files, parser)()
    Navigator(dag[1][1]['parser'], dag[1][1]['parser'], [(0, 41), (0, 41)])()


if __name__ == "__main__":
    main()