from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ASTNode:

    kind: str

    value: Any = None

    children: List["ASTNode"] = field(
        default_factory=list
    )

    line: int | None = None

    def to_dict(self):

        data = {
            "kind": self.kind
        }

        if self.value is not None:

            data["value"] = self.value

        if self.line is not None:

            data["line"] = self.line

        if self.children:

            data["children"] = [
                child.to_dict()
                for child in self.children
            ]

        return data


def ast_to_text(
    node: ASTNode,
    prefix: str = "",
    is_last: bool = True
) -> str:

    connector = (
        "└── "
        if is_last
        else "├── "
    )

    label = node.kind

    if node.value is not None:

        label += f": {node.value}"

    if node.line is not None:

        label += f"  [line {node.line}]"

    lines = [
        prefix + connector + label
    ]

    child_prefix = (
        prefix
        + ("    " if is_last else "│   ")
    )

    for i, child in enumerate(node.children):

        lines.append(
            ast_to_text(
                child,
                child_prefix,
                i == len(node.children) - 1
            )
        )

    return "\n".join(lines)