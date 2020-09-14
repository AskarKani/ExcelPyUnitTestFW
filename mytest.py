import os
import subprocess
import cppyy
import openpyxl
from pathlib import Path

class mytest:
    def __init__(self):
        self.unit_test_out = Path(os.getcwd()) / "unit_test_out"
        self.test_cases_out = Path(os.getcwd()) / "unit_test_cases"
        if not os.path.isdir(self.unit_test_out):
            os.mkdir(self.unit_test_out)
        if not os.path.isdir(self.test_cases_out):
            os.mkdir(self.test_cases_out)
        self.my_cppyy = cppyy
        self.flags = ""

    def terminal_exec(self, cmd):
        try:
            outstr = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, check=True)
            logdata = outstr.stdout.decode()
            return logdata
        except subprocess.CalledProcessError as e:
            logdata = "\n\nError:\n" + e.stdout.decode('utf-8')
            return logdata

    def check_is_file(self, file_path):
        if os.path.isfile(file_path):
            return True
        else:
            return False

    # g++ -fpic -c add.cpp
    # g++ -shared -o libadd.so add.o
    def compile(self, include_path, cpp_path):
        if not self.check_is_file(cpp_path):
            print(f"{cpp_path} is invalid")
            exit(1)
        if not self.check_is_file(include_path):
            print(f"{include_path} is invalid")
            exit(1)
        file_cpp_name = os.path.splitext(os.path.basename(cpp_path))[0]
        out_cpp_path = self.unit_test_out / file_cpp_name
        lib_name = "lib" + file_cpp_name + ".so"
        lib_out_path = self.unit_test_out / lib_name
        self.terminal_exec(f"g++ -fpic -c {cpp_path} -o {out_cpp_path} {self.flags}")
        self.terminal_exec(f"g++ -shared -o {lib_out_path} {out_cpp_path} {self.flags}")
        self.my_cppyy.include(include_path)
        self.my_cppyy.load_library(str(lib_out_path))
        cppyy.add_include_path("/home/askar/my_projects/test_cpp/unit_test/")

    def test_result(self, excel_name):
        excel_path = self.test_cases_out / excel_name
        if os.path.isfile(excel_path):
            book = openpyxl.load_workbook(excel_path, read_only=False)
        else:
            print("TEST cases excel sheet is missing...")
            exit(1)
        return book, excel_path

    def test(self, func_name):
        book, excel_path = self.test_result(f"{func_name}.xlsx")
        print(f"Executing unit test for function : {func_name}")
        sheet = book.active
        column = sheet.max_column
        expected_result_col = 0

        for i in range(1, column + 1):
            cell_value = sheet.cell(row=1, column=i).value
            if cell_value == "Expected Result":
                expected_result_col = i
        result_obtained_col = expected_result_col + 1
        result_col = expected_result_col + 2

        pass_count = fail_count = 0
        greenFill = openpyxl.styles.PatternFill(start_color='FF00FF00',
                                                end_color='FF00FF00',
                                                fill_type='solid')
        redFill = openpyxl.styles.PatternFill(start_color='FFFF0000',
                                              end_color='FFFF0000',
                                              fill_type='solid')
        for j in range(2, sheet.max_row + 1):
            test_params = []
            for i in range(2, expected_result_col):
                test_params.append(sheet.cell(row=j, column=i).value)
            expected_result = sheet.cell(row=j, column=expected_result_col).value

            temp_func = f"locals()['temp']=self.my_cppyy.gbl.{func_name}("
            for i in test_params:
                try:
                    int(i)
                    temp_func += str(i) + ","
                except ValueError:
                    temp_func += "\"" + str(i) + "\"" + ","
            func = temp_func + ")"
            exec(func)
            result_obtained = locals()['temp']
            sheet.cell(row=j, column=result_obtained_col).value = result_obtained
            if expected_result == result_obtained:
                result = "PASS"
                pass_count = pass_count + 1
                sheet.cell(row=j, column=result_col).fill = greenFill
            else:
                result = "FAIL"
                fail_count = fail_count + 1
                sheet.cell(row=j, column=result_col).fill = redFill
            sheet.cell(row=j, column=result_col).value = result
        book.save(excel_path)
        print(f"Total test cases executed : {sheet.max_row - 1}")
        print(f"Total PASS : {pass_count}")
        print(f"Total FAIL : {fail_count}")
        print()
