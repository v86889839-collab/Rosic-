#!/usr/bin/env python3
"""
Росич v0.2 — интерпретатор языка программирования на русском.
Форматы файлов:
  .рос    — главный файл проекта (точка входа)
  .rus    — обычный файл/модуль
  .функц  — функция в отдельном файле
  .лог    — лог-файл
  .сфайл  — стоп-файл (останавливает циклы)
"""

import sys
import os
import re
from pathlib import Path

TEST_MODE = False
TEST_RESULTS = []

def start_test_mode(filepath):
    global TEST_MODE
    TEST_MODE = True
    print(f"=== ЗАПУСК ТЕСТОВ: {os.path.basename(filepath)} ===")

def record_test(name, success, error_msg=""):
    status = "[PASS]" if success else "[FAIL]"
    msg = f"{status} ТЕСТ: {name}"
    if not success:
        msg += f" — {error_msg}"
    TEST_RESULTS.append((success, name, error_msg))
    print(msg)

def finish_tests():
    passed = sum(1 for s, _, _ in TEST_RESULTS if s)
    failed = len(TEST_RESULTS) - passed
    print("=== РЕЗУЛЬТАТЫ ТЕСТОВ ===")
    print(f"Всего тестов: {len(TEST_RESULTS)}")
    print(f"Пройдено: {passed}")
    print(f"Упало: {failed}")
    if failed > 0:
        print("ОШИБКА: тесты не пройдены!")
        sys.exit(1)
    else:
        print("Все тесты пройдены.")

# --- Внутри функции execute_file (или где ты читаешь файл построчно) ---

