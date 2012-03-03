"""Mr. Repo - A simple repo management system"""
from mr_repo.version import version

if __name__ == '__main__':
    from mr_repo.repossesser import Repossesser
    from sys import argv
    import re
    prog = "mr_repo"
    if (len(argv) > 0):
        prog = argv.pop(0)
        # If prog does not look something like Mr. Repo then change it
        if None == re.search('mr(\.|)([-_ ]{0,2})repo', prog,
                flags=re.IGNORECASE):
            prog = "mr_repo"
    #Create an instance of MrRepo
    repossesser = Repossesser(prog=prog, args=argv, execute=True, one_use=True)
