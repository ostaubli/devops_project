from typing import Any
import abc
import os
import sys
import re
import subprocess
import importlib
import traceback
import pylint.lint
from mypy import api

IMPORT_PATTERN = re.compile(r"(?:import|from)\s+([a-z0-9_\.]*)")
PYLINT_DISABLE_PATTERN = re.compile(r'#\s*pylint:\sdisable=(.*)')


def get_imported_files(main_file: str, existing_files: list[str]) -> list[str]:
    """
    Recursively get all .py-files which are imported inside the main_file.
    "existing_files" is a list of existing .py files in the project
    """
    with open(main_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    imported_files = []
    for line in lines:
        match = IMPORT_PATTERN.search(line)
        if match:
            rel_file = match.group(1).strip().replace('.', '/') + '.py'
            if rel_file in existing_files:
                imported_files.append(rel_file)
                imported_files.extend(get_imported_files(rel_file, existing_files))
            if rel_file.strip('.py') + '/__init__.py' in existing_files:
                # If theres an init file, all .py-files inside that directory matter
                for dir_file in existing_files:
                    if dir_file.startswith(rel_file.strip('.py')):
                        imported_files.append(dir_file)
                        imported_files.extend(get_imported_files(dir_file, existing_files))
    return imported_files


class Benchmark:

    COLOR_OKAY = '\033[92m'
    COLOR_FAIL = '\033[91m'
    COLOR_ENDC = '\033[0m'
    COLOR_RESULT = '\033[93m'

    def __init__(self, argv: list[str]) -> None:
        self.mode = argv[1]
        if self.mode == 'python':
            self.script = argv[2]
            self.game_server = Python_Game_Server(self.script)
            self.relevant_files = self._get_relevant_files()

    def _get_relevant_files(self) -> list[str]:
        file_name = f"server/py/{self.script.split('.')[0]}.py"
        py_files = []
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file).removeprefix(os.getcwd() + '/'))
        relevant_files = get_imported_files(file_name, py_files)
        relevant_files.remove('server/py/game.py')
        return relevant_files


    def run_tests(self, disable_features: bool = False) -> None:
        os.system('color')

        print('--- Benchmark ---')
        if self.mode == 'python':
            print(f'Mode:   {self.mode}')
            print(f'Script: {self.script}')
        print()

        list_function_name = self.get_list_function_name()

        cnt_tests_valid = 0
        cnt_tests_total = 0
        cnt_points_valid = 0
        cnt_points_total = 0
        for function_name in list_function_name:

            function = getattr(self, function_name)
            id_test = function.__doc__.split(":")[0]
            points = int(function.__doc__.split(" ")[-2][1:])
            description = function.__doc__[len(id_test) + 2:]
            cnt_tests_total += 1
            cnt_points_total += points
            try:
                if disable_features:
                    os.environ["DISABLED_FEATURES"] = function_name
                function()
            except AssertionError as e:
                print(f'{self.COLOR_FAIL}{id_test}{self.COLOR_ENDC}: {description}')
                print(e)
            except Exception:
                print(f'{self.COLOR_FAIL}{id_test}{self.COLOR_ENDC}: {description}')
                print(traceback.format_exc())
            else:
                print(f'{self.COLOR_OKAY}{id_test}{self.COLOR_ENDC}: {description}')
                cnt_tests_valid += 1
                cnt_points_valid += points
            print()

        print(f'{self.COLOR_RESULT}Result{self.COLOR_ENDC}')
        print(f'Tests: {cnt_tests_valid}/{cnt_tests_total} valid', )
        print(f'Mark:  {cnt_points_valid}/{cnt_points_total} points', )
        print()


    def get_list_function_name(self) -> list[str]:
        list_function_name = []
        for attribute in dir(self):
            if attribute.startswith('__'):
                continue
            attribute_value = getattr(self, attribute)
            if callable(attribute_value):
                if attribute.startswith('test_'):
                    list_function_name.append(attribute)

        # sort by number in docstring
        list_function_nr = []
        for function_name in list_function_name:
            function = getattr(self, function_name)
            function_nr = function.__doc__.split(":")[0]
            list_function_nr.append(function_nr)
        list_zipped = zip(list_function_nr, list_function_name)
        list_function_name = [function_name for _, function_name in sorted(list_zipped)]

        return list_function_name


    @staticmethod
    def get_disabled_pylint_checks(file_path: str) -> list[str]:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        disable_comments = []
        for line_nr, line in enumerate(lines, 1):
            match = PYLINT_DISABLE_PATTERN.search(line)
            if match:
                disable_comments.append(
                    f"File {file_path}: You have used '# pylint: disable={', '.join(match.group(1).split())}'"
                    f" on line {line_nr}, nice trick, but that does not count.")
        return disable_comments


    def test_pylint(self) -> None:
        """Test 100: Code style with Pylint [5 point]"""
        og_pipe = sys.stdout # Save original pipeline
        messy_files = []
        for file in [f"server/py/{self.script.split('.')[0]}.py"] + self.relevant_files:
            with open(os.devnull, 'w', encoding="utf-8") as tmp_pipe:
                sys.stdout = tmp_pipe # Pipe stdout to temporary pipeline
                import_string = file.replace('/', '.').strip('.py')
                pylint_score = round(pylint.lint.Run([import_string], exit=False).linter.stats.global_note, 2)
            if pylint_score != 10:
                messy_files.append(f"File {file}: Pylint score {pylint_score:.1f}/10")
            disabled_checks = self.get_disabled_pylint_checks(file)
            if len(disabled_checks) > 0:
                messy_files.extend(disabled_checks)
        sys.stdout = og_pipe # Set stdout pipe back to original
        if len(messy_files) > 0:
            raise AssertionError('\n'.join(messy_files))


    def test_mypy(self) -> None:
        """Test 101: Type checking with MyPy [5 point]"""
        module_name, _ = self.script.split('.')
        result = api.run([f"server/py/{module_name}.py"])
        if result[2] != 0:
            raise AssertionError(f'MyPy exit code is {result[2]}')


    def test_pytest(self) -> None:
        """Test 102: Pytest runs successfully and coverage is >80% [5 point]"""
        module_name, _ = self.script.split('.')
        test_file = f"tests/test_{module_name}.py"
        if not os.path.isfile(test_file):
            raise AssertionError(f"There is no testfile for module '{module_name}' ('{test_file}')")
        result = subprocess.run(["coverage", "run", "-m", "pytest", test_file], capture_output=True, check=False)
        if result.returncode != 0:
            raise AssertionError(f"Pytest exit code is {result.returncode}")
        coverage_result = subprocess.run(
            ["coverage", "report", "--format=total", f"server/py/{module_name}.py"],
            capture_output=True, text=True, check=True)
        if int(coverage_result.stdout) <= 80:
            raise AssertionError(f"Test coverage is too low ({int(coverage_result.stdout)}%)")


