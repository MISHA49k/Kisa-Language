"""
Обновленный парсер для языка Kisa
Преобразует токены в абстрактное синтаксическое дерево (AST)
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from kisa_lexer import Token, TokenType, Lexer


@dataclass
class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    commands: List['Command']


@dataclass
class Command(ASTNode):
    pass


@dataclass
class VyveliCommand(Command):
    """Команда: выведи тип:текст ..."""
    type_name: str
    value: str


@dataclass
class RaspoznatCommand(Command):
    """Команда: распознать тип:имя как текст."""
    type_name: str
    as_type: str


@dataclass
class SdelaiCommand(Command):
    """Команда: сделай текст ссылку ..."""
    element_type: str
    element_name: str
    parameters: Dict[str, str]


@dataclass
class PokzatCommand(Command):
    """Команда: показать заголовок/сообщение/ошибка <текст>."""
    display_type: str  # заголовок, сообщение, ошибка
    content: str


@dataclass
class ProchitatCommand(Command):
    """Команда: прочитать переменная <имя> <тип> [скрытый]."""
    var_name: str
    var_type: str
    is_hidden: bool = False


@dataclass
class PeremennaiaCommand(Command):
    """Команда: переменная <имя> тип:<тип> значение:<значение>."""
    var_name: str
    var_type: str
    value: Optional[str] = None


@dataclass
class ProveritCommand(Command):
    """Команда: проверить <переменная> <условие> <значение>."""
    var_name: str
    condition: str  # длина, тип, равно, больше, меньше
    expected_value: Optional[str] = None


@dataclass
class EsliCommand(Command):
    """Команда: если <условие>. ... иначе. ... конец."""
    condition: str
    then_commands: List[Command]
    else_commands: Optional[List[Command]] = None


@dataclass
class SohranitCommand(Command):
    """Команда: сохранить <переменные> в файл <путь>."""
    variables: List[str]
    file_path: str


@dataclass
class FunkciaCommand(Command):
    """Команда: функция <имя> параметры:(<параметры>). ... конец."""
    name: str
    parameters: List[str]
    body: List[Command]


@dataclass
class VyzvovCommand(Command):
    """Команда: вызов <имя_функции> с параметрами:(<значения>)."""
    name: str
    arguments: Dict[str, str]


@dataclass
class VozvrtatCommand(Command):
    """Команда: возврат <значение>."""
    value: str


# ============= ИГРОВЫЕ КОМАНДЫ =============

@dataclass
class IgraCommand(Command):
    """Команда: игра название:"имя" ширина:800 высота:600."""
    name: str
    width: int
    height: int
    properties: Dict[str, Any] = None


@dataclass
class ScenaCommand(Command):
    """Команда: сцена главная сценарий:{...}."""
    scene_name: str
    scenario_commands: List[Command]


@dataclass
class ObjectCommand(Command):
    """Команда: объект герой позиция:(100,100) размер:(50,50) цвет:синий."""
    object_name: str
    object_type: str
    properties: Dict[str, Any]  # позиция, размер, цвет, изображение, и т.д.


@dataclass
class EventCommand(Command):
    """Команда: событие движение при нажатии стрелка_вверх."""
    event_type: str  # движение, столкновение, нажатие
    event_trigger: str
    action: Optional[str] = None


@dataclass
class NachisliCommand(Command):
    """Команда: начисли очки плюс:10 или начисли здоровье минус:5."""
    stat_type: str  # очки, здоровье, энергия
    operation: str  # плюс, минус
    value: int


@dataclass
class ObnoviCommand(Command):
    """Команда: обнови герой позиция:(x+5,y) скорость:5."""
    object_name: str
    updates: Dict[str, Any]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Token:
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[pos]
    
    def advance(self):
        if self.position < len(self.tokens):
            self.position += 1
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(f"Ожидался {token_type}, получен {token.type} на строке {token.line}")
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType) -> bool:
        if self.match(token_type):
            self.advance()
            return True
        return False
    
    def parse(self) -> Program:
        commands = []
        while not self.match(TokenType.EOF):
            command = self.parse_command()
            if command:
                commands.append(command)
        return Program(commands)
    
    def parse_command(self) -> Optional[Command]:
        if self.match(TokenType.ВЫВЕДИ):
            return self.parse_vyvedli_command()
        elif self.match(TokenType.РАСПОЗНАТЬ):
            return self.parse_raspoznat_command()
        elif self.match(TokenType.СДЕЛАЙ):
            return self.parse_sdelai_command()
        elif self.match(TokenType.ПОКАЗАТЬ):
            return self.parse_pokazat_command()
        elif self.match(TokenType.ПРОЧИТАТЬ):
            return self.parse_prochitat_command()
        elif self.match(TokenType.ПЕРЕМЕННАЯ):
            return self.parse_peremenaia_command()
        elif self.match(TokenType.ПРОВЕРИТЬ):
            return self.parse_proverit_command()
        elif self.match(TokenType.ЕСЛИ):
            return self.parse_esli_command()
        elif self.match(TokenType.СОХРАНИТЬ):
            return self.parse_sohranit_command()
        elif self.match(TokenType.ФУНКЦИЯ):
            return self.parse_funkcija_command()
        elif self.match(TokenType.ВЫЗОВ):
            return self.parse_vyzov_command()
        elif self.match(TokenType.ВОЗВРАТ):
            return self.parse_vozvrtat_command()
        # Игровые команды
        elif self.match(TokenType.ИГРА):
            return self.parse_igra_command()
        elif self.match(TokenType.СЦЕНА):
            return self.parse_scena_command()
        elif self.match(TokenType.ОБЪЕКТ):
            return self.parse_object_command()
        elif self.match(TokenType.СОБЫТИЕ):
            return self.parse_event_command()
        elif self.match(TokenType.НАЧИСЛИ):
            return self.parse_nachisli_command()
        elif self.match(TokenType.ОБНОВИ):
            return self.parse_upd_command()
        else:
            # Пропустить неизвестный токен
            self.advance()
            return None
    
    def parse_vyvedli_command(self) -> VyveliCommand:
        """выведи тип:текст Привет."""
        self.expect(TokenType.ВЫВЕДИ)
        self.expect(TokenType.ТИП)
        self.expect(TokenType.ДВОЕТОЧИЕ)
        
        type_token = self.current_token()
        if self.match(TokenType.ТЕКСТ):
            self.advance()
            type_name = "текст"
        else:
            type_name = type_token.value
            self.advance()
        
        value = ""
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            if self.match(TokenType.СКОБКА_ОТКРЫВ):
                self.advance()
                var_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
                value += f"({var_name})"
                self.expect(TokenType.СКОБКА_ЗАКРЫВ)
            else:
                value += self.current_token().value
                if not self.match(TokenType.ТОЧКА):
                    value += " "
                self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return VyveliCommand(type_name, value.strip())
    
    def parse_raspoznat_command(self) -> RaspoznatCommand:
        """распознать тип:имя как текст."""
        self.expect(TokenType.РАСПОЗНАТЬ)
        self.expect(TokenType.ТИП)
        self.expect(TokenType.ДВОЕТОЧИЕ)
        
        type_name = self.expect(TokenType.ИМЯ).value
        self.expect(TokenType.КАК)
        as_type = self.expect(TokenType.ТЕКСТ).value
        self.expect(TokenType.ТОЧКА)
        
        return RaspoznatCommand(type_name, as_type)
    
    def parse_sdelai_command(self) -> SdelaiCommand:
        """сделай текст ссылку название:YouTube, ссылка:youtube.com."""
        self.expect(TokenType.СДЕЛАЙ)
        element_type = self.expect(TokenType.ТЕКСТ).value
        element_name = self.expect(TokenType.ССЫЛКУ).value
        
        parameters = {}
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            if self.match(TokenType.НАЗВАНИЕ, TokenType.ССЫЛКА):
                param_name = self.current_token().value
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                param_value = ""
                while not self.match(TokenType.ЗАПЯТАЯ, TokenType.ТОЧКА, TokenType.EOF):
                    param_value += self.current_token().value
                    self.advance()
                parameters[param_name] = param_value.strip()
                if self.match(TokenType.ЗАПЯТАЯ):
                    self.advance()
            else:
                self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return SdelaiCommand(element_type, element_name, parameters)
    
    def parse_pokazat_command(self) -> PokzatCommand:
        """показать заголовок/сообщение/ошибка <текст>."""
        self.expect(TokenType.ПОКАЗАТЬ)
        
        display_type = ""
        if self.match(TokenType.ЗАГОЛОВОК):
            display_type = "заголовок"
            self.advance()
        elif self.match(TokenType.СООБЩЕНИЕ):
            display_type = "сообщение"
            self.advance()
        elif self.match(TokenType.ОШИБКА):
            display_type = "ошибка"
            self.advance()
        
        content = ""
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            content += self.current_token().value + " "
            self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return PokzatCommand(display_type, content.strip())
    
    def parse_prochitat_command(self) -> ProchitatCommand:
        """прочитать переменная <имя> <тип> [скрытый]."""
        self.expect(TokenType.ПРОЧИТАТЬ)
        self.expect(TokenType.ПЕРЕМЕННАЯ)
        
        var_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        var_type = "текст"
        if self.match(TokenType.ТЕКСТ, TokenType.ЧИСЛО):
            var_type = self.current_token().value
            self.advance()
        
        is_hidden = self.consume(TokenType.СКРЫТЫЙ)
        self.expect(TokenType.ТОЧКА)
        
        return ProchitatCommand(var_name, var_type, is_hidden)
    
    def parse_peremenaia_command(self) -> PeremennaiaCommand:
        """переменная <имя> тип:<тип> значение:<значение>."""
        self.expect(TokenType.ПЕРЕМЕННАЯ)
        var_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        self.expect(TokenType.ТИП)
        self.expect(TokenType.ДВОЕТОЧИЕ)
        var_type = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        value = None
        if self.consume(TokenType.ЗНАЧЕНИЕ):
            self.expect(TokenType.ДВОЕТОЧИЕ)
            value = self.current_token().value
            self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return PeremennaiaCommand(var_name, var_type, value)
    
    def parse_proverit_command(self) -> ProveritCommand:
        """проверить <переменная> <условие> <значение>."""
        self.expect(TokenType.ПРОВЕРИТЬ)
        var_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        condition = ""
        expected_value = None
        
        if self.match(TokenType.ДЛИНА):
            condition = "длина"
            self.advance()
            if self.match(TokenType.БОЛЬШЕ, TokenType.МЕНЬШЕ, TokenType.РАВНО):
                condition += "_" + self.current_token().value
                self.advance()
                expected_value = self.expect(TokenType.ЧИСЛО_ЛИТ).value
        elif self.match(TokenType.ТИП):
            condition = "тип"
            self.advance()
            expected_value = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        self.expect(TokenType.ТОЧКА)
        return ProveritCommand(var_name, condition, expected_value)
    
    def parse_esli_command(self) -> EsliCommand:
        """если <условие>. ... иначе. ... конец."""
        self.expect(TokenType.ЕСЛИ)
        
        condition = ""
        while not self.match(TokenType.ТОЧКА):
            condition += self.current_token().value + " "
            self.advance()
        self.expect(TokenType.ТОЧКА)
        
        then_commands = []
        while not self.match(TokenType.ИНАЧЕ, TokenType.КОНЕЦ, TokenType.EOF):
            cmd = self.parse_command()
            if cmd:
                then_commands.append(cmd)
        
        else_commands = None
        if self.consume(TokenType.ИНАЧЕ):
            self.expect(TokenType.ТОЧКА)
            else_commands = []
            while not self.match(TokenType.КОНЕЦ, TokenType.EOF):
                cmd = self.parse_command()
                if cmd:
                    else_commands.append(cmd)
        
        self.expect(TokenType.КОНЕЦ)
        self.expect(TokenType.ТОЧКА)
        
        return EsliCommand(condition.strip(), then_commands, else_commands)
    
    def parse_sohranit_command(self) -> SohranitCommand:
        """сохранить <переменные> в файл <путь>."""
        self.expect(TokenType.СОХРАНИТЬ)
        
        variables = []
        while not self.match(TokenType.В):
            if self.match(TokenType.ИДЕНТИФИКАТОР):
                variables.append(self.current_token().value)
            self.advance()
        
        self.expect(TokenType.В)
        self.expect(TokenType.ФАЙЛ)
        file_path = self.expect(TokenType.СТРОКА).value
        self.expect(TokenType.ТОЧКА)
        
        return SohranitCommand(variables, file_path)
    
    def parse_funkcija_command(self) -> FunkciaCommand:
        """функция <имя> параметры:(<параметры>). ... конец."""
        self.expect(TokenType.ФУНКЦИЯ)
        name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        parameters = []
        if self.consume(TokenType.ПАРАМЕТРЫ):
            self.expect(TokenType.ДВОЕТОЧИЕ)
            self.expect(TokenType.СКОБКА_ОТКРЫВ)
            while not self.match(TokenType.СКОБКА_ЗАКРЫВ):
                if self.match(TokenType.ИДЕНТИФИКАТОР):
                    parameters.append(self.current_token().value)
                self.advance()
            self.expect(TokenType.СКОБКА_ЗАКРЫВ)
        
        self.expect(TokenType.ТОЧКА)
        
        body = []
        while not self.match(TokenType.КОНЕЦ):
            cmd = self.parse_command()
            if cmd:
                body.append(cmd)
        
        self.expect(TokenType.КОНЕЦ)
        self.expect(TokenType.ТОЧКА)
        
        return FunkciaCommand(name, parameters, body)
    
    def parse_vyzov_command(self) -> VyzvovCommand:
        """вызов <имя_функции> с параметрами:(<значения>)."""
        self.expect(TokenType.ВЫЗОВ)
        name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        arguments = {}
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return VyzvovCommand(name, arguments)
    
    def parse_vozvrtat_command(self) -> VozvrtatCommand:
        """возврат <значение>."""
        self.expect(TokenType.ВОЗВРАТ)
        value = self.current_token().value
        self.advance()
        self.expect(TokenType.ТОЧКА)
        
        return VozvrtatCommand(value)
    
    # ============= ИГРОВЫЕ ПАРСЕРЫ =============
    
    def parse_igra_command(self) -> IgraCommand:
        """игра название:"Моя игра" ширина:800 высота:600."""
        self.expect(TokenType.ИГРА)
        
        name = ""
        width = 800
        height = 600
        properties = {}
        
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            if self.match(TokenType.НАЗВАНИЕ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                name = self.expect(TokenType.СТРОКА).value
            elif self.match(TokenType.ШИРИНА):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                width = int(self.expect(TokenType.ЧИСЛО_ЛИТ).value)
            elif self.match(TokenType.ВЫСОТА):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                height = int(self.expect(TokenType.ЧИСЛО_ЛИТ).value)
            else:
                self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return IgraCommand(name, width, height, properties)
    
    def parse_scena_command(self) -> ScenaCommand:
        """сцена главная сценарий:{...}."""
        self.expect(TokenType.СЦЕНА)
        scene_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        scenario_commands = []
        if self.consume(TokenType.СЦЕНАРИЙ):
            self.expect(TokenType.ДВОЕТОЧИЕ)
            self.expect(TokenType.ФИГУРНАЯ_ОТКРЫВ)
            
            while not self.match(TokenType.ФИГУРНАЯ_ЗАКРЫВ):
                cmd = self.parse_command()
                if cmd:
                    scenario_commands.append(cmd)
            
            self.expect(TokenType.ФИГУРНАЯ_ЗАКРЫВ)
        
        self.expect(TokenType.ТОЧКА)
        return ScenaCommand(scene_name, scenario_commands)
    
    def parse_object_command(self) -> ObjectCommand:
        """объект герой позиция:(100,100) размер:(50,50) цвет:синий."""
        self.expect(TokenType.ОБЪЕКТ)
        object_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        object_type = "персонаж"  # по умолчанию
        properties = {}
        
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            if self.match(TokenType.ПОЗИЦИЯ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                pos_str = self.parse_coordinates()
                properties['позиция'] = pos_str
            elif self.match(TokenType.РАЗМЕР):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                size_str = self.parse_coordinates()
                properties['размер'] = size_str
            elif self.match(TokenType.ЦВЕТ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                properties['цвет'] = self.expect(TokenType.ИДЕНТИФИКАТОР).value
            elif self.match(TokenType.ИЗОБРАЖЕНИЕ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                properties['изображение'] = self.expect(TokenType.СТРОКА).value
            else:
                self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return ObjectCommand(object_name, object_type, properties)
    
    def parse_event_command(self) -> EventCommand:
        """событие движение при нажатии стрелка_вверх."""
        self.expect(TokenType.СОБЫТИЕ)
        
        event_type = ""
        if self.match(TokenType.ДВИЖЕНИЕ):
            event_type = "движение"
            self.advance()
        elif self.match(TokenType.СТОЛКНОВЕНИЕ):
            event_type = "столкновение"
            self.advance()
        
        event_trigger = ""
        if self.consume(TokenType.ПРИ):
            if self.consume(TokenType.НАЖАТИИ):
                event_trigger = "нажатие_" + self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        self.expect(TokenType.ТОЧКА)
        return EventCommand(event_type, event_trigger)
    
    def parse_nachisli_command(self) -> NachisliCommand:
        """начисли очки плюс:10."""
        self.expect(TokenType.НАЧИСЛИ)
        stat_type = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        operation = "плюс"
        if self.consume(TokenType.ПЛЮС):
            self.expect(TokenType.ДВОЕТОЧИЕ)
            operation = "плюс"
        elif self.consume(TokenType.МИНУС):
            self.expect(TokenType.ДВОЕТОЧИЕ)
            operation = "минус"
        
        value = int(self.expect(TokenType.ЧИСЛО_ЛИТ).value)
        self.expect(TokenType.ТОЧКА)
        
        return NachisliCommand(stat_type, operation, value)
    
    def parse_upd_command(self) -> ObnoviCommand:
        """обнови герой позиция:(x+5,y)."""
        self.expect(TokenType.ОБНОВИ)
        object_name = self.expect(TokenType.ИДЕНТИФИКАТОР).value
        
        updates = {}
        while not self.match(TokenType.ТОЧКА, TokenType.EOF):
            if self.match(TokenType.ПОЗИЦИЯ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                pos_str = self.parse_coordinates()
                updates['позиция'] = pos_str
            elif self.match(TokenType.СКОРОСТЬ):
                self.advance()
                self.expect(TokenType.ДВОЕТОЧИЕ)
                updates['скорость'] = int(self.expect(TokenType.ЧИСЛО_ЛИТ).value)
            else:
                self.advance()
        
        self.expect(TokenType.ТОЧКА)
        return ObnoviCommand(object_name, updates)
    
    def parse_coordinates(self) -> str:
        """Парсит координаты вида (100,200)"""
        self.expect(TokenType.СКОБКА_ОТКРЫВ)
        coord_str = ""
        while not self.match(TokenType.СКОБКА_ЗАКРЫВ):
            coord_str += self.current_token().value
            self.advance()
        self.expect(TokenType.СКОБКА_ЗАКРЫВ)
        return coord_str.strip()


def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
