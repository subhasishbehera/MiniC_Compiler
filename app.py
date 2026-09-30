import streamlit as st
import pandas as pd

from compiler.pipeline import run_pipeline


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="MiniC Compiler Visualizer",

    page_icon="⚙️",

    layout="wide",

    initial_sidebar_state="expanded"

)


# =========================================================
# DEFAULT MINIC PROGRAM
# =========================================================

DEFAULT_CODE = """int main() {

    int a = 10;
    float b = 20.5;
    int c;

    c = a + 5 * 2;

    if (c > 10) {

        int x = c;

        b = b + x;
    }

    while (c < 30) {

        c = c + 1;
    }

    return c;
}"""


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {

        padding-top: 1.5rem;

        padding-bottom: 3rem;

    }

    .hero {

        padding: 1.5rem;

        border-radius: 18px;

        border: 1px solid
        rgba(128,128,128,.25);

        background:
        linear-gradient(
            135deg,
            rgba(99,102,241,.12),
            rgba(14,165,233,.08)
        );

        margin-bottom: 1.5rem;

    }

    .stage-card {

        padding: 1rem;

        border-radius: 14px;

        border: 1px solid
        rgba(128,128,128,.25);

        min-height: 145px;

    }

    .stage-number {

        font-size: .75rem;

        font-weight: 700;

        opacity: .65;

        letter-spacing: .08em;

    }

    .stage-title {

        font-size: 1.05rem;

        font-weight: 750;

        margin-top: .3rem;

    }

    .stage-desc {

        font-size: .85rem;

        opacity: .75;

        margin-top: .4rem;

    }

    .arrow {

        text-align: center;

        font-size: 1.8rem;

        padding-top: 2.2rem;

        opacity: .6;

    }

    .success-box {

        padding: 1rem;

        border-radius: 12px;

        border: 1px solid
        rgba(34,197,94,.35);

        background:
        rgba(34,197,94,.08);

        margin-bottom: 1rem;

    }

    .error-box {

        padding: 1rem;

        border-radius: 12px;

        border: 1px solid
        rgba(239,68,68,.35);

        background:
        rgba(239,68,68,.08);

        margin-bottom: 1rem;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            ⚙️ MiniC Compiler
            <br>
            Front-End Visualizer
        </h1>

        <p>

        Enter MiniC source code and visualize
        how the compiler processes it:

        <b>
        Lexical Analysis
        →
        Syntax Analysis
        →
        AST
        →
        Symbol Table
        </b>

        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "Compiler Pipeline"
    )

    st.markdown(
        """
        ### 1. Lexical Analysis

        Source characters
        → Tokens

        ### 2. Syntax Analysis

        Tokens
        → Grammar

        ### 3. AST

        Grammar structure
        → Tree

        ### 4. Symbol Table

        Identifiers
        → Attributes

        ### 5. Scope Management

        Enter / Exit / Lookup
        """
    )

    st.divider()

    st.subheader(
        "Current Project Scope"
    )

    st.success(
        "First 50% — Compiler Front-End"
    )

    st.caption(
        """
        Current implementation:

        Lexical Analysis
        → Syntax Analysis
        → AST
        → Symbol Table

        Later stages can include:

        Semantic Analysis
        → TAC
        → Optimization
        → Code Generation
        """
    )


# =========================================================
# INPUT SECTION
# =========================================================

st.subheader(
    "1. Enter MiniC Source Code"
)

input_col, info_col = st.columns(
    [1.7, 1]
)


# ---------------------------------------------------------
# CODE EDITOR
# ---------------------------------------------------------

with input_col:

    source = st.text_area(

        "MiniC Program",

        value=DEFAULT_CODE,

        height=450,

        key="source_code",

        label_visibility="collapsed",

        placeholder=(
            "Write your MiniC code here..."
        )

    )


# ---------------------------------------------------------
# HELP PANEL
# ---------------------------------------------------------

with info_col:

    st.markdown(
        "### Supported MiniC Features"
    )

    st.markdown(
        """
        **Data types**

        - `int`
        - `float`
        - `char`

        **Statements**

        - declarations
        - assignments
        - `if`
        - `else`
        - `while`
        - `for`
        - `return`

        **Expressions**

        - `+`
        - `-`
        - `*`
        - `/`
        - `%`
        - `<`
        - `>`
        - `<=`
        - `>=`
        - `==`
        - `!=`
        - `&&`
        - `||`
        - `!`

        **Scopes**

        - function scope
        - nested block scope
        """
    )

    st.markdown(
        "### Example"
    )

    st.code(
        """int main() {
    int x = 10;
    int y;

    y = x + 5;

    return y;
}""",
        language="c"
    )


