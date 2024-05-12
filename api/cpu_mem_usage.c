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
    if (fp!= NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp)!= NULL) {
            if (strstr(line, "MemTotal:")!= NULL) {
                sscanf(line, "MemTotal: %llu kB", &sys_mem_info->total_ram);
            } else if (strstr(line, "MemFree:")!= NULL) {
                sscanf(line, "MemFree: %llu kB", &sys_mem_info->free_ram);
            } else if (strstr(line, "SwapTotal:")!= NULL) {
                sscanf(line, "SwapTotal: %llu kB", &sys_mem_info->total_swap);
            } else if (strstr(line, "SwapFree:")!= NULL) {
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
    if (fp!= NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp)!= NULL) {
            if (strstr(line, "VmSize:")!= NULL) {
                sscanf(line, "VmSize: %llu kB", &proc_mem_info->total_memory);
            } else if (strstr(line, "VmExe:")!= NULL) {
                sscanf(line, "VmExe: %llu kB", &proc_mem_info->code_memory);
            } else if (strstr(line, "VmData:")!= NULL) {
                sscanf(line, "VmData: %llu kB", &proc_mem_info->heap_memory);
            } else if (strstr(line, "VmStk:")!= NULL) {
                sscanf(line, "VmStk: %llu kB", &proc_mem_info->stack_memory);
            }
        }
        fclose(fp);
    }

    sprintf(path, "/proc/%d/smaps", pid);
    fp = fopen(path, "r");
    if (fp!= NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp)!= NULL) {
            if (strstr(line, "Size:")!= NULL) {
                sscanf(line, "Size: %llu kB", &proc_mem_info->total_pages);
            } else if (strstr(line, "KernelPageSize:")!= NULL) {
                sscanf(line, "KernelPageSize: %llu", &proc_mem_info->code_pages);
            } else if (strstr(line, "MMUPageSize:")!= NULL) {
                sscanf(line, "MMUPageSize: %llu", &proc_mem_info->heap_pages);
            } else if (strstr(line, "AnonHugePages:")!= NULL) {
                sscanf(line, "AnonHugePages: %llu", &proc_mem_info->stack_pages);
            }
        }
        fclose(fp);
    }
}

int main() {
    SystemMemoryInfo sys_mem_info;
    get_system_memory_info(&sys_mem_info);

    printf("System Memory Info:\n");
    printf("  Total RAM: %llu kB\n", sys_mem_info.total_ram);
    printf("  Free RAM: %llu kB\n", sys_mem_info.free_ram);
    printf("  RAM Usage Percentage: %.2f%%\n", sys_mem_info.ram_usage_percentage);
    printf("  Total Swap: %llu kB\n", sys_mem_info.total_swap);
    printf("  Free Swap: %llu kB\n", sys_mem_info.free_swap);
    printf("  Swap Usage Percentage: %.2f%%\n", sys_mem_info.swap_usage_percentage);

    DIR *dir = opendir("/proc");
    if (dir!= NULL) {
        struct dirent *entry;
        json_object *jobj = json_object_new_array();
        while ((entry = readdir(dir))!= NULL) {
            if (atoi(entry->d_name)!= 0) {
                pid_t pid = atoi(entry->d_name);
                ProcessMemoryInfo proc_mem_info;
                get_process_memory_info(pid, &proc_mem_info);

                json_object *jproc = json_object_new_object();
                json_object_object_add(jproc, "pid", json_object_new_int(pid));
                json_object_object_add(jproc, "total_memory", json_object_new_uint64(proc_mem_info.total_memory));
                json_object_object_add(jproc, "code_memory", json_object_new_uint64(proc_mem_info.code_memory));
                json_object_object_add(jproc, "heap_memory", json_object_new_uint64(proc_mem_info.heap_memory));
                json_object_object_add(jproc, "stack_memory", json_object_new_uint64(proc_mem_info.stack_memory));
                json_object_object_add(jproc, "total_pages", json_object_new_uint64(proc_mem_info.total_pages));
                json_object_object_add(jproc, "code_pages", json_object_new_uint64(proc_mem_info.code_pages));
                json_object_object_add(jproc, "heap_pages", json_object_new_uint64(proc_mem_info.heap_pages));
                json_object_object_add(jproc, "stack_pages", json_object_new_uint64(proc_mem_info.stack_pages));

                json_object_array_add(jobj, jproc);
            }
        }

        closedir(dir);

        FILE *fp_json = fopen("memory.json", "w");
        if (fp_json!= NULL) {
            fprintf(fp_json, "%s", json_object_to_json_string(jobj));
            fclose(fp_json);
        }

        json_object_put(jobj);
    }

    return 0;
}