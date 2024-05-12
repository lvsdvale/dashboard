#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <string.h>
#include <sys/time.h>
#include <json-c/json.h>

#define BUF_SIZE 1024
#define JSON_UPDATE_INTERVAL 5 // Intervalo de atualização em segundos

// Estrutura para armazenar as informações de memória do sistema
typedef struct {
    unsigned long long total_ram;
    unsigned long long free_ram;
    unsigned long long total_swap;
    unsigned long long free_swap;
    double ram_usage_percentage;
    double swap_usage_percentage;
} SystemMemoryInfo;

// Estrutura para armazenar as informações de memória de um processo
typedef struct {
    pid_t pid;
    unsigned long long total_memory;
    unsigned long long code_memory;
    unsigned long long heap_memory;
    unsigned long long stack_memory;
    unsigned long long total_pages;
    unsigned long long code_pages;
    unsigned long long heap_pages;
    unsigned long long stack_pages;
} ProcessMemoryInfo;

// Função para obter as informações de memória do sistema
void get_system_memory_info(SystemMemoryInfo *sys_mem_info) {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (fp != NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp) != NULL) {
            if (strstr(line, "MemTotal:") != NULL) {
                sscanf(line, "MemTotal: %llu kB", &sys_mem_info->total_ram);
            } else if (strstr(line, "MemFree:") != NULL) {
                sscanf(line, "MemFree: %llu kB", &sys_mem_info->free_ram);
            } else if (strstr(line, "SwapTotal:") != NULL) {
                sscanf(line, "SwapTotal: %llu kB", &sys_mem_info->total_swap);
            } else if (strstr(line, "SwapFree:") != NULL) {
                sscanf(line, "SwapFree: %llu kB", &sys_mem_info->free_swap);
            }
        }
        fclose(fp);
    }

    sys_mem_info->ram_usage_percentage = (double)(sys_mem_info->total_ram - sys_mem_info->free_ram) / sys_mem_info->total_ram * 100.0;
    sys_mem_info->swap_usage_percentage = (double)(sys_mem_info->total_swap - sys_mem_info->free_swap) / sys_mem_info->total_swap * 100.0;
}

// Função para obter as informações de memória de um processo
void get_process_memory_info(pid_t pid, ProcessMemoryInfo *proc_mem_info) {
    char path[256];
    sprintf(path, "/proc/%d/status", pid);
    FILE *fp = fopen(path, "r");
    if (fp != NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp) != NULL) {
            if (strstr(line, "VmSize:") != NULL) {
                sscanf(line, "VmSize: %llu kB", &proc_mem_info->total_memory);
            } else if (strstr(line, "VmExe:") != NULL) {
                sscanf(line, "VmExe: %llu kB", &proc_mem_info->code_memory);
            } else if (strstr(line, "VmData:") != NULL) {
                sscanf(line, "VmData: %llu kB", &proc_mem_info->heap_memory);
            } else if (strstr(line, "VmStk:") != NULL) {
                sscanf(line, "VmStk: %llu kB", &proc_mem_info->stack_memory);
            }
        }
        fclose(fp);
    }

    sprintf(path, "/proc/%d/smaps", pid);
    fp = fopen(path, "r");
    if (fp != NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp) != NULL) {
            if (strstr(line, "Size:") != NULL) {
                sscanf(line, "Size: %llu kB", &proc_mem_info->total_pages);
            } else if (strstr(line, "KernelPageSize:") != NULL) {
                sscanf(line, "KernelPageSize: %llu", &proc_mem_info->code_pages);
            } else if (strstr(line, "MMUPageSize:") != NULL) {
                sscanf(line, "MMUPageSize: %llu", &proc_mem_info->heap_pages);
            } else if (strstr(line, "AnonHugePages:") != NULL) {
                sscanf(line, "AnonHugePages: %llu", &proc_mem_info->stack_pages);
            }
        }
        fclose(fp);
    }
}

