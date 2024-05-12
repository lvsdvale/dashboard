#!/bin/bash

# Compilação dos programas em C
gcc -o api/get_process_data api/get_process_data.c -ljson-c
gcc -o api/cpu_mem_usage api/cpu_mem_usage.c -ljson-c

# Execução dos programas em C em segundo plano com sudo
echo '@Kgsrwv60' | sudo -S ./api/cpu_mem_usage &
echo '@Kgsrwv60' | sudo -S ./api/get_process_data &

# Execução do programa principal em Python
python3 main.py