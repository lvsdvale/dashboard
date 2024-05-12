#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>
#include <unistd.h>

#define CPU_USAGE_INTERVAL 5

int main() {
    int i;
    char line[1024];
    FILE *fp;
    float cpu_usage, prev_cpu_usage = 0.0;
    float mem_usage;

    json_object *jobj = json_object_new_object();

    while (1) {
        // Lê o arquivo /proc/stat para obter informações sobre o uso de CPU
        fp = fopen("/proc/stat", "r");
        if (fp == NULL) {
            perror("Erro ao abrir /proc/stat");
            exit(1);
        }

        while (fgets(line, 1024, fp)!= NULL) {
            if (strncmp(line, "cpu ", 4) == 0) {
                int user, nice, system, idle;
                sscanf(line, "cpu %d %d %d %d", &user, &nice, &system, &idle);
                cpu_usage = (user + nice + system) * 100.0 / (user + nice + system + idle);
                break;
            }
        }

        fclose(fp);

        // Calcula a variação do uso de CPU
        cpu_usage = (cpu_usage - prev_cpu_usage) / CPU_USAGE_INTERVAL;
        prev_cpu_usage = cpu_usage;

        // Lê o arquivo /proc/meminfo para obter informações sobre o uso de memória
        fp = fopen("/proc/meminfo", "r");
        if (fp == NULL) {
            perror("Erro ao abrir /proc/meminfo");
            exit(1);
        }

        int total_memory, free_memory;
        while (fgets(line, 1024, fp)!= NULL) {
            if (strncmp(line, "MemTotal:", 9) == 0) {
                sscanf(line, "MemTotal: %d kB", &total_memory);
            } else if (strncmp(line, "MemFree:", 8) == 0) {
                sscanf(line, "MemFree: %d kB", &free_memory);
            }
        }

        fclose(fp);

        // Calcula o uso de memória
        mem_usage = (total_memory - free_memory) * 100.0 / total_memory;

        // Adiciona os dados ao objeto JSON
        json_object *jcpu = json_object_new_double(cpu_usage);
        json_object *jmem = json_object_new_double(mem_usage);
        json_object_object_add(jobj, "cpu_usage", jcpu);
        json_object_object_add(jobj, "mem_usage", jmem);

        // Salva o objeto JSON em um arquivo
        FILE *fp_json = fopen("cpu_mem.json", "w");
        if (fp_json == NULL) {
            perror("Erro ao abrir data.json");
            exit(1);
        }
        fprintf(fp_json, "%s", json_object_to_json_string(jobj));
        fclose(fp_json);

        // Imprime os resultados
        printf("CPU usage: %.2f%%\n", cpu_usage);
        printf("Memory usage: %.2f%%\n", mem_usage);

        // Aguarda 5 segundos
        sleep(CPU_USAGE_INTERVAL);
    }

    json_object_put(jobj);

    return 0;
}