cls
g++ -Wall -Wextra -Werror -std=c++11 -pedantic %1.cpp -o %1
%1
del /f %1.exe
