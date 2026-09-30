from typing import List

from .lexer import Token
from .ast import ASTNode


class ParserError(Exception):
    pass


# ---------------------------------------------------------
# DATA TYPES
# ---------------------------------------------------------

TYPE_TOKENS = {
    "INT",
    "FLOAT",
    "CHAR",
    "VOID"
}


# ---------------------------------------------------------
# PARSER
# ---------------------------------------------------------

class Parser:

    def __init__(self, tokens: List[Token]):

        self.tokens = tokens

        self.pos = 0

        # Used by Streamlit to visualize parsing
        self.trace = []

    # -----------------------------------------------------
    # CURRENT TOKEN
    # -----------------------------------------------------

    @property
    def current(self):

        return self.tokens[self.pos]

    # -----------------------------------------------------
    # LOOKAHEAD
    # -----------------------------------------------------

    def peek(self, offset=1):

        index = min(
            self.pos + offset,
            len(self.tokens) - 1
        )

        return self.tokens[index]

    # -----------------------------------------------------
    # RECORD PARSER STEP
    # -----------------------------------------------------

    def record(self, rule):

        self.trace.append({

            "Step": len(self.trace) + 1,

            "Grammar Rule": rule,

            "Lookahead": self.current.type,

            "Lexeme": self.current.lexeme,

            "Line": self.current.line

        })

    # -----------------------------------------------------
    # ADVANCE
    # -----------------------------------------------------

    def advance(self):

        token = self.current

        self.pos += 1

        return token

    # -----------------------------------------------------
    # CHECK
    # -----------------------------------------------------

    def check(self, token_type):

        return (
            self.current.type
            == token_type
        )

    # -----------------------------------------------------
    # MATCH
    # -----------------------------------------------------

    def match(self, *token_types):

        if self.current.type in token_types:

            return self.advance()

        return None

    # -----------------------------------------------------
    # EXPECT
    # -----------------------------------------------------

    def expect(
        self,
        token_type,
        message=None
    ):

        if not self.check(token_type):

            expected = (
                message
                or token_type
            )

            raise ParserError(

                f"Expected {expected}, "
                f"found {self.current.type} "
                f"({self.current.lexeme!r}) "
                f"at line {self.current.line}, "
                f"column {self.current.column}."

            )

        return self.advance()

    # -----------------------------------------------------
    # PROGRAM
    # -----------------------------------------------------

    def parse(self):

        self.record(
            "program → main_function EOF"
        )

        root = self.parse_main_function()

        self.expect("EOF")

        return root

    # -----------------------------------------------------
    # MAIN FUNCTION
    # -----------------------------------------------------

    def parse_main_function(self):

        self.record(
            "main_function → int main ( ) block"
        )

        self.expect(
            "INT",
            "int"
        )

        self.expect(
            "MAIN",
            "main"
        )

        self.expect(
            "LPAREN",
            "("
        )

        self.expect(
            "RPAREN",
            ")"
        )

        body = self.parse_block(
            is_function_body=True
        )

        return ASTNode(

            "Program",

            children=[

                ASTNode(

                    "Function",

                    "main",

                    [body],

                    self.tokens[0].line

                )

            ]

        )

    # -----------------------------------------------------
    # BLOCK
    # -----------------------------------------------------

    def parse_block(
        self,
        is_function_body=False
    ):

        self.record(
            "block → { declaration_or_statement* }"
        )

        start = self.expect(
            "LBRACE",
            "{"
        )

        children = []

        while (
            not self.check("RBRACE")
            and not self.check("EOF")
        ):

            if (
                self.current.type
                in TYPE_TOKENS
            ):

                children.append(
                    self.parse_declaration()
                )

            else:

                children.append(
                    self.parse_statement()
                )

        self.expect(
            "RBRACE",
            "}"
        )

        return ASTNode(

            "Block",

            children=children,

            line=start.line

        )

    # -----------------------------------------------------
    # DECLARATION
    # -----------------------------------------------------

    def parse_declaration(self):

        self.record(
            "declaration → type identifier initializer? ;"
        )

        type_token = self.advance()

        name = self.expect(
            "IDENTIFIER",
            "identifier"
        )

        children = []

        if self.match("ASSIGN"):

            children.append(
                self.parse_expression()
            )

        self.expect(
            "SEMICOLON",
            ";"
        )

        return ASTNode(

            "Declaration",

            value=(
                f"{type_token.lexeme} "
                f"{name.lexeme}"
            ),

            children=children,

            line=type_token.line

        )

    # -----------------------------------------------------
    # STATEMENTS
    # -----------------------------------------------------

    def parse_statement(self):

        if self.check("IF"):

            return self.parse_if()

        if self.check("WHILE"):

            return self.parse_while()

        if self.check("FOR"):

            return self.parse_for()

        if self.check("RETURN"):

            return self.parse_return()

        if self.check("LBRACE"):

            return self.parse_block()

        if self.check("SEMICOLON"):

            self.advance()

            return ASTNode(
                "EmptyStatement"
            )

        return self.parse_assignment()

    # -----------------------------------------------------
    # IF
    # -----------------------------------------------------

    def parse_if(self):

        self.record(
            "if_statement → if ( expression ) statement else? statement?"
        )

        token = self.expect("IF")

        self.expect("LPAREN")

        condition = (
            self.parse_expression()
        )

        self.expect("RPAREN")

        then_branch = (
            self.parse_statement()
        )

        children = [
            condition,
            then_branch
        ]

        if self.match("ELSE"):

            children.append(
                self.parse_statement()
            )

        return ASTNode(

            "IfStatement",

            children=children,

            line=token.line

        )

    # -----------------------------------------------------
    # WHILE
    # -----------------------------------------------------

    def parse_while(self):

        self.record(
            "while_statement → while ( expression ) statement"
        )

        token = self.expect("WHILE")

        self.expect("LPAREN")

        condition = (
            self.parse_expression()
        )

        self.expect("RPAREN")

        body = (
            self.parse_statement()
        )

        return ASTNode(

            "WhileStatement",

            children=[
                condition,
                body
            ],

            line=token.line

        )

    # -----------------------------------------------------
    # FOR
    # -----------------------------------------------------

    def parse_for(self):

        self.record(
            "for_statement → for ( assignment? ; expression? ; assignment? ) statement"
        )

        token = self.expect("FOR")

        self.expect("LPAREN")

        init = None
        condition = None
        update = None

        if not self.check("SEMICOLON"):

            init = self.parse_assignment(
                expect_semicolon=False
            )

        self.expect("SEMICOLON")

        if not self.check("SEMICOLON"):

            condition = (
                self.parse_expression()
            )

        self.expect("SEMICOLON")

        if not self.check("RPAREN"):

            update = self.parse_assignment(
                expect_semicolon=False
            )

        self.expect("RPAREN")

        body = (
            self.parse_statement()
        )

        children = [
            x
            for x in [
                init,
                condition,
                update,
                body
            ]
            if x is not None
        ]

        return ASTNode(

            "ForStatement",

            children=children,

            line=token.line

        )

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    def parse_return(self):

        self.record(
            "return_statement → return expression? ;"
        )

        token = self.expect("RETURN")

        children = []

        if not self.check("SEMICOLON"):

            children.append(
                self.parse_expression()
            )

        self.expect(
            "SEMICOLON",
            ";"
        )

        return ASTNode(

            "ReturnStatement",

            children=children,

            line=token.line

        )

    # -----------------------------------------------------
    # ASSIGNMENT
    # -----------------------------------------------------

    def parse_assignment(
        self,
        expect_semicolon=True
    ):

        self.record(
            "assignment → identifier = expression"
        )

        name = self.expect(
            "IDENTIFIER",
            "identifier"
        )

        operator = self.expect(
            "ASSIGN",
            "assignment operator '='"
        )

        expression = (
            self.parse_expression()
        )

        if expect_semicolon:

            self.expect(
                "SEMICOLON",
                ";"
            )

        return ASTNode(

            "Assignment",

            value=(
                f"{name.lexeme} "
                f"{operator.lexeme}"
            ),

            children=[
                expression
            ],

            line=name.line

        )

    # -----------------------------------------------------
    # EXPRESSION
    # -----------------------------------------------------

    def parse_expression(self):

        self.record(
            "expression → logical_or"
        )

        return self.parse_logical_or()

    # -----------------------------------------------------
    # LOGICAL OR
    # -----------------------------------------------------

    def parse_logical_or(self):

        node = (
            self.parse_logical_and()
        )

        while self.match("OR"):

            operator = (
                self.tokens[self.pos - 1]
            )

            right = (
                self.parse_logical_and()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # LOGICAL AND
    # -----------------------------------------------------

    def parse_logical_and(self):

        node = (
            self.parse_equality()
        )

        while self.match("AND"):

            operator = (
                self.tokens[self.pos - 1]
            )

            right = (
                self.parse_equality()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # EQUALITY
    # -----------------------------------------------------

    def parse_equality(self):

        node = (
            self.parse_relational()
        )

        while (
            self.check("EQ")
            or self.check("NE")
        ):

            operator = self.advance()

            right = (
                self.parse_relational()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # RELATIONAL
    # -----------------------------------------------------

    def parse_relational(self):

        node = (
            self.parse_additive()
        )

        while (
            self.check("LT")
            or self.check("LE")
            or self.check("GT")
            or self.check("GE")
        ):

            operator = self.advance()

            right = (
                self.parse_additive()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # ADDITION / SUBTRACTION
    # -----------------------------------------------------

    def parse_additive(self):

        node = (
            self.parse_term()
        )

        while (
            self.check("PLUS")
            or self.check("MINUS")
        ):

            operator = self.advance()

            right = (
                self.parse_term()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # MULTIPLICATION / DIVISION / MODULO
    # -----------------------------------------------------

    def parse_term(self):

        node = (
            self.parse_unary()
        )

        while (
            self.check("STAR")
            or self.check("SLASH")
            or self.check("MOD")
        ):

            operator = self.advance()

            right = (
                self.parse_unary()
            )

            node = ASTNode(

                "BinaryOp",

                operator.lexeme,

                [
                    node,
                    right
                ],

                operator.line

            )

        return node

    # -----------------------------------------------------
    # UNARY
    # -----------------------------------------------------

    def parse_unary(self):

        if self.match(
            "NOT",
            "PLUS",
            "MINUS"
        ):

            operator = (
                self.tokens[self.pos - 1]
            )

            operand = (
                self.parse_unary()
            )

            return ASTNode(

                "UnaryOp",

                operator.lexeme,

                [operand],

                operator.line

            )

        return self.parse_factor()

    # -----------------------------------------------------
    # FACTOR
    # -----------------------------------------------------

    def parse_factor(self):

        token = self.current

        # Identifier

        if token.type == "IDENTIFIER":

            self.advance()

            return ASTNode(

                "Identifier",

                token.lexeme,

                line=token.line

            )

        # Literals

        if token.type in {
            "INT_LITERAL",
            "FLOAT_LITERAL",
            "CHAR_LITERAL",
            "STRING_LITERAL"
        }:

            self.advance()

            return ASTNode(

                "Literal",

                token.lexeme,

                line=token.line

            )

        # Parentheses

        if self.match("LPAREN"):

            expression = (
                self.parse_expression()
            )

            self.expect(
                "RPAREN",
                ")"
            )

            return expression

        raise ParserError(

            f"Expected expression, "
            f"found {token.type} "
            f"({token.lexeme!r}) "
            f"at line {token.line}, "
            f"column {token.column}."

        )