"""
Обновленный лексический анализатор для языка Kisa
Преобразует исходный код в токены
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Ключевые слова команд
    ВЫВЕДИ = auto()
    РАСПОЗНАТЬ = auto()
    СДЕЛАЙ = auto()
    КАК = auto()
    ТИП = auto()
    ТЕКСТ = auto()
    ИМЯ = auto()
    ССЫЛКУ = auto()
    НАЗВАНИЕ = auto()
    ПЕРЕХОД = auto()
    ПРИ = auto()
    НАЖАТИИ = auto()
    САЙТ = auto()
    ССЫЛКА = auto()
    
    # Новые команды для регистрации
    ПОКАЗАТЬ = auto()
    ЗАГОЛОВОК = auto()
    ПРОЧИТАТЬ = auto()
    ПЕРЕМЕННАЯ = auto()
    СКРЫТЫЙ = auto()
    ПРОВЕРИТЬ = auto()
    ДЛИНА = auto()
    БОЛЬШЕ = auto()
    МЕНЬШЕ = auto()
    РАВНО = auto()
    СОХРАНИТЬ = auto()
    В = auto()
    ФАЙЛ = auto()
    ЕСЛИ = auto()
    ВСЕ_ПРОВЕРЕНО = auto()
    ИНАЧЕ = auto()
    КОНЕЦ = auto()
    ОШИБКА = auto()
    СООБЩЕНИЕ = auto()
    ЧИСЛО = auto()
    ПЛЮС = auto()
    МИНУС = auto()
    УМНОЖИТЬ = auto()
    РАЗДЕЛИТЬ = auto()
    ФУНКЦИЯ = auto()
    ПАРАМЕТРЫ = auto()
    ВОЗВРАТ = auto()
    ВЫЗОВ = auto()
    
    # Команды для игр
    ИГРА = auto()
    СЦЕНА = auto()
    ОБЪЕКТ = auto()
    СОБЫТИЕ = auto()
    ДВИЖЕНИЕ = auto()
    СТОЛКНОВЕНИЕ = auto()
    НАЧИСЛИ = auto()
    ОБНОВИ = auto()
    
    # Атрибуты игр
    ШИРИНА = auto()
    ВЫСОТА = auto()
    ЦВЕТ = auto()
    ПОЗИЦИЯ = auto()
    СКОРОСТЬ = auto()
    РАЗМЕР = auto()
    ИЗОБРАЖЕНИЕ = auto()
    ХОД = auto()
    СЦЕНАРИЙ = auto()
    
    # Литералы и идентификаторы
    СТРОКА = auto()
    ЧИСЛО_ЛИТ = auto()
    ИДЕНТИФИКАТОР = auto()
    
    # Операторы и разделители
    ДВОЕТОЧИЕ = auto()
    ТОЧКА = auto()
    ЗАПЯТАЯ = auto()
    СКОБКА_ОТКРЫВ = auto()
    СКОБКА_ЗАКРЫВ = auto()
    ФИГУРНАЯ_ОТКРЫВ = auto()
    ФИГУРНАЯ_ЗАКРЫВ = auto()
    
    # Специальные
    EOF = auto()
    НЕИЗВЕСТНЫЙ = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Словарь ключевых слов
        self.keywords = {
            'выведи': TokenType.ВЫВЕДИ,
            'распознать': TokenType.РАСПОЗНАТЬ,
            'сделай': TokenType.СДЕЛАЙ,
            'как': TokenType.КАК,
            'тип': TokenType.ТИП,
            'текст': TokenType.ТЕКСТ,
            'имя': TokenType.ИМЯ,
            'ссылку': TokenType.ССЫЛКУ,
            'название': TokenType.НАЗВАНИЕ,
            'переход': TokenType.ПЕРЕХОД,
            'при': TokenType.ПРИ,
            'нажатии': TokenType.НАЖАТИИ,
            'сайт': TokenType.САЙТ,
            'ссылка': TokenType.ССЫЛКА,
            'показать': TokenType.ПОКАЗАТЬ,
            'заголовок': TokenType.ЗАГОЛОВОК,
            'прочитать': TokenType.ПРОЧИТАТЬ,
            'переменная': TokenType.ПЕРЕМЕННАЯ,
            'скрытый': TokenType.СКРЫТЫЙ,
            'проверить': TokenType.ПРОВЕРИТЬ,
            'длина': TokenType.ДЛИНА,
            'больше': TokenType.БОЛЬШЕ,
            'меньше': TokenType.МЕНЬШЕ,
            'равно': TokenType.РАВНО,
            'сохранить': TokenType.СОХРАНИТЬ,
            'в': TokenType.В,
            'файл': TokenType.ФАЙЛ,
            'если': TokenType.ЕСЛИ,
            'все_проверено': TokenType.ВСЕ_ПРОВЕРЕНО,
            'иначе': TokenType.ИНАЧЕ,
            'конец': TokenType.КОНЕЦ,
            'ошибка': TokenType.ОШИБКА,
            'сообщение': TokenType.СООБЩЕНИЕ,
            'число': TokenType.ЧИСЛО,
            'плюс': TokenType.ПЛЮС,
            'минус': TokenType.МИНУС,
            'умножить': TokenType.УМНОЖИТЬ,
            'разделить': TokenType.РАЗДЕЛИТЬ,
            'функция': TokenType.ФУНКЦИЯ,
            'параметры': TokenType.ПАРАМЕТРЫ,
            'возврат': TokenType.ВОЗВРАТ,
            'вызов': TokenType.ВЫЗОВ,
            # Команды для игр
            'игра': TokenType.ИГРА,
            'сцена': TokenType.СЦЕНА,
            'объект': TokenType.ОБЪЕКТ,
            'событие': TokenType.СОБЫТИЕ,
            'движение': TokenType.ДВИЖЕНИЕ,
            'столкновение': TokenType.СТОЛКНОВЕНИЕ,
            'начисли': TokenType.НАЧИСЛИ,
            'обнови': TokenType.ОБНОВИ,
            # Атрибуты
            'ширина': TokenType.ШИРИНА,
            'высота': TokenType.ВЫСОТА,
            'цвет': TokenType.ЦВЕТ,
            'позиция': TokenType.ПОЗИЦИЯ,
            'скорость': TokenType.СКОРОСТЬ,
            'размер': TokenType.РАЗМЕР,
            'изображение': TokenType.ИЗОБРАЖЕНИЕ,
            'ход': TokenType.ХОД,
            'сценарий': TokenType.СЦЕНАРИЙ,
        }
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.code):
            return None
        return self.code[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.position + offset
        if pos >= len(self.code):
            return None
        return self.code[pos]
    
    def advance(self):
        if self.position < len(self.code):
            if self.code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self, quote: str) -> str:
        result = ""
        self.advance()  # пропустить открывающую кавычку
        
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() == 'n':
                    result += '\n'
                elif self.current_char() == 't':
                    result += '\t'
                elif self.current_char() == '\\':
                    result += '\\'
                else:
                    result += self.current_char()
                self.advance()
            else:
                result += self.current_char()
                self.advance()
        
        if self.current_char() == quote:
            self.advance()  # пропустить закрывающую кавычку
        
        return result
    
    def read_identifier(self) -> str:
        result = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() in '_'):
            result += self.current_char()
            self.advance()
        return result
    
    def read_number(self) -> str:
        result = ""
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            result += self.current_char()
            self.advance()
        return result
    
    def tokenize(self) -> List[Token]:
        while self.position < len(self.code):
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            line = self.line
            column = self.column
            char = self.current_char()
            
            # Строки в кавычках
            if char in '"\'':
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.СТРОКА, value, line, column))
            
            # Числа
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.ЧИСЛО_ЛИТ, value, line, column))
            
            # Идентификаторы и ключевые слова
            elif char.isalpha() or char == '_':
                value = self.read_identifier()
                token_type = self.keywords.get(value, TokenType.ИДЕНТИФИКАТОР)
                self.tokens.append(Token(token_type, value, line, column))
            
            # Операторы и разделители
            elif char == ':':
                self.tokens.append(Token(TokenType.ДВОЕТОЧИЕ, ':', line, column))
                self.advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.ТОЧКА, '.', line, column))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.ЗАПЯТАЯ, ',', line, column))
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.СКОБКА_ОТКРЫВ, '(', line, column))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.СКОБКА_ЗАКРЫВ, ')', line, column))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.ФИГУРНАЯ_ОТКРЫВ, '{', line, column))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.ФИГУРНАЯ_ЗАКРЫВ, '}', line, column))
                self.advance()
            else:
                self.tokens.append(Token(TokenType.НЕИЗВЕСТНЫЙ, char, line, column))
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
