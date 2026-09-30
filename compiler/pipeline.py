from .lexer import (
    Lexer,
    LexerError
)

from .parser import (
    Parser,
    ParserError
)

from .symbol_table import (
    SymbolTableManager,
    SymbolTableError
)

from .ast import ast_to_text


def run_pipeline(source: str):

    result = {

        "success": False,

        "source": source,

        "tokens": [],

        "parser_trace": [],

        "ast": None,

        "ast_text": "",

        "symbols": [],

        "scopes": [],

        "symbol_events": [],

        "error": None,

        "error_stage": None

    }

    # =====================================================
    # STAGE 1
    # LEXICAL ANALYSIS
    # =====================================================

    try:

        tokens = Lexer(
            source
        ).tokenize()

        result["tokens"] = [

            token.as_dict()

            for token in tokens

        ]

    except LexerError as exc:

        result["error_stage"] = (
            "Lexical Analysis"
        )

        result["error"] = str(exc)

        return result

    # =====================================================
    # STAGE 2
    # SYNTAX ANALYSIS
    # =====================================================

    try:

        parser = Parser(
            tokens
        )

        ast = parser.parse()

        result["parser_trace"] = (
            parser.trace
        )

        result["ast"] = (
            ast.to_dict()
        )

        result["ast_text"] = (
            ast_to_text(ast)
        )

    except ParserError as exc:

        result["error_stage"] = (
            "Syntax Analysis"
        )

        result["error"] = str(exc)

        result["parser_trace"] = (
            parser.trace
        )

        return result

    # =====================================================
    # STAGE 3
    # SYMBOL TABLE
    # =====================================================

    try:

        manager = (
            SymbolTableManager()
        )

        manager.build_from_ast(
            ast
        )

        result["symbols"] = (
            manager.get_all_symbols()
        )

        result["scopes"] = (
            manager.get_scopes()
        )

        result["symbol_events"] = (
            manager.get_events()
        )

    except SymbolTableError as exc:

        result["error_stage"] = (
            "Symbol Table"
        )

        result["error"] = str(exc)

        result["symbols"] = (
            manager.get_all_symbols()
        )

        result["scopes"] = (
            manager.get_scopes()
        )

        result["symbol_events"] = (
            manager.get_events()
        )

        return result

    # =====================================================
    # SUCCESS
    # =====================================================

    result["success"] = True

    return result