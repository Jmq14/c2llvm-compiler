# c2llvm-compiler

## install llvmpy
From official document of llvmpy, building llvm-3.3 from source code is recommended, though many problems would be invoked on mac OS. Please use `brew install homebrew/versions/llvm33` (remind: not the up-to-date version of llvm but 3.3 or 3.2) instead and follw the instructions below (for mac OS only). 

`git clone https://github.com/llvmpy/llvmpy.git`

`cd llvmpy`

`sudo LLVM_CONFIG_PATH=/usr/local/Cellar/llvm33/3.3_1/bin/llvm-config-3.3 python setup.py install`

And run test in python shell (remind: not in the llvmpy source directory).

`import llvm`

`llvm.test()`