def execute_file(filepath):
    # Проверка расширения
    _, ext = os.path.splitext(filepath)
    if ext == ".test":
        start_test_mode(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_test_name = None
    current_test_lines = []

    for line in lines:
        stripped = line.strip()

        # Если это метка теста — начинаем новый тест
        if stripped.startswith("// ТЕСТ:") or stripped.startswith("# ТЕСТ:"):
            # Если был предыдущий тест — выполняем его
            if current_test_name is not None and current_test_lines:
                run_single_test(current_test_name, current_test_lines)
            # Начинаем новый тест
            current_test_name = stripped.split(":", 1)[1].strip()
            current_test_lines = [line]
            continue

        # Обычный код: добавляем к текущему тесту, если режим тестов
        if TEST_MODE and current_test_name:
            current_test_lines.append(line)
        else:
            # Обычный режим: просто выполняем строку
            execute_line(line)  # твоя существующая функция

    # Выполняем последний тест, если был
    if TEST_MODE and current_test_name and current_test_lines:
        run_single_test(current_test_name, current_test_lines)

    if TEST_MODE:
        finish_tests()

def run_single_test(test_name, lines):
    try:
        code = "".join(lines)
        execute_code(code)  # твоя функция, которая исполняет кусок кода
        record_test(test_name, True)
    except Exception as e:
        tb = traceback.format_exc()
        record_test(test_name, False, str(e))
        # Опционально: можно вывести traceback для детальной отладки
        # print(tb)
        
# === ЛЕКСЕР ===

class Token:
    def __init__(self, тип, значение, строка=0):
        self.тип = тип
        self.значение = значение
        self.строка = строка
    def __repr__(self):
        return f"Token({self.тип}, {self.значение!r})"

KEYWORDS = {
    'пусть': 'LET',
    'функция': 'FUNC',
    'вернуть': 'RETURN',
    'если': 'IF',
    'иначе': 'ELSE',
    'для': 'FOR',
    'пока': 'WHILE',
    'снова': 'LOOP',
    'стоп': 'BREAK',
    'дальше': 'CONTINUE',
    'структура': 'STRUCT',
    'импорт': 'IMPORT',
    'печатать': 'PRINT',
    'правда': 'TRUE',
    'ложно': 'FALSE',
    'и': 'AND',
    'или': 'OR',
    'не': 'NOT',
    'в': 'IN',
    'пары': 'PAIRS',
    'попытка': 'TRY',
    'ловля': 'CATCH',
    'бросить': 'THROW',
    'после': 'AFTER',
}

def lex(source):
    tokens = []
    i = 0
    строка = 1
    while i < len(source):
        c = source[i]
        # Перенос строки
        if c == '\n':
            tokens.append(Token('NEWLINE', '\n', строка))
            строка += 1
            i += 1
            continue
        # Пробелы и табы
        if c in ' \t\r':
            i += 1
            continue
        # Комментарии // или #
        if c == '/' and i+1 < len(source) and source[i+1] == '/':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue
        if c == '#':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue
        # Строка
        if c == '"':
            i += 1
            s = ''
            while i < len(source) and source[i] != '"':
                if source[i] == '\\' and i+1 < len(source):
                    nxt = source[i+1]
                    if nxt == 'n': s += '\n'
                    elif nxt == 't': s += '\t'
                    elif nxt == '"': s += '"'
                    elif nxt == '\\': s += '\\'
                    else: s += nxt
                    i += 2
                else:
                    s += source[i]
                    i += 1
            i += 1  # закрывающая кавычка
            tokens.append(Token('STRING', s, строка))
            continue
        # Число
        if c.isdigit() or (c == '.' and i+1 < len(source) and source[i+1].isdigit()):
            num = ''
            while i < len(source) and (source[i].isdigit() or source[i] == '.'):
                num += source[i]
                i += 1
            if '.' in num:
                tokens.append(Token('NUMBER', float(num), строка))
            else:
                tokens.append(Token('NUMBER', int(num), строка))
            continue
        # Идентификатор / ключевое слово
        if c.isalpha() or c == '_':
            word = ''
            while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                word += source[i]
                i += 1
            if word in KEYWORDS:
                tokens.append(Token(KEYWORDS[word], word, строка))
            else:
                tokens.append(Token('IDENT', word, строка))
            continue
        # Операторы и символы
        if c == '-' and i+1 < len(source) and source[i+1] == '>':
            tokens.append(Token('ARROW', '->', строка))
            i += 2
            continue
        if c == '=' and i+1 < len(source) and source[i+1] == '=':
            tokens.append(Token('EQ', '==', строка))
            i += 2
            continue
        if c == '!' and i+1 < len(source) and source[i+1] == '=':
            tokens.append(Token('NEQ', '!=', строка))
            i += 2
            continue
        if c == '<' and i+1 < len(source) and source[i+1] == '=':
            tokens.append(Token('LTE', '<=', строка))
            i += 2
            continue
        if c == '>' and i+1 < len(source) and source[i+1] == '=':
            tokens.append(Token('GTE', '>=', строка))
            i += 2
            continue
        if c == '<':
            tokens.append(Token('LT', '<', строка))
            i += 1; continue
        if c == '>':
            tokens.append(Token('GT', '>', строка))
            i += 1; continue
        if c == '=':
            tokens.append(Token('ASSIGN', '=', строка))
            i += 1; continue
        if c == '+':
            tokens.append(Token('PLUS', '+', строка)); i += 1; continue
        if c == '-':
            tokens.append(Token('MINUS', '-', строка)); i += 1; continue
        if c == '*':
            tokens.append(Token('STAR', '*', строка)); i += 1; continue
        if c == '/':
            tokens.append(Token('SLASH', '/', строка)); i += 1; continue
        if c == '%':
            tokens.append(Token('PERCENT', '%', строка)); i += 1; continue
        if c == '(':
            tokens.append(Token('LPAREN', '(', строка)); i += 1; continue
        if c == ')':
            tokens.append(Token('RPAREN', ')', строка)); i += 1; continue
        if c == '{':
            tokens.append(Token('LBRACE', '{', строка)); i += 1; continue
        if c == '}':
            tokens.append(Token('RBRACE', '}', строка)); i += 1; continue
        if c == '[':
            tokens.append(Token('LBRACKET', '[', строка)); i += 1; continue
        if c == ']':
            tokens.append(Token('RBRACKET', ']', строка)); i += 1; continue
        if c == ',':
            tokens.append(Token('COMMA', ',', строка)); i += 1; continue
        if c == ':':
            tokens.append(Token('COLON', ':', строка)); i += 1; continue
        if c == '.':
            tokens.append(Token('DOT', '.', строка)); i += 1; continue
        # Неизвестный символ
        raise SyntaxError(f"Неизвестный символ '{c}' на строке {строка}")
    tokens.append(Token('EOF', None, строка))
    return tokens


# === ПАРСЕР ===

class Node:
    pass

class Num(Node):
    def __init__(self, v): self.v = v
class Str(Node):
    def __init__(self, v): self.v = v
class Bool(Node):
    def __init__(self, v): self.v = v
class Var(Node):
    def __init__(self, name): self.name = name
class List(Node):
    def __init__(self, items): self.items = items
class BinOp(Node):
    def __init__(self, op, l, r): self.op, self.l, self.r = op, l, r
class UnaryOp(Node):
    def __init__(self, op, val): self.op, self.val = op, val
class Assign(Node):
    def __init__(self, name, val): self.name, self.val = name, val
class LetDecl(Node):
    def __init__(self, name, val, тип=None): self.name, self.val, self.тип = name, val, тип
class Call(Node):
    def __init__(self, callee, args): self.callee, self.args = callee, args
class MethodCall(Node):
    def __init__(self, obj, name, args): self.obj, self.name, self.args = obj, name, args
class FieldAccess(Node):
    def __init__(self, obj, field): self.obj, self.field = obj, field
class If(Node):
    def __init__(self, cond, body, else_body=None): self.cond, self.body, self.else_body = cond, body, else_body
class For(Node):
    def __init__(self, var, iterable, body): self.var, self.iterable, self.body = var, iterable, body
class While(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body
class Loop(Node):
    def __init__(self, body): self.body = body
class Break(Node):
    pass
class Continue(Node):
    pass
class FuncDef(Node):
    def __init__(self, name, params, body, ret_type=None): self.name, self.params, self.body, self.ret_type = name, params, body, ret_type
class Return(Node):
    def __init__(self, val): self.val = val
class StructDef(Node):
    def __init__(self, name, fields, methods): self.name, self.fields, self.methods = name, fields, methods
class StructInit(Node):
    def __init__(self, name, fields): self.name, self.fields = name, fields
class Import(Node):
    def __init__(self, path): self.path = path
class Print(Node):
    def __init__(self, expr): self.expr = expr
class After(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t
    def check(self, тип):
        return self.peek().тип == тип
    def match(self, тип):
        if self.check(тип): return self.advance()
        return None
    def expect(self, тип):
        if self.check(тип): return self.advance()
        raise SyntaxError(f"Ожидался {тип}, получено {self.peek().тип} ('{self.peek().значение}') на строке {self.peek().строка}")
    def skip_newlines(self):
        while self.check('NEWLINE'): self.advance()

    def parse_program(self):
        stmts = []
        self.skip_newlines()
        while not self.check('EOF'):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return stmts

    def parse_statement(self):
        t = self.peek()
        if t.тип == 'LET': return self.parse_let()
        if t.тип == 'FUNC': return self.parse_func()
        if t.тип == 'IF': return self.parse_if()
        if t.тип == 'FOR': return self.parse_for()
        if t.тип == 'WHILE': return self.parse_while()
        if t.тип == 'LOOP': return self.parse_loop()
        if t.тип == 'BREAK': self.advance(); return Break()
        if t.тип == 'CONTINUE': self.advance(); return Continue()
        if t.тип == 'RETURN': return self.parse_return()
        if t.тип == 'STRUCT': return self.parse_struct()
        if t.тип == 'IMPORT': return self.parse_import()
        if t.тип == 'PRINT': return self.parse_print()
        if t.тип == 'AFTER': return self.parse_after()
        return self.parse_expr_or_assign()

    def parse_let(self):
        self.advance()  # пусть
        name = self.expect('IDENT').значение
        тип = None
        if self.match('COLON'):
            тип = self.expect('IDENT').значение
        self.expect('ASSIGN')
        val = self.parse_expr()
        return LetDecl(name, val, тип)

    def parse_func(self):
        self.advance()  # функция
        name = self.expect('IDENT').значение
        self.expect('LPAREN')
        params = []
        if not self.check('RPAREN'):
            while True:
                pname = self.expect('IDENT').значение
                ptype = None
                if self.match('COLON'):
                    ptype = self.expect('IDENT').значение
                params.append((pname, ptype))
                if not self.match('COMMA'): break
        self.expect('RPAREN')
        ret_type = None
        if self.match('ARROW'):
            ret_type = self.expect('IDENT').значение
        self.expect('LBRACE')
        self.skip_newlines()
        body = []
        while not self.check('RBRACE'):
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect('RBRACE')
        return FuncDef(name, params, body, ret_type)

    def parse_if(self):
        self.advance()  # если
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.skip_newlines()
        body = []
        while not self.check('RBRACE'):
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect('RBRACE')
        else_body = None
        self.skip_newlines()
        if self.check('ELSE'):
            self.advance()
            self.expect('LBRACE')
            self.skip_newlines()
            else_body = []
            while not self.check('RBRACE'):
                else_body.append(self.parse_statement())
                self.skip_newlines()
            self.expect('RBRACE')
        return If(cond, body, else_body)

    def parse_for(self):
        self.advance()  # для
        self.expect('LPAREN')
        # для (пусть i в [1, 2, 3]) или для (i в [1, 2, 3])
        if self.check('LET'):
            self.advance()  # пусть
        var = self.expect('IDENT').значение
        if self.check('IN'):
            self.advance()
            iterable = self.parse_expr()
            self.expect('RPAREN')
            self.expect('LBRACE')
            self.skip_newlines()
            body = []
            while not self.check('RBRACE'):
                body.append(self.parse_statement())
                self.skip_newlines()
            self.expect('RBRACE')
            return For(var, iterable, body)
        else:
            # для (иниц; условие; шаг)
            init = self.parse_expr_or_assign()
            self.expect('COMMA')
            cond = self.parse_expr()
            self.expect('COMMA')
            step = self.parse_expr_or_assign()
            self.expect('RPAREN')
            self.expect('LBRACE')
            self.skip_newlines()
            body = []
            while not self.check('RBRACE'):
                body.append(self.parse_statement())
                self.skip_newlines()
            self.expect('RBRACE')
            return For(var, cond, body)  # simplified

    def parse_while(self):
        self.advance()  # пока
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.skip_newlines()
        body = []
        while not self.check('RBRACE'):
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect('RBRACE')
        return While(cond, body)

    def parse_loop(self):
        self.advance()  # снова
        self.expect('LBRACE')
        self.skip_newlines()
        body = []
        while not self.check('RBRACE'):
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect('RBRACE')
        return Loop(body)

    def parse_return(self):
        self.advance()  # вернуть
        val = None
        if not self.check('NEWLINE') and not self.check('RBRACE') and not self.check('EOF'):
            val = self.parse_expr()
        return Return(val)

    def parse_struct(self):
        self.advance()  # структура
        name = self.expect('IDENT').значение
        self.expect('LBRACE')
        self.skip_newlines()
        fields = []
        methods = []
        while not self.check('RBRACE'):
            if self.check('FUNC'):
                methods.append(self.parse_func())
            else:
                fname = self.expect('IDENT').значение
                ftype = None
                if self.match('COLON'):
                    ftype = self.expect('IDENT').значение
                fields.append((fname, ftype))
            self.skip_newlines()
        self.expect('RBRACE')
        return StructDef(name, fields, methods)

    def parse_import(self):
        self.advance()  # импорт
        path = self.expect('STRING').значение
        return Import(path)

    def parse_print(self):
        self.advance()  # печатать
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        return Print(expr)

    def parse_after(self):
        self.advance()  # после
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.skip_newlines()
        body = []
        while not self.check('RBRACE'):
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect('RBRACE')
        return After(cond, body)

    def parse_expr_or_assign(self):
        expr = self.parse_expr()
        if self.check('ASSIGN'):
            self.advance()
            val = self.parse_expr()
            if isinstance(expr, Var):
                return Assign(expr.name, val)
            raise SyntaxError("Нельзя присвоить этому выражению")
        return expr

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.check('OR'):
            self.advance()
            right = self.parse_and()
            left = BinOp('or', left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.check('AND'):
            self.advance()
            right = self.parse_not()
            left = BinOp('and', left, right)
        return left

    def parse_not(self):
        if self.check('NOT'):
            self.advance()
            val = self.parse_not()
            return UnaryOp('not', val)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_add()
        while self.peek().тип in ('EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'):
            op = self.advance().тип
            right = self.parse_add()
            left = BinOp(op, left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().тип in ('PLUS', 'MINUS'):
            op = self.advance().тип
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().тип in ('STAR', 'SLASH', 'PERCENT'):
            op = self.advance().тип
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.check('MINUS'):
            self.advance()
            val = self.parse_unary()
            return UnaryOp('-', val)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.check('DOT'):
                self.advance()
                name = self.expect('IDENT').значение
                if self.check('LPAREN'):
                    self.advance()
                    args = []
                    if not self.check('RPAREN'):
                        while True:
                            args.append(self.parse_expr())
                            if not self.match('COMMA'): break
                    self.expect('RPAREN')
                    expr = MethodCall(expr, name, args)
                else:
                    expr = FieldAccess(expr, name)
            elif self.check('LPAREN'):
                self.advance()
                args = []
                if not self.check('RPAREN'):
                    while True:
                        args.append(self.parse_expr())
                        if not self.match('COMMA'): break
                self.expect('RPAREN')
                expr = Call(expr, args)
            elif self.check('LBRACE') and isinstance(expr, Var):
                self.advance()
                self.skip_newlines()
                fields = {}
                while not self.check('RBRACE'):
                    fname = self.expect('IDENT').значение
                    self.expect('COLON')
                    fval = self.parse_expr()
                    fields[fname] = fval
                    self.skip_newlines()
                    if not self.match('COMMA'):
                        break
                    self.skip_newlines()
                self.expect('RBRACE')
                expr = StructInit(expr.name, fields)
            else:
                break
        return expr

    def parse_primary(self):
        t = self.peek()
        if t.тип == 'NUMBER': self.advance(); return Num(t.значение)
        if t.тип == 'STRING': self.advance(); return Str(t.значение)
        if t.тип == 'TRUE': self.advance(); return Bool(True)
        if t.тип == 'FALSE': self.advance(); return Bool(False)
        if t.тип == 'IDENT': self.advance(); return Var(t.значение)
        if t.тип == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        if t.тип == 'LBRACKET':
            self.advance()
            items = []
            self.skip_newlines()
            if not self.check('RBRACKET'):
                while True:
                    items.append(self.parse_expr())
                    self.skip_newlines()
                    if not self.match('COMMA'): break
                    self.skip_newlines()
            self.expect('RBRACKET')
            return List(items)
        raise SyntaxError(f"Неожиданный токен {t.тип} ('{t.значение}') на строке {t.строка}")


# === ИНТЕРПРЕТАТОР ===

class RosicStruct:
    def __init__(self, name, fields, methods, env):
        self.name = name
        self.fields = fields
        self.methods = methods
        self.env = env
    def init(self, init_vals):
        obj = {}
        for fname, ftype in self.fields:
            obj[fname] = init_vals.get(fname, None)
        obj['__struct__'] = self
        return obj

class RosicFunc:
    def __init__(self, def_node, closure):
        self.def_node = def_node
        self.closure = closure

class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, val): self.val = val
class RosicError(Exception): pass

class Interpreter:
    def __init__(self):
        self.global_env = {}
        self.log_entries = []
        self.stop_file_active = False
        self.project_dir = Path('.').resolve()
        self.loaded_modules = set()

    def check_stop_file(self, project_dir):
        """Проверяет наличие .сфайл в проекте"""
        for f in Path(project_dir).glob('*.сфайл'):
            self.stop_file_active = True
            return True
        return False

    def log(self, msg, level='ИНФО'):
        entry = f"[{level}] {msg}"
        self.log_entries.append(entry)
        return entry

    def write_log(self, project_dir):
        """Записывает лог в .лог файл"""
        log_path = Path(project_dir) / 'росич.лог'
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.log_entries))

    def load_func_file(self, path):
        """Загружает функцию из .функц файла"""
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        tokens = lex(source)
        parser = Parser(tokens)
        stmts = parser.parse_program()
        return stmts

    def eval_program(self, stmts, env=None):
        if env is None: env = self.global_env
        for stmt in stmts:
            self.eval(stmt, env)

    def eval(self, node, env):
        if isinstance(node, Num): return node.v
        if isinstance(node, Str): return node.v
        if isinstance(node, Bool): return node.v
        if isinstance(node, Var):
            if node.name in env: return env[node.name]
            if node.name in self.global_env: return self.global_env[node.name]
            if node.name in BUILTINS: return BUILTINS[node.name]
            raise RosicError(f"Переменная '{node.name}' не определена")
        if isinstance(node, List):
            return [self.eval(i, env) for i in node.items]
        if isinstance(node, BinOp):
            return self.eval_binop(node, env)
        if isinstance(node, UnaryOp):
            val = self.eval(node.val, env)
            if node.op == '-': return -val
            if node.op == 'not': return not val
        if isinstance(node, LetDecl):
            val = self.eval(node.val, env)
            env[node.name] = val
            return None
        if isinstance(node, Assign):
            val = self.eval(node.val, env)
            env[node.name] = val
            return None
        if isinstance(node, Print):
            val = self.eval(node.expr, env)
            if isinstance(val, bool):
                print("правда" if val else "ложно")
            elif isinstance(val, float):
                if val == int(val):
                    print(f"{val:.1f}")
                else:
                    print(val)
            elif isinstance(val, dict) and '__struct__' in val:
                s = val['__struct__']
                fields = ', '.join(f"{k}: {v}" for k, v in val.items() if k != '__struct__')
                print(f"{s.name} {{ {fields} }}")
            else:
                print(val)
            return None
        if isinstance(node, If):
            cond = self.eval(node.cond, env)
            if cond:
                self.eval_program(node.body, env)
            elif node.else_body:
                self.eval_program(node.else_body, env)
            return None
        if isinstance(node, For):
            iterable = self.eval(node.iterable, env)
            for item in iterable:
                if self.stop_file_active:
                    break
                env[node.var] = item
                try:
                    self.eval_program(node.body, env)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None
        if isinstance(node, While):
            while self.eval(node.cond, env):
                if self.stop_file_active:
                    break
                try:
                    self.eval_program(node.body, env)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None
        if isinstance(node, Loop):
            while True:
                if self.stop_file_active:
                    break
                try:
                    self.eval_program(node.body, env)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None
        if isinstance(node, Break): raise BreakException()
        if isinstance(node, Continue): raise ContinueException()
        if isinstance(node, Return): raise ReturnException(self.eval(node.val, env) if node.val else None)
        if isinstance(node, FuncDef):
            func = RosicFunc(node, env)
            env[node.name] = func
            return None
        if isinstance(node, StructDef):
            s = RosicStruct(node.name, node.fields, node.methods, env)
            def make_init(s):
                def init(*args):
                    init_vals = {}
                    if len(args) == 1 and isinstance(args[0], dict):
                        init_vals = args[0]
                    obj = {}
                    for fname, ftype in s.fields:
                        obj[fname] = init_vals.get(fname, None)
                    obj['__struct__'] = s
                    for method in s.methods:
                        obj[method.name] = RosicFunc(method, env)
                    return obj
                return init
            env[node.name] = make_init(s)
            return None
        if isinstance(node, Call):
            callee = self.eval(node.callee, env)
            args = [self.eval(a, env) for a in node.args]
            if callable(callee):
                return callee(*args)
            if isinstance(callee, RosicFunc):
                return self.call_func(callee, args)
            raise RosicError(f"Вызов не-функции: {callee}")
        if isinstance(node, MethodCall):
            obj = self.eval(node.obj, env)
            method_name = node.name
            args = [self.eval(a, env) for a in node.args]
            if isinstance(obj, dict) and '__struct__' in obj:
                if method_name in obj:
                    func = obj[method_name]
                    if isinstance(func, RosicFunc):
                        func_env = dict(func.closure)
                        func_env['self'] = obj
                        return self.call_func(func, args, func_env)
                # struct methods
            # builtin methods on list, string etc
            if isinstance(obj, list):
                if method_name == 'длина': return len(obj)
                if method_name == 'добавить': obj.append(args[0]); return None
                if method_name == 'удалить': obj.pop(args[0]); return None
                if method_name == 'к_тексту': return str(obj)
            if isinstance(obj, str):
                if method_name == 'длина': return len(obj)
                if method_name == 'верх': return obj.upper()
                if method_name == 'низ': return obj.lower()
                if method_name == 'к_тексту': return obj
            raise RosicError(f"Метод '{method_name}' не найден")
        if isinstance(node, FieldAccess):
            obj = self.eval(node.obj, env)
            if isinstance(obj, dict):
                return obj.get(node.field, None)
            raise RosicError(f"Поле '{node.field}' не найдено")
        if isinstance(node, StructInit):
            constructor = self.eval(Var(node.name), env)
            init_vals = {}
            for fname, fval_node in node.fields.items():
                init_vals[fname] = self.eval(fval_node, env)
            if callable(constructor):
                return constructor(init_vals)
            raise RosicError(f"Структура '{node.name}' не определена")
        if isinstance(node, Import):
            return self.handle_import(node.path, env)
        if isinstance(node, After):
            cond = self.eval(node.cond, env)
            if cond:
                self.eval_program(node.body, env)
            return None
        return None

    def eval_binop(self, node, env):
        op = node.op
        l = self.eval(node.l, env)
        r = self.eval(node.r, env)
        if op == 'PLUS':
            if isinstance(l, str) or isinstance(r, str):
                return str(l) + str(r) if not (isinstance(l, str) and isinstance(r, str)) else l + r
            return l + r
        if op == 'MINUS': return l - r
        if op == 'STAR': return l * r
        if op == 'SLASH':
            if isinstance(l, int) and isinstance(r, int) and l % r == 0:
                return l // r
            return l / r
        if op == 'PERCENT': return l % r
        if op == 'EQ': return l == r
        if op == 'NEQ': return l != r
        if op == 'LT': return l < r
        if op == 'GT': return l > r
        if op == 'LTE': return l <= r
        if op == 'GTE': return l >= r
        if op == 'and': return l and r
        if op == 'or': return l or r

    def call_func(self, func, args, extra_env=None):
        func_env = dict(func.closure)
        if extra_env:
            func_env.update(extra_env)
        for i, (pname, ptype) in enumerate(func.def_node.params):
            if i < len(args):
                func_env[pname] = args[i]
            else:
                func_env[pname] = None
        try:
            self.eval_program(func.def_node.body, func_env)
        except ReturnException as e:
            return e.val
        return None

    def handle_import(self, path, env):
        """Обрабатывает импорт .rus, .функц и других модулей"""
        base = self.project_dir
        # Ищем файл: module.rus, module.рос, module.функц
        for ext in ['.rus', '.рос', '.функц']:
            full = base / (path + ext)
            if full.exists():
                if str(full) in self.loaded_modules:
                    return None  # уже загружен
                self.loaded_modules.add(str(full))
                self.log(f"Импорт модуля: {full}")
                with open(full, 'r', encoding='utf-8') as f:
                    source = f.read()
                tokens = lex(source)
                parser = Parser(tokens)
                stmts = parser.parse_program()
                self.eval_program(stmts, env)
                return None
        raise RosicError(f"Модуль '{path}' не найден")

    def run(self, filepath):
        filepath = Path(filepath).resolve()
        self.project_dir = filepath.parent

        # Проверяем .сфайл
        if self.check_stop_file(self.project_dir):
            self.log("Найден .сфайл — циклы будут остановлены", 'ПРЕДУПР')
            print("Внимание: найден .сфайл — циклы будут остановлены")

        # Проверяем расширение
        ext = filepath.suffix
        if ext == '.рос':
            self.log(f"Запуск главного файла: {filepath.name}")
        elif ext == '.rus':
            self.log(f"Запуск модуля: {filepath.name}")
        elif ext == '.функц':
            self.log(f"Загрузка функции: {filepath.name}")
        else:
            self.log(f"Неизвестный формат: {ext}", 'ПРЕДУПР')

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tokens = lex(source)
        parser = Parser(tokens)
        stmts = parser.parse_program()

        try:
            self.eval_program(stmts)
        except RosicError as e:
            print(f"Ошибка Росича: {e}")
            self.log(f"Ошибка: {e}", 'ОШИБКА')
        finally:
            self.write_log(self.project_dir)

BUILTINS = {
    'длина': lambda x: len(x) if not isinstance(x, dict) else len([k for k in x if k != '__struct__']),
    'к_тексту': lambda x: str(x),
    'диапазон': lambda *a: list(range(*a)) if len(a) > 1 else list(range(a[0])),
    'абсолют': lambda x: abs(x),
    'макс': lambda *a: max(a),
    'мин': lambda *a: min(a),
    'сумма': lambda x: sum(x),
    'целое': lambda x: int(x),
    'вещ': lambda x: float(x),
    'тип': lambda x: type(x).__name__,
}

# === REPL ===

def repl():
    print("Росич v0.2 — REPL (напишите 'выход' для выхода)")
    interp = Interpreter()
    env = interp.global_env
    while True:
        try:
            line = input("росич> ")
            if line.strip() == 'выход': break
            if not line.strip(): continue
            tokens = lex(line)
            parser = Parser(tokens)
            stmts = parser.parse_program()
            for stmt in stmts:
                result = interp.eval(stmt, env)
                if result is not None:
                    print(result)
        except Exception as e:
            print(f"Ошибка: {e}")

# === MAIN ===

def main():
    if len(sys.argv) < 2:
        repl()
        return
    filepath = sys.argv[1]
    interp = Interpreter()
    interp.run(filepath)

if __name__ == "__main__":
    main()
