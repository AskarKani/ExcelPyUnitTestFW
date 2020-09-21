import os
import subprocess
import cppyy
import shutil
import openpyxl
from pathlib import Path

class mytest:
    def __init__(self, excel_path):
        self.unit_test_out = Path(os.getcwd()) / "unit_test_out"
        if not os.path.isdir(self.unit_test_out):
            os.mkdir(self.unit_test_out)
        self.my_cppyy = cppyy
        self.excel_path = excel_path
        self.flags = ""

    def terminal_exec(self, cmd):
        try:
            outstr = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, check=True)
            logdata = outstr.stdout.decode()
            return logdata
        except subprocess.CalledProcessError as e:
            logdata = "\n\nError:\n" + e.stdout.decode('utf-8')
            return logdata

    def check_path(self, header, path):
        if (not path) or (not os.path.isfile(path)):
            print(f"{header}:{path} is incorrect...")
            exit(1)

    def read_excel(self):
        self.book = openpyxl.load_workbook(self.excel_path, read_only=False)
        self.sheet = self.book.active
        self.include_file = self.sheet['B1'].value
        self.check_path("$INC_FILE", self.include_file)
        self.func_file = self.sheet['B2'].value
        self.check_path("$FUNC_FILE", self.func_file)
        self.include_path_gcc = self.sheet['B3'].value
        self.flags_gcc = self.sheet['B4'].value
        if not self.flags_gcc:
            self.flags_gcc = ""
        self.func_name = self.sheet['B5'].value
        if not self.func_name:
            print(f"enter func_name..")
            exit(1)

    # g++ -fpic -c add.cpp
    # g++ -shared -o libadd.so add.o
    def compile(self):
        file_cpp_name = os.path.splitext(os.path.basename(self.func_file))[0]
        out_cpp_path = self.unit_test_out / file_cpp_name
        lib_name = "lib" + file_cpp_name + ".so"
        lib_out_path = self.unit_test_out / lib_name
        if self.include_path_gcc:
            self.terminal_exec(f"g++ -fpic -c {self.func_file} -o {out_cpp_path} {self.flags_gcc} -I {self.include_path_gcc}")
            self.terminal_exec(f"g++ -shared -o {lib_out_path} {out_cpp_path} {self.flags_gcc} -I {self.include_path_gcc}")
        else:
            self.terminal_exec(f"g++ -fpic -c {self.func_file} -o {out_cpp_path} {self.flags_gcc}")
            self.terminal_exec(f"g++ -shared -o {lib_out_path} {out_cpp_path} {self.flags_gcc}")
        self.my_cppyy.include(self.include_file)
        try:
            self.my_cppyy.load_library(str(lib_out_path))
        except RuntimeError:
            print("ERROR : Library path is missing or error in compilation..")
            exit(1)

    def clean(self):
        if os.path.isdir(self.unit_test_out):
            shutil.rmtree(self.unit_test_out)

    def test(self):
        self.read_excel()
        self.compile()
        print(f"Executing unit test for function : {self.func_name}")
        column = self.sheet.max_column
        expected_result_col = 0

        for i in range(2, column + 1):
            cell_value = self.sheet.cell(row=6, column=i).value
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
        for j in range(7, self.sheet.max_row + 1):
            test_params = []
            for i in range(2, expected_result_col):
                test_params.append(self.sheet.cell(row=j, column=i).value)
            expected_result = self.sheet.cell(row=j, column=expected_result_col).value

            temp_func = f"locals()['temp']=self.my_cppyy.gbl.{self.func_name}("
            for i in test_params:
                try:
                    int(i)
                    temp_func += str(i) + ","
                except ValueError:
                    temp_func += "\"" + str(i) + "\"" + ","
            func = temp_func + ")"
            exec(func)
            result_obtained = locals()['temp']
            self.sheet.cell(row=j, column=result_obtained_col).value = result_obtained
            if expected_result == result_obtained:
                result = "PASS"
                pass_count = pass_count + 1
                self.sheet.cell(row=j, column=result_col).fill = greenFill
            else:
                result = "FAIL"
                fail_count = fail_count + 1
                self.sheet.cell(row=j, column=result_col).fill = redFill
            self.sheet.cell(row=j, column=result_col).value = result
        self.book.save(self.excel_path)
        print(f"Total test cases executed : {self.sheet.max_row - 1}")
        print(f"Total PASS : {pass_count}")
        print(f"Total FAIL : {fail_count}")
        print()
        self.clean()
        