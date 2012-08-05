import time
import sys
import subprocess
import simpleregister

def main():
    f = open("secret.txt")
    p = subprocess.Popen(["plink.exe", "-L", "5432:mimer.teknolog.fi:5432",
        "*username*@mimer.teknolog.fi"], stdin=f)
    return simpleregister.main()
    p.terminate()

if __name__ == "__main__":
    sys.exit(main())