# =========================================================
# COMPILE BUTTON
# =========================================================

compile_clicked = st.button(

    "▶ Compile & Visualize",

    type="primary",

    use_container_width=True

)


# =========================================================
# RUN PIPELINE
# =========================================================

if compile_clicked:

    if not source.strip():

        st.session_state["result"] = {

            "success": False,

            "error_stage": "Input",

            "error": (
                "Please enter a MiniC program."
            ),

            "tokens": [],

            "parser_trace": [],

            "ast": None,

            "ast_text": "",

            "symbols": [],

            "scopes": [],

            "symbol_events": []

        }

    else:

        st.session_state[
            "result"
        ] = run_pipeline(
            source
        )


# =========================================================
# GET RESULT
# =========================================================

result = st.session_state.get(
    "result"
)


if result is None:

    st.info(
        """
        Enter MiniC code above and
        click **Compile & Visualize**
        to see the compiler pipeline.
        """
    )

    st.stop()


# =========================================================
# STATUS
# =========================================================

if result.get("success"):

    st.markdown(
        """
        <div class="success-box">

        ✅ <b>
        Compilation Front-End Successful
        </b>

        <br>

        Lexical Analysis →
        Syntax Analysis →
        AST →
        Symbol Table

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="error-box">

        ❌ <b>
        {result.get("error_stage", "Error")}
        </b>

        <br><br>

        {result.get("error", "Unknown error")}

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PIPELINE VISUALIZATION
# =========================================================

st.subheader(
    "2. Compiler Pipeline"
)

pipeline_columns = st.columns(
    [
        1,
        .18,
        1,
        .18,
        1,
        .18,
        1
    ]
)


stages = [

    (
        "01",
        "Lexical Analysis",
        "Source characters → Tokens"
    ),

    (
        "02",
        "Syntax Analysis",
        "Tokens → Grammar"
    ),

    (
        "03",
        "AST",
        "Grammar → Tree"
    ),

    (
        "04",
        "Symbol Table",
        "Identifiers → Attributes"
    )

]


for i, stage in enumerate(stages):

    with pipeline_columns[i * 2]:

        st.markdown(

            f"""
            <div class="stage-card">

                <div class="stage-number">

                    {stage[0]}

                </div>

                <div class="stage-title">

                    {stage[1]}

                </div>

                <div class="stage-desc">

                    {stage[2]}

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )

    if i < 3:

        with pipeline_columns[
            i * 2 + 1
        ]:

            st.markdown(
                '<div class="arrow">→</div>',
                unsafe_allow_html=True
            )


# =========================================================
# METRICS
# =========================================================

tokens = result.get(
    "tokens",
    []
)

parser_trace = result.get(
    "parser_trace",
    []
)

symbols = result.get(
    "symbols",
    []
)

scopes = result.get(
    "scopes",
    []
)


metric1, metric2, metric3, metric4, metric5 = st.columns(5)


metric1.metric(
    "Tokens",
    max(
        len(tokens) - 1,
        0
    )
)


metric2.metric(
    "Parser Steps",
    len(parser_trace)
)


metric3.metric(
    "Identifiers",
    len(symbols)
)


metric4.metric(
    "Scopes",
    len(scopes)
)


metric5.metric(
    "Pipeline",
    "PASS"
    if result.get("success")
    else "STOP"
)


# =========================================================
# OUTPUT TABS
# =========================================================

st.subheader(
    "3. Step-by-Step Visual Output"
)


tab_tokens, tab_parser, tab_symbol, tab_scope, tab_summary = st.tabs(

    [
        "🔤 1. Tokens",

        "🌳 2. Syntax / AST",

        "📋 3. Symbol Table",

        "🔐 4. Scope Events",

        "📊 5. Pipeline Summary"
    ]

)


# =========================================================
# TAB 1 — TOKENS
# =========================================================

with tab_tokens:

    st.markdown(
        "## Lexical Analysis"
    )

    st.caption(
        """
        The lexical analyzer scans the source
        from left to right and converts lexemes
        into tokens.
        """
    )

    if tokens:

        token_df = pd.DataFrame(
            tokens
        )

        display_df = token_df[
            token_df["Token"] != "EOF"
        ].copy()

        st.dataframe(

            display_df,

            use_container_width=True,

            hide_index=True,

            height=450

        )

        st.markdown(
            "### Token Distribution"
        )

        counts = (

            display_df[
                "Token"
            ]

            .value_counts()

            .rename_axis(
                "Token"
            )

            .reset_index(
                name="Count"
            )

        )

        st.bar_chart(
            counts.set_index(
                "Token"
            )
        )

        with st.expander(
            "Show Raw Token Stream"
        ):

            st.code(

                " → ".join(

                    f"{row.Token}"
                    f"({row.Lexeme})"

                    for row
                    in display_df.itertuples()

                )

            )


