#!/usr/bin/env python3

if __name__ == '__main__':
    import sys
    from .vmonkey import *

    f=open(sys.argv[1],'r')
    x=f.read()
    f.close()

    r=process_file('','',x, strip_useless=True)

    print(r[0][1])
