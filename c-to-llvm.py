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
int lessPrior[6][6] = {{1, 1, 1, 1, 0, 1}, {1, 1, 1, 1, 0, 1},
                      {0, 0, 1, 1, 0, 1}, {0, 0, 1, 1, 0, 1},
                      {0, 0, 0, 0, 0, 1}, {1, 1, 1, 1, 0, 1}};

int main() {
  int a = 1;
  int b = 2;
  int c = a + lessPrior[0][0];
  while (c < 4) {
      c = c + 1;
  }
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