class Game_Server(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def reset(self) -> None:
        pass

    @abc.abstractmethod
    def set_state(self, state: Any) -> None:
        pass

    @abc.abstractmethod
    def get_state(self) -> Any:
        pass

    @abc.abstractmethod
    def print_state(self) -> None:
        pass

    @abc.abstractmethod
    def get_list_action(self) -> Any:
        pass

    @abc.abstractmethod
    def select_action(self) -> Any:
        pass

    @abc.abstractmethod
    def apply_action(self, action: Any) -> None:
        pass


class Python_Game_Server(Game_Server):

    def __init__(self, script: str) -> None:
        module_name, self.class_name = script.split('.')
        self.game_module = importlib.import_module(f"server.py.{module_name}")

    def reset(self) -> None:
        self.game = getattr(self.game_module, self.class_name)()
        self.player = getattr(self.game_module, "RandomPlayer")()

    def set_state(self, state: Any) -> None:
        self.game.set_state(state)

    def get_state(self) -> Any:
        return self.game.get_state()

    def print_state(self) -> None:
        self.game.print_state()

    def get_list_action(self) -> list[Any]:
        return self.game.get_list_action()

    def select_action(self) -> Any:
        return self.player.select_action(self.game.get_state(), self.game.get_list_action())

    def apply_action(self, action: Any) -> None:
        self.game.apply_action(action)