// Função para criar o JSON de informações de memória do sistema
json_object* create_system_memory_json(const SystemMemoryInfo *sys_mem_info) {
    json_object *jobj = json_object_new_object();
    json_object_object_add(jobj, "total_ram", json_object_new_uint64(sys_mem_info->total_ram));
    json_object_object_add(jobj, "free_ram", json_object_new_uint64(sys_mem_info->free_ram));
    json_object_object_add(jobj, "ram_usage_percentage", json_object_new_double(sys_mem_info->ram_usage_percentage));
    json_object_object_add(jobj, "total_swap", json_object_new_uint64(sys_mem_info->total_swap));
    json_object_object_add(jobj, "free_swap", json_object_new_uint64(sys_mem_info->free_swap));
    json_object_object_add(jobj, "swap_usage_percentage", json_object_new_double(sys_mem_info->swap_usage_percentage));
    return jobj;
}

// Função para criar o JSON de informações de um processo
json_object* create_process_memory_json(const ProcessMemoryInfo *proc_mem_info) {
    json_object *jobj = json_object_new_object();
    json_object_object_add(jobj, "pid", json_object_new_int(proc_mem_info->pid));
    json_object_object_add(jobj, "total_memory", json_object_new_uint64(proc_mem_info->total_memory));
    json_object_object_add(jobj, "code_memory", json_object_new_uint64(proc_mem_info->code_memory));
    json_object_object_add(jobj, "heap_memory", json_object_new_uint64(proc_mem_info->heap_memory));
    json_object_object_add(jobj, "stack_memory", json_object_new_uint64(proc_mem_info->stack_memory));
    json_object_object_add(jobj, "total_pages", json_object_new_uint64(proc_mem_info->total_pages));
    json_object_object_add(jobj, "code_pages", json_object_new_uint64(proc_mem_info->code_pages));
    json_object_object_add(jobj, "heap_pages", json_object_new_uint64(proc_mem_info->heap_pages));
    json_object_object_add(jobj, "stack_pages", json_object_new_uint64(proc_mem_info->stack_pages));
    return jobj;
}

// Função para atualizar os JSONs de dados global e de processo
void update_json_data() {
    // Variáveis para armazenar informações de memória do sistema e de um processo
    SystemMemoryInfo sys_mem_info;
    ProcessMemoryInfo proc_mem_info;

    // Obtém informações de memória do sistema
    get_system_memory_info(&sys_mem_info);

    // Cria o JSON para as informações de memória do sistema
    json_object *jglobal = create_system_memory_json(&sys_mem_info);

    // Abre o diretório de processos
    DIR *dir = opendir("/proc");
    if (dir != NULL) {
        // Cria o objeto JSON para armazenar informações de todos os processos
        json_object *jprocs = json_object_new_array();

        // Itera sobre os processos no diretório /proc
        struct dirent *entry;
        while ((entry = readdir(dir)) != NULL) {
            if (atoi(entry->d_name) != 0) {
                pid_t pid = atoi(entry->d_name);

                // Obtém informações de memória do processo
                get_process_memory_info(pid, &proc_mem_info);

                // Cria o JSON para as informações do processo
                json_object *jproc = create_process_memory_json(&proc_mem_info);

                // Adiciona o JSON do processo ao array de processos
                json_object_array_add(jprocs, jproc);
            }
        }

        // Fecha o diretório de processos
        closedir(dir);

        // Escreve o JSON de processos no arquivo
        FILE *fp_procs = fopen("processes_memory.json", "w");
        if (fp_procs != NULL) {
            fprintf(fp_procs, "%s", json_object_to_json_string(jprocs));
            fclose(fp_procs);
        }

        // Libera memória do JSON de processos
        json_object_put(jprocs);
    }

    // Escreve o JSON global no arquivo
    FILE *fp_global = fopen("global_data.json", "w");
    if (fp_global != NULL) {
        fprintf(fp_global, "%s", json_object_to_json_string(jglobal));
        fclose(fp_global);
    }

    // Libera memória do JSON global
    json_object_put(jglobal);
}

int main() {
    while (1) {
        // Atualiza os JSONs de dados global e de processo
        update_json_data();

        // Aguarda o próximo intervalo de atualização
        sleep(JSON_UPDATE_INTERVAL);
    }

    return 0;
}
