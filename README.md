# c2llvm-compiler

## Installtion 

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

### Show AST Tree
TODO

### Generate LLVM IR
TODO
