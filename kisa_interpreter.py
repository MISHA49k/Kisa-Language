"""
Обновленный интерпретатор для языка Kisa
Исполняет AST команды с поддержкой регистрации
"""

import json
import os
from typing import Dict, Any, List
from getpass import getpass
from kisa_parser import (
    Program, VyveliCommand, RaspoznatCommand, SdelaiCommand, 
    PokzatCommand, ProchitatCommand, PeremennaiaCommand, ProveritCommand,
    EsliCommand, SohranitCommand, FunkciaCommand, VyzvovCommand, VozvrtatCommand,
    parse_code
)


class KisaInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.types: Dict[str, str] = {}
        self.html_output: List[str] = []
        self.console_output: List[str] = []
        self.functions: Dict[str, FunkciaCommand] = {}
        self.checks: Dict[str, bool] = {}
        self.last_check_result = True
    
    def execute(self, program: Program) -> str:
        """Исполняет программу и возвращает результат"""
        for command in program.commands:
            if isinstance(command, VyveliCommand):
                self.execute_vyvedli(command)
            elif isinstance(command, RaspoznatCommand):
                self.execute_raspoznat(command)
            elif isinstance(command, SdelaiCommand):
                self.execute_sdelai(command)
            elif isinstance(command, PokzatCommand):
                self.execute_pokazat(command)
            elif isinstance(command, ProchitatCommand):
                self.execute_prochitat(command)
            elif isinstance(command, PeremennaiaCommand):
                self.execute_peremenaia(command)
            elif isinstance(command, ProveritCommand):
                self.execute_proverit(command)
            elif isinstance(command, EsliCommand):
                self.execute_esli(command)
            elif isinstance(command, SohranitCommand):
                self.execute_sohranit(command)
            elif isinstance(command, FunkciaCommand):
                self.execute_funkcija(command)
            elif isinstance(command, VyzvovCommand):
                self.execute_vyzov(command)
            elif isinstance(command, VozvrtatCommand):
                self.execute_vozvrtat(command)
        
        return self.get_output()
    
    def execute_vyvedli(self, command: VyveliCommand):
        """Выполняет команду выведи"""
        output = command.value
        
        import re
        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, f"({var_name})"))
        
        output = re.sub(r'\((\w+)\)', replace_var, output)
        
        if command.type_name == "текст":
            self.console_output.append(output)
            print(output)
    
    def execute_raspoznat(self, command: RaspoznatCommand):
        """Выполняет команду распознать"""
        self.types[command.type_name] = command.as_type
        self.variables[command.type_name] = None
    
    def execute_sdelai(self, command: SdelaiCommand):
        """Выполняет команду сделай (создание элементов)"""
        if command.element_type == "текст" and command.element_name == "ссылку":
            name = command.parameters.get("название", "Ссылка")
            url = command.parameters.get("ссылка", "#")
            html = f'<a href="{url}">{name}</a>'
            self.html_output.append(html)
    
    def execute_pokazat(self, command: PokzatCommand):
        """Выполняет команду показать"""
        output = ""
        if command.display_type == "заголовок":
            output = f"\n{'='*50}\n{command.content}\n{'='*50}"
        elif command.display_type == "сообщение":
            output = f"✓ {command.content}"
        elif command.display_type == "ошибка":
            output = f"✗ ОШИБКА: {command.content}"
        
        self.console_output.append(output)
        print(output)
    
    def execute_prochitat(self, command: ProchitatCommand):
        """Выполняет команду прочитать"""
        if command.is_hidden:
            value = getpass(f"Введите {command.var_name}: ")
        else:
            value = input(f"Введите {command.var_name}: ")
        
        # Преобразуем тип
        if command.var_type == "число":
            try:
                self.variables[command.var_name] = int(value)
            except ValueError:
                self.variables[command.var_name] = 0
        else:
            self.variables[command.var_name] = value
        
        self.types[command.var_name] = command.var_type
    
    def execute_peremenaia(self, command: PeremennaiaCommand):
        """Выполняет команду переменная"""
        if command.value is not None:
            if command.var_type == "число":
                try:
                    self.variables[command.var_name] = int(command.value)
                except ValueError:
                    self.variables[command.var_name] = 0
            else:
                self.variables[command.var_name] = command.value
        else:
            self.variables[command.var_name] = None
        
        self.types[command.var_name] = command.var_type
    
    def execute_proverit(self, command: ProveritCommand):
        """Выполняет команду проверить"""
        var_value = self.variables.get(command.var_name)
        result = False
        
        if "длина" in command.condition:
            length = len(str(var_value)) if var_value else 0
            expected = int(command.expected_value) if command.expected_value else 0
            
            if "больше" in command.condition:
                result = length > expected
            elif "меньше" in command.condition:
                result = length < expected
            elif "равно" in command.condition:
                result = length == expected
        
        elif "тип" in command.condition:
            result = self.types.get(command.var_name) == command.expected_value
        
        elif "равно" in command.condition:
            result = str(var_value) == str(command.expected_value)
        
        self.checks[command.var_name] = result
        self.last_check_result = result
    
    def execute_esli(self, command: EsliCommand):
        """Выполняет команду если"""
        # Простая обработка условия
        condition_met = False
        
        if "все_проверено" in command.condition:
            condition_met = all(self.checks.values()) if self.checks else True
        else:
            # Общее условие
            condition_met = self.last_check_result
        
        if condition_met:
            for cmd in command.then_commands:
                self.execute(Program([cmd]))
        elif command.else_commands:
            for cmd in command.else_commands:
                self.execute(Program([cmd]))
    
    def execute_sohranit(self, command: SohranitCommand):
        """Выполняет команду сохранить"""
        data = {}
        for var in command.variables:
            data[var] = str(self.variables.get(var, ""))
        
        try:
            with open(command.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            msg = f"Данные сохранены в файл {command.file_path}"
            self.console_output.append(msg)
            print(msg)
        except Exception as e:
            error_msg = f"Ошибка при сохранении: {str(e)}"
            self.console_output.append(error_msg)
            print(error_msg)
    
    def execute_funkcija(self, command: FunkciaCommand):
        """Выполняет команду функция"""
        self.functions[command.name] = command
    
    def execute_vyzov(self, command: VyzvovCommand):
        """Выполняет команду вызов"""
        if command.name in self.functions:
            func = self.functions[command.name]
            for cmd in func.body:
                self.execute(Program([cmd]))
    
    def execute_vozvrtat(self, command: VozvrtatCommand):
        """Выполняет команду возврат"""
        pass  # Будет реализовано позже
    
    def get_output(self) -> str:
        """Возвращает полный вывод программы"""
        result = []
        
        if self.console_output:
            result.extend(self.console_output)
        
        if self.html_output:
            result.append("\n=== HTML Output ===")
            result.extend(self.html_output)
        
        return "\n".join(result)
    
    def set_variable(self, name: str, value: Any):
        """Устанавливает значение переменной"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Получает значение переменной"""
        return self.variables.get(name)


def run_kisa_code(code: str) -> str:
    """Запускает код на языке Kisa и возвращает результат"""
    try:
        program = parse_code(code)
        interpreter = KisaInterpreter()
        return interpreter.execute(program)
    except Exception as e:
        return f"Ошибка: {str(e)}"


# Пример использования
if __name__ == "__main__":
    example_code = """
выведи тип:текст Привет.
распознать тип:имя как текст.
выведи тип:текст Привет, (имя).
    """
    
    result = run_kisa_code(example_code)
    print(result)
