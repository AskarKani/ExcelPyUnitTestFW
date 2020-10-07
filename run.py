#! /usr/bin/python3

import os
import sys
from mytest import Mytest


if __name__ == '__main__':
    des = "!........................! C++ Unit Test !........................!\n " \
          "\rpython3 run.py <excel_sheet_path>"
    print(des)
    if len(sys.argv) < 2:
        print("ERROR: Test cases excel sheet path is missing.\nPass the path as argument")
        exit(1)
    elif len(sys.argv) > 2:
        print("ERROR: Length of arguments are grater than two")
        exit(1)

    test_case_excel = sys.argv[1]

    if not os.path.isfile(test_case_excel):
        print(f"{test_case_excel} path is invalid ...")
        exit(1)

    test = Mytest(test_case_excel)
    test.test()

