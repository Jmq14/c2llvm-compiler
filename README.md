# c2llvm-compiler

## Installation 

### install llvmlite
LLVM 3.8 is needed for the llvmlite we use in this project. You can build from srouce code, and for Mac OS user you can simply run `brew install homebrew/versions/llvm38`.

Then download llvmlite code: `git clone https://github.com/numba/llvmlite.git`

Build:

`cd llvmlite`

`sudo LLVM_CONFIG_PATH=/path/to/your/llvm/bin/llvm-config-3.8 python setup.py install`

### install PLY

`pip install PLY`

### download c2llvm-compiler

`git clone  https://github.com/Jmq14/c2llvm-compiler.git`

## Usage

NOTE: we don't support pre-process. You can use `clang -E` or  `gcc -E` or just delete all `#include` and `#define`

### Show AST Tree
`python c-to-ast.py [your c file]`

### Generate LLVM IR
`python c-to-llvm.py [your .c file] > [output .ll file]`

### Run LLVM IR
First edit the header of the .ll file and input your target datalayout and target triple. Use `clang -v` to check it. Sure you can simply delete these two lines since llvm will do it for you.(But don't leave it blank.)

Then,

`lli-3.8 [output .ll file]`
