mkdir tmp
mkdir tmp/$1
pypy mesi_sim.py WEATHER $1 1024 64 > tmp/$1/1 &
pypy mesi_sim.py WEATHER $1 2048 64 > tmp/$1/2 &
pypy mesi_sim.py WEATHER $1 4096 64 > tmp/$1/3 
pypy mesi_sim.py WEATHER $1 8192 64 > tmp/$1/4 &
pypy mesi_sim.py WEATHER $1 16384 64 > tmp/$1/5 &
pypy mesi_sim.py WEATHER $1 32768 64 > tmp/$1/6 
