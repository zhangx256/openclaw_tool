def ps_escape_double_quoted(s: str) -> str:
    return s.replace("`", "``").replace('"', '`"').replace("$", "`$")


def ps_dq(s: str) -> str:
    return f'"{ps_escape_double_quoted(s)}"'

