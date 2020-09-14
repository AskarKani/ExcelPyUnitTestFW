import argparse
import os
import sys
from mytest import mytest



if __name__ == '__main__':
    des = "!........................! Python Unit Test !........................!\n " \
          "\rpython3 run.py -I <include files path> -F <cpp files or function definition> -flags <flags to compile>"
    parser = argparse.ArgumentParser(description=des, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-I', nargs='+', type=str, help='pass the include files as list')
    parser.add_argument('-F', nargs='+', type=str, help='pass the function files as list')
    parser.add_argument('-N', nargs='+', type=str, help='pass the function names as list')
    # parser.add_argument('-flags', nargs='+', type=str, help='pass the flags for compiling as list if any')
    arg = parser.parse_args()

    if not arg.I or not arg.F or not arg.N:
        print("Pass the include files, function definition and paths with respective arguments...")
        print(parser.print_help())
        sys.exit(1)

    for _ in [arg.I, arg.F]:
        for file in _:
            if not os.path.isfile(file):
                print(f"The {file} path is incorrect")
                sys.exit(1)

    test = mytest()
    for include, file in zip(arg.I, arg.F):
        test.compile(include, file)
    for function in arg.N:
        test.test(function)
