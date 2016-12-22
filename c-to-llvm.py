# ------------------------------------------------------------------------------
# pycparser: c-to-c.py
#
# Example of using pycparser.c_generator, serving as a simplistic translator
# from C to AST and back to C.
#
#
# ------------------------------------------------------------------------------
from __future__ import print_function
import sys

import cparser
import llvmlite_generator


def translate_to_c(filename):
    ast = cparser.parse_file(filename)
    ast.show()
    generator = llvmlite_generator.LLVMGenerator()
    print(generator.generate(ast))


def _zz_test_translate():
    src = r'''

int main() {
    int i = 0;
    int j = 0;
    int k = 0;
    while (i < 8) {
       i = i + 1;

       if (i == 4) {
       j = i;

       continue;
       }

       if (i == 4) {
       j = i + 1;
       }
    }
    printf("%d", j);
    return 0;
}
'''
    parser = cparser.CParser()
    ast = parser.parse(src)
    ast.show(attrnames=True)

    generator = llvmlite_generator.LLVMGenerator()

    print(generator.generate(ast))


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        translate_to_c(sys.argv[1])
    else:
        _zz_test_translate()
