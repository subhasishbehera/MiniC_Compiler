import re
from dataclasses import dataclass
from typing import List


class LexerError(Exception):
    pass


@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    column: int

    def as_dict(self):
        return {
            "Line": self.line,
            "Column": self.column,
            "Token": self.type,
            "Lexeme": self.lexeme,
        }


# ---------------------------------------------------------
# MiniC KEYWORDS
# ---------------------------------------------------------

KEYWORDS = {
    "int": "INT",
    "float": "FLOAT",
    "char": "CHAR",
    "void": "VOID",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "return": "RETURN",
    "main": "MAIN",
}


# ---------------------------------------------------------
# TOKEN PATTERNS
# ---------------------------------------------------------

TOKEN_SPEC = [
    # Comments
    ("COMMENT", r"//[^\n]*"),
    ("MCOMMENT", r"/\*[\s\S]*?\*/"),

    # Literals
    ("FLOAT_LITERAL", r"(?:\d+\.\d+|\d+\.\d*[fF])"),
    ("INT_LITERAL", r"\d+"),
    ("STRING_LITERAL", r'"(?:\\.|[^"\\])*"'),
    ("CHAR_LITERAL", r"'(?:\\.|[^'\\])'"),

    # Multi-character operators
    ("EQ", r"=="),
    ("NE", r"!="),
    ("LE", r"<="),
    ("GE", r">="),
    ("AND", r"&&"),
    ("OR", r"\|\|"),
    ("PLUSPLUS", r"\+\+"),
    ("MINUSMINUS", r"--"),
    ("PLUS_ASSIGN", r"\+="),
    ("MINUS_ASSIGN", r"-="),
    ("MUL_ASSIGN", r"\*="),
    ("DIV_ASSIGN", r"/="),

    # Relational operators
    ("LT", r"<"),
    ("GT", r">"),

    # Arithmetic operators
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("MOD", r"%"),

    # Logical
    ("NOT", r"!"),

    # Assignment
    ("ASSIGN", r"="),

    # Brackets
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),

    # Delimiters
    ("SEMICOLON", r";"),
    ("COMMA", r","),

    # Identifier
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z_0-9]*"),

    # Whitespace
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r\f]+"),

    # Anything unknown
    ("UNKNOWN", r"."),
]


MASTER = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in TOKEN_SPEC
    )
)


# ---------------------------------------------------------
# LEXER
# ---------------------------------------------------------

class Lexer:

    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> List[Token]:

        tokens = []

        line = 1
        column = 1
        pos = 0

        while pos < len(self.source):

            match = MASTER.match(self.source, pos)

            if not match:
                raise LexerError(
                    f"Cannot tokenize input at "
                    f"line {line}, column {column}."
                )

            kind = match.lastgroup
            lexeme = match.group()

            # -----------------------------
            # NEW LINE
            # -----------------------------

            if kind == "NEWLINE":

                line += 1
                column = 1

                pos = match.end()

                continue

            # -----------------------------
            # IGNORE
            # -----------------------------

            if kind in {
                "SKIP",
                "COMMENT",
                "MCOMMENT"
            }:

                newlines = lexeme.count("\n")

                if newlines:

                    line += newlines

                    column = (
                        len(
                            lexeme.rsplit(
                                "\n",
                                1
                            )[-1]
                        )
                        + 1
                    )

                else:

                    column += len(lexeme)

                pos = match.end()

                continue

            # -----------------------------
            # UNKNOWN CHARACTER
            # -----------------------------

            if kind == "UNKNOWN":

                raise LexerError(
                    f"Unknown character {lexeme!r} "
                    f"at line {line}, column {column}."
                )

            # -----------------------------
            # KEYWORDS
            # -----------------------------

            if (
                kind == "IDENTIFIER"
                and lexeme in KEYWORDS
            ):

                kind = KEYWORDS[lexeme]

            # -----------------------------
            # CREATE TOKEN
            # -----------------------------

            tokens.append(
                Token(
                    type=kind,
                    lexeme=lexeme,
                    line=line,
                    column=column
                )
            )

            column += len(lexeme)

            pos = match.end()

        # EOF TOKEN

        tokens.append(
            Token(
                type="EOF",
                lexeme="EOF",
                line=line,
                column=column
            )
        )

        return tokens