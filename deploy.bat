@GOTO:fondo
open intranet.rgm.it
rgm
Ahviy9bi

mkdir intranet.rgm.it/pip/cstruct
cd intranet.rgm.it/pip/cstruct

lcd dist

binary
mput *.whl

disconnect
bye

:fondo
@echo off

python setup.py bdist_wheel

rem ftp -s:ftpscript.txt.

ftp -i -s:"%~f0"
