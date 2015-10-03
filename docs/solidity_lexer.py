from pygments.lexers.c_cpp import CFamilyLexer
from pygments.lexer import (
    words,
)
from pygments.token import (
    Keyword,
)


class SolidityLexer(CFamilyLexer):
    name = "Solidity"
    aliases = ["solidity", "sol"]
    filenames = ["*.sol"]

    tokens = {
        'address': [
            (r'address', Keyword.Type),
            #(words(('address',)), Keyword.Type),
        ]
    }
