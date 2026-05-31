"""
Обновленный интерпретатор для языка Kisa
Исполняет AST команды с поддержкой игровых функций
"""

import json
import os
from typing import Dict, Any, List
from getpass import getpass
from kisa_parser import (
    Program, VyveliCommand, RaspoznatCommand, SdelaiCommand, 
    PokzatCommand, ProchitatCommand, PeremennaiaCommand, ProveritCommand,
    EsliCommand, SohranitCommand, FunkciaCommand, VyzvovCommand, VozvrtatCommand,
    IgraCommand, ScenaCommand, ObjectCommand, EventCommand, NachisliCommand,
    ObnoviCommand, parse_code
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
        
        # Игровые переменные
        self.game_state: Dict[str, Any] = {
            'name': '',
            'width': 800,
            'height': 600,
            'scenes': {},
            'objects': {},
            'stats': {},
            'events': {}
        }
    
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
            # Игровые команды
            elif isinstance(command, IgraCommand):
                self.execute_igra(command)
            elif isinstance(command, ScenaCommand):
                self.execute_scena(command)
            elif isinstance(command, ObjectCommand):
                self.execute_object(command)
            elif isinstance(command, EventCommand):
                self.execute_event(command)
            elif isinstance(command, NachisliCommand):
                self.execute_nachisli(command)
            elif isinstance(command, ObnoviCommand):
                self.execute_update(command)
        
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
        condition_met = False
        
        if "все_проверено" in command.condition:
            condition_met = all(self.checks.values()) if self.checks else True
        else:
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
    
    # ============= ИГРОВЫЕ КОМАНДЫ =============
    
    def execute_igra(self, command: IgraCommand):
        """Выполняет команду игра - инициализирует игру"""
        self.game_state['name'] = command.name
        self.game_state['width'] = command.width
        self.game_state['height'] = command.height
        
        msg = f"🎮 Игра '{command.name}' инициализирована ({command.width}x{command.height})"
        self.console_output.append(msg)
        print(msg)
    
    def execute_scena(self, command: ScenaCommand):
        """Выполняет команду сцена - добавляет сцену в игру"""
        self.game_state['scenes'][command.scene_name] = {
            'commands': command.scenario_commands,
            'objects': []
        }
        
        msg = f"📍 Сцена '{command.scene_name}' создана"
        self.console_output.append(msg)
        print(msg)
        
        # Выполняем сценарий сцены
        for cmd in command.scenario_commands:
            self.execute(Program([cmd]))
    
    def execute_object(self, command: ObjectCommand):
        """Выполняет команду объект - создает игровой объект"""
        obj = {
            'name': command.object_name,
            'type': command.object_type,
            'properties': command.properties
        }
        
        self.game_state['objects'][command.object_name] = obj
        
        props_str = ", ".join([f"{k}={v}" for k, v in command.properties.items()])
        msg = f"🎯 Объект '{command.object_name}' создан ({props_str})"
        self.console_output.append(msg)
        print(msg)
    
    def execute_event(self, command: EventCommand):
        """Выполняет команду событие - добавляет обработчик события"""
        event_key = f"{command.event_type}:{command.event_trigger}"
        self.game_state['events'][event_key] = command
        
        msg = f"⚡ Событие '{event_key}' зарегистрировано"
        self.console_output.append(msg)
        print(msg)
    
    def execute_nachisli(self, command: NachisliCommand):
        """Выполняет команду начисли - увеличивает/уменьшает статистику"""
        if command.stat_type not in self.game_state['stats']:
            self.game_state['stats'][command.stat_type] = 0
        
        if command.operation == "плюс":
            self.game_state['stats'][command.stat_type] += command.value
        elif command.operation == "минус":
            self.game_state['stats'][command.stat_type] -= command.value
        
        current_value = self.game_state['stats'][command.stat_type]
        op_symbol = "+" if command.operation == "плюс" else "-"
        msg = f"📊 {command.stat_type}: {op_symbol}{command.value} (текущее значение: {current_value})"
        self.console_output.append(msg)
        print(msg)
    
    def execute_update(self, command: ObnoviCommand):
        """Выполняет команду обнови - обновляет свойства объекта"""
        if command.object_name in self.game_state['objects']:
            obj = self.game_state['objects'][command.object_name]
            for key, value in command.updates.items():
                obj['properties'][key] = value
            
            updates_str = ", ".join([f"{k}={v}" for k, v in command.updates.items()])
            msg = f"🔄 Объект '{command.object_name}' обновлен ({updates_str})"
            self.console_output.append(msg)
            print(msg)
        else:
            error_msg = f"✗ Объект '{command.object_name}' не найден"
            self.console_output.append(error_msg)
            print(error_msg)
    
    def get_output(self) -> str:
        """Возвращает полный вывод программы"""
        result = []
        
        if self.console_output:
            result.extend(self.console_output)
        
        if self.html_output:
            result.append("\n=== HTML Output ===")
            result.extend(self.html_output)
        
        # Добавляем информацию об игре если она создана
        if self.game_state['name']:
            result.append("\n=== Состояние игры ===")
            result.append(f"Название: {self.game_state['name']}")
            result.append(f"Размер: {self.game_state['width']}x{self.game_state['height']}")
            
            if self.game_state['objects']:
                result.append(f"Объектов: {len(self.game_state['objects'])}")
            if self.game_state['stats']:
                result.append(f"Статистика: {self.game_state['stats']}")
        
        return "\n".join(result)
    
    def set_variable(self, name: str, value: Any):
        """Устанавливает значение переменной"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Получает значение переменной"""
        return self.variables.get(name)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Возвращает состояние игры"""
        return self.game_state


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
игра название:"Моя первая игра" ширина:800 высота:600.
объект герой позиция:(100,100) размер:(50,50) цвет:синий.
начисли очки плюс:10.
показать сообщение Игра запущена успешно.
    """
    
    result = run_kisa_code(example_code)
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:")
    print("="*50)
    print(result)
