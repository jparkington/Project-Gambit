from Dagger   import *
from Navigator import *
from Parser    import *
from Utilities import *

def main():

    files  = Utility()
    parser = Parser(files())
    dag    = Dagger(files, parser)()
    Navigator(parser, dag[0], dag[1])()

if __name__ == "__main__":
    main()