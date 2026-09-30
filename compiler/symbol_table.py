from dataclasses import dataclass, field
from typing import Dict, List

from .ast import ASTNode


class SymbolTableError(Exception):
    pass


# ---------------------------------------------------------
# SYMBOL
# ---------------------------------------------------------

@dataclass
class Symbol:

    name: str

    type: str

    kind: str

    scope: str

    scope_level: int

    line: int

    initialized: bool = False


# ---------------------------------------------------------
# SCOPE
# ---------------------------------------------------------

@dataclass
class Scope:

    name: str

    level: int

    symbols: Dict[str, Symbol] = field(
        default_factory=dict
    )


# ---------------------------------------------------------
# SYMBOL TABLE MANAGER
# ---------------------------------------------------------

class SymbolTableManager:

    def __init__(self):

        # Active scope stack

        self.scope_stack: List[Scope] = [

            Scope(
                "global",
                0
            )

        ]

        # Keeps historical scopes
        # for visualization

        self.all_scopes: List[Scope] = [

            self.scope_stack[0]

        ]

        # Records symbol-table activity

        self.events = []

    # -----------------------------------------------------
    # CURRENT SCOPE
    # -----------------------------------------------------

    @property
    def current_scope(self):

        return self.scope_stack[-1]

    # -----------------------------------------------------
    # ENTER SCOPE
    # -----------------------------------------------------

    def enter_scope(self, name):

        scope = Scope(

            name,

            len(self.scope_stack)

        )

        self.scope_stack.append(
            scope
        )

        self.all_scopes.append(
            scope
        )

        self.events.append({

            "Action": "ENTER_SCOPE",

            "Name": name,

            "Scope": name,

            "Level": scope.level

        })

    # -----------------------------------------------------
    # EXIT SCOPE
    # -----------------------------------------------------

    def exit_scope(self):

        if len(self.scope_stack) == 1:

            return

        scope = (
            self.scope_stack.pop()
        )

        self.events.append({

            "Action": "EXIT_SCOPE",

            "Name": scope.name,

            "Scope": scope.name,

            "Level": scope.level

        })

    # -----------------------------------------------------
    # INSERT
    # -----------------------------------------------------

    def insert(
        self,
        name,
        type_name,
        kind,
        line,
        initialized=False
    ):

        scope = self.current_scope

        # Duplicate declaration

        if name in scope.symbols:

            raise SymbolTableError(

                f"Duplicate declaration "
                f"of '{name}' in scope "
                f"'{scope.name}' "
                f"at line {line}."

            )

        symbol = Symbol(

            name=name,

            type=type_name,

            kind=kind,

            scope=scope.name,

            scope_level=scope.level,

            line=line,

            initialized=initialized

        )

        scope.symbols[name] = symbol

        self.events.append({

            "Action": "INSERT",

            "Name": name,

            "Scope": scope.name,

            "Level": scope.level

        })

        return symbol

    # -----------------------------------------------------
    # LOOKUP
    # -----------------------------------------------------

    def lookup(
        self,
        name,
        line=None
    ):

        # Search from innermost
        # scope outward

        for scope in reversed(
            self.scope_stack
        ):

            if name in scope.symbols:

                symbol = (
                    scope.symbols[name]
                )

                self.events.append({

                    "Action": "LOOKUP",

                    "Name": name,

                    "Scope": symbol.scope,

                    "Level": symbol.scope_level

                })

                return symbol

        # Not found

        self.events.append({

            "Action": "LOOKUP_FAILED",

            "Name": name,

            "Scope": self.current_scope.name,

            "Level": self.current_scope.level

        })

        raise SymbolTableError(

            f"Identifier '{name}' "
            f"used before declaration"
            + (
                f" at line {line}."
                if line
                else "."
            )

        )

    # -----------------------------------------------------
    # BUILD TABLE FROM AST
    # -----------------------------------------------------

    def build_from_ast(
        self,
        root: ASTNode
    ):

        # main function

        function = root.children[0]

        self.insert(

            "main",

            "int",

            "function",

            function.line,

            True

        )

        # Enter main scope

        self.enter_scope("main")

        body = function.children[0]

        self._walk_block(
            body,
            create_scope=False
        )

        self.exit_scope()

    # -----------------------------------------------------
    # WALK BLOCK
    # -----------------------------------------------------

    def _walk_block(
        self,
        node,
        create_scope=True
    ):

        if create_scope:

            scope_name = (
                f"block_{len(self.all_scopes)}"
            )

            self.enter_scope(
                scope_name
            )

        for child in node.children:

            # -------------------------
            # DECLARATION
            # -------------------------

            if child.kind == "Declaration":

                parts = (
                    child.value.split(
                        maxsplit=1
                    )
                )

                type_name = parts[0]

                name = parts[1]

                initialized = bool(
                    child.children
                )

                self.insert(

                    name,

                    type_name,

                    "variable",

                    child.line,

                    initialized

                )

                for expression in (
                    child.children
                ):

                    self._walk_expression(
                        expression
                    )

            # -------------------------
            # NESTED BLOCK
            # -------------------------

            elif child.kind == "Block":

                self._walk_block(
                    child,
                    create_scope=True
                )

            # -------------------------
            # STATEMENT
            # -------------------------

            elif child.kind in {

                "Assignment",
                "IfStatement",
                "WhileStatement",
                "ForStatement",
                "ReturnStatement"

            }:

                self._walk_statement(
                    child
                )

        if create_scope:

            self.exit_scope()

    # -----------------------------------------------------
    # WALK STATEMENT
    # -----------------------------------------------------

    def _walk_statement(
        self,
        node
    ):

        # Assignment

        if node.kind == "Assignment":

            name = (
                node.value.split()[0]
            )

            self.lookup(
                name,
                node.line
            )

            if node.children:

                self._walk_expression(
                    node.children[0]
                )

        # If / While

        elif node.kind in {

            "IfStatement",
            "WhileStatement"

        }:

            if node.children:

                self._walk_expression(
                    node.children[0]
                )

            for child in node.children[1:]:

                if child.kind == "Block":

                    self._walk_block(
                        child,
                        create_scope=True
                    )

                else:

                    self._walk_statement(
                        child
                    )

        # For

        elif node.kind == "ForStatement":

            for child in node.children:

                if child.kind == "Block":

                    self._walk_block(
                        child,
                        create_scope=True
                    )

                elif child.kind == "Assignment":

                    self._walk_statement(
                        child
                    )

                else:

                    self._walk_expression(
                        child
                    )

        # Return

        elif node.kind == "ReturnStatement":

            for child in node.children:

                self._walk_expression(
                    child
                )

        # Block

        elif node.kind == "Block":

            self._walk_block(
                node,
                create_scope=True
            )

    # -----------------------------------------------------
    # WALK EXPRESSION
    # -----------------------------------------------------

    def _walk_expression(
        self,
        node
    ):

        if node.kind == "Identifier":

            self.lookup(
                node.value,
                node.line
            )

        for child in node.children:

            self._walk_expression(
                child
            )

    # -----------------------------------------------------
    # SYMBOL DATA
    # -----------------------------------------------------

    def get_all_symbols(self):

        rows = []

        for scope in self.all_scopes:

            for symbol in (
                scope.symbols.values()
            ):

                rows.append({

                    "Name": symbol.name,

                    "Type": symbol.type,

                    "Kind": symbol.kind,

                    "Scope": symbol.scope,

                    "Level": symbol.scope_level,

                    "Line": symbol.line,

                    "Initialized":
                        "Yes"
                        if symbol.initialized
                        else "No"

                })

        return rows

    # -----------------------------------------------------
    # SCOPE DATA
    # -----------------------------------------------------

    def get_scopes(self):

        return [

            {

                "Scope": scope.name,

                "Level": scope.level,

                "Symbols":
                    len(scope.symbols),

                "Identifiers":
                    ", ".join(
                        scope.symbols.keys()
                    )
                    or "—"

            }

            for scope in self.all_scopes

        ]

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    def get_events(self):

        return self.events