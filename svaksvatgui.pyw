import time
import sys
import subprocess
import svaksvatgui

def main():
    f = open("secret.txt")
    p = subprocess.Popen(["plink.exe", "-L", "5432:mimer.teknolog.fi:5432",
        "*username*@mimer.teknolog.fi"], stdin=f)
    return svaksvatgui.main()
    p.terminate()

if __name__ == "__main__":
    sys.exit(main())