# =========================================================
# TAB 2 — PARSER + AST
# =========================================================

with tab_parser:

    st.markdown(
        "## Syntax Analysis"
    )

    st.caption(
        """
        The recursive-descent parser checks
        whether the token sequence follows
        the MiniC grammar and constructs
        an Abstract Syntax Tree.
        """
    )

    if parser_trace:

        st.markdown(
            "### Parser Trace"
        )

        st.dataframe(

            pd.DataFrame(
                parser_trace
            ),

            use_container_width=True,

            hide_index=True,

            height=350

        )

    if result.get(
        "ast_text"
    ):

        st.markdown(
            "### Abstract Syntax Tree"
        )

        st.code(

            result[
                "ast_text"
            ],

            language="text"

        )

    if result.get("ast"):

        with st.expander(
            "View AST as JSON"
        ):

            st.json(
                result["ast"]
            )


# =========================================================
# TAB 3 — SYMBOL TABLE
# =========================================================

with tab_symbol:

    st.markdown(
        "## Symbol Table Management"
    )

    st.caption(
        """
        Each declared identifier is stored
        with attributes such as its type,
        kind, scope and declaration line.
        """
    )

    if symbols:

        st.dataframe(

            pd.DataFrame(
                symbols
            ),

            use_container_width=True,

            hide_index=True

        )

    else:

        st.info(
            "No symbols were generated."
        )

    st.markdown(
        "### Scope Overview"
    )

    if scopes:

        st.dataframe(

            pd.DataFrame(
                scopes
            ),

            use_container_width=True,

            hide_index=True

        )


# =========================================================
# TAB 4 — SCOPE EVENTS
# =========================================================

with tab_scope:

    st.markdown(
        "## Scope & Symbol Events"
    )

    st.caption(
        """
        This makes symbol-table activity visible:
        entering scopes, inserting identifiers,
        looking up identifiers and exiting scopes.
        """
    )

    events = result.get(
        "symbol_events",
        []
    )

    if events:

        event_df = pd.DataFrame(
            events
        )

        st.dataframe(

            event_df,

            use_container_width=True,

            hide_index=True,

            height=420

        )

        st.markdown(
            "### Event Summary"
        )

        action_counts = (

            event_df[
                "Action"
            ]

            .value_counts()

            .rename_axis(
                "Action"
            )

            .reset_index(
                name="Count"
            )

        )

        st.bar_chart(

            action_counts.set_index(
                "Action"
            )

        )

    else:

        st.info(
            "No symbol-table events generated."
        )


# =========================================================
# TAB 5 — PIPELINE SUMMARY
# =========================================================

with tab_summary:

    st.markdown(
        "## End-to-End Pipeline"
    )

    stage_rows = [

        {

            "Stage":
                "Lexical Analysis",

            "Input":
                "Source Code",

            "Output":
                f"{max(len(tokens)-1, 0)} tokens",

            "Status":
                "PASS"
                if tokens
                else "STOP"

        },

        {

            "Stage":
                "Syntax Analysis",

            "Input":
                "Token Stream",

            "Output":
                "AST + Parser Trace"
                if result.get("ast")
                else "—",

            "Status":
                "PASS"
                if result.get("ast")
                else "STOP"

        },

        {

            "Stage":
                "Symbol Table",

            "Input":
                "AST",

            "Output":
                f"{len(symbols)} identifiers / "
                f"{len(scopes)} scopes",

            "Status":

                "PASS"
                if result.get("success")
                else (
                    "STOP"
                    if result.get(
                        "error_stage"
                    )
                    == "Symbol Table"
                    else "—"
                )

        }

    ]

    st.dataframe(

        pd.DataFrame(
            stage_rows
        ),

        use_container_width=True,

        hide_index=True

    )

    st.markdown(
        "### Source Code Submitted"
    )

    st.code(
        source,
        language="c"
    )

    if not result.get(
        "success"
    ):

        st.warning(

            f"""
            Pipeline stopped at
            **{result.get("error_stage")}**.

            Fix the error and compile again.
            """

        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    """
    MiniC Compiler Front-End Visualizer
    • Lexical Analysis
    → Syntax Analysis
    → AST
    → Symbol Table
    """
)