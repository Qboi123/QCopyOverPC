import os

from QCompiler.qcompiler import QCompilerEXE

compiler = QCompilerEXE(
    ["venv", ".idea", ".git", ".gitignore", ".gitattributes", "echoclient.py", "echoserver.py", "hello.txt",
     "build", "build.py", "obj", "bin"],
    icon="", main_folder=os.getcwd(), main_file="copyoverpc.py", hidden_imports=["_tkinter", "pkg_resources",
                                                                                 "pkg_resources.py2_warn"],
    one_file=True, hide_console=True)
compiler.reindex()
compiler.compile(compiler.get_command(compiler.get_args()))
