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

// Estrutura para armazenar as informações de E/S do processo
typedef struct {
    unsigned long long read_bytes;
    unsigned long long write_bytes;
} IOInfo;

// Função para obter informações de E/S do processo
void get_io_info(int pid, IOInfo *io_info) {
    char io_path[256];
    sprintf(io_path, "/proc/%d/io", pid);
    int fd = open(io_path, O_RDONLY);
    if (fd != -1) {
        char buf[BUF_SIZE];
        ssize_t bytes_read = read(fd, buf, BUF_SIZE);
        if (bytes_read != -1) {
            buf[bytes_read] = '\0';
            char *pos = strstr(buf, "read_bytes:");
            if (pos) {
                sscanf(pos, "read_bytes: %llu", &io_info->read_bytes);
            }
            pos = strstr(buf, "write_bytes:");
            if (pos) {
                sscanf(pos, "write_bytes: %llu", &io_info->write_bytes);
            }
        }
        close(fd);
    }
}

// Função para calcular a diferença de tempo em milissegundos
long long timeval_diff(struct timeval *start, struct timeval *end) {
    return (end->tv_sec - start->tv_sec) * 1000LL + (end->tv_usec - start->tv_usec) / 1000LL;
}

// Função para obter as estatísticas de E/S do sistema de arquivos
void get_disk_io_counters(unsigned long long *read_bytes, unsigned long long *write_bytes) {
    FILE *fp = fopen("/proc/diskstats", "r");
    if (fp != NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp) != NULL) {
            char dev_name[64];
            unsigned long long rd, wr;
            int major, minor;
            sscanf(line, "%d %d %s %llu %*d %*d %llu %*d %*d %*d %*d", &major, &minor, dev_name, &rd, &wr);
            if (major > 0 && minor > 0) {
                *read_bytes += rd * 512;   // Setor de 512 bytes
                *write_bytes += wr * 512;  // Setor de 512 bytes
            }
        }
        fclose(fp);
    }
}

// Função para obter o nome do processo
void get_process_name(int pid, char *name) {
    char comm_path[256];
    sprintf(comm_path, "/proc/%d/comm", pid);
    FILE *fp = fopen(comm_path, "r");
    if (fp != NULL) {
        fgets(name, BUF_SIZE, fp);
        fclose(fp);
        // Remover o caractere de nova linha, se existir
        strtok(name, "\n");
    }
}

int main() {
    // Variáveis para armazenar informações do processo
    pid_t pid;
    pid_t ppid;
    long mem_usage_mb;
    IOInfo io_info;
    struct rusage usage;
    struct timeval start_time, end_time;
    long long elapsed_time;
    unsigned long long total_read_bytes = 0;
    unsigned long long total_write_bytes = 0;

    // Loop infinito para atualizar as informações a cada 5 segundos
    while (1) {
        // Obter o tempo de início
        gettimeofday(&start_time, NULL);

        // Zerar as estatísticas de E/S do sistema de arquivos
        total_read_bytes = 0;
        total_write_bytes = 0;

        // Obter as estatísticas de E/S do sistema de arquivos
        get_disk_io_counters(&total_read_bytes, &total_write_bytes);

        // Abrir o diretório /proc
        DIR *dir = opendir("/proc");
        if (dir != NULL) {
            // Loop através de cada entrada no diretório /proc
            struct dirent *entry;
            json_object *jobj = json_object_new_array();
            while ((entry = readdir(dir)) != NULL) {
                // Verificar se o nome da entrada é um número (um PID)
                if (atoi(entry->d_name) != 0) {
                    // Obter o PID
                    pid = atoi(entry->d_name);

                    // Obter o PID do processo pai
                    ppid = getppid();

                    // Obter o uso de recursos do processo
                    getrusage(RUSAGE_SELF, &usage);

                    // Calcular o uso de memória em MB
                    mem_usage_mb = usage.ru_maxrss / 1024;

                    // Obter informações de E/S do processo
                    get_io_info(pid, &io_info);

                    // Calcular a diferença de tempo desde o início do processo
                    gettimeofday(&end_time, NULL);
                    elapsed_time = timeval_diff(&start_time, &end_time);

                    // Calcular o uso da CPU em porcentagem
                    double cpu_usage = ((double)(usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) * 1000.0 +
                                        (double)(usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1000.0) /
                                       (double)elapsed_time * 100.0;

                    // Obter o nome do processo
                    char process_name[BUF_SIZE];
                    get_process_name(pid, process_name);

                    // Criar um objeto JSON para o processo
                    json_object *jproc = json_object_new_object();
                    json_object_object_add(jproc, "pid", json_object_new_int(pid));
                    json_object_object_add(jproc, "name", json_object_new_string(process_name));
                    json_object_object_add(jproc, "ppid", json_object_new_int(ppid));
                    json_object_object_add(jproc, "mem_usage_mb", json_object_new_int(mem_usage_mb));
                    json_object_object_add(jproc, "cpu_usage", json_object_new_double(cpu_usage));
                    json_object_object_add(jproc, "total_read_bytes", json_object_new_uint64(io_info.read_bytes));
                    json_object_object_add(jproc, "total_write_bytes", json_object_new_uint64(io_info.write_bytes));

                    // Adicionar o objeto JSON do processo ao array
                    json_object_array_add(jobj, jproc);
                }
            }

            // Fechar o diretório /proc
            closedir(dir);

            // Salvar o objeto JSON em um arquivo
            FILE *fp_json = fopen("processes.json", "w");
            if (fp_json != NULL) {
                fprintf(fp_json, "%s", json_object_to_json_string(jobj));
                fclose(fp_json);
            }

            json_object_put(jobj);
        }

        // Esperar 5 segundos antes de atualizar as informações
        sleep(5);
    }

    return 0;
}
