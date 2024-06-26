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
#define INTERVAL 5  // Intervalo de tempo em segundos entre as leituras

typedef struct {
    unsigned long long read_bytes;
    unsigned long long write_bytes;
} IOInfo;

typedef struct {
    unsigned long long user_time;
    unsigned long long system_time;
} CPUInfo;

void get_io_info(int pid, IOInfo *io_info) {
    char io_path[256];
    sprintf(io_path, "/proc/%d/io", pid);
    int fd = open(io_path, O_RDONLY);
    if (fd!= -1) {
        char buf[BUF_SIZE];
        ssize_t bytes_read = read(fd, buf, BUF_SIZE);
        if (bytes_read!= -1) {
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

void get_cpu_info(int pid, CPUInfo *cpu_info) {
    char stat_path[256];
    sprintf(stat_path, "/proc/%d/stat", pid);
    FILE *fp = fopen(stat_path, "r");
    if (fp!= NULL) {
        long long unsigned utime, stime;
        fscanf(fp, "%*d %*s %*c %*d %*d %*d %*d %*d %*u %*u %*u %*u %*u %llu %llu", &utime, &stime);
        cpu_info->user_time = utime;
        cpu_info->system_time = stime;
        fclose(fp);
    }
}

unsigned long long get_total_cpu_time() {
    FILE *fp = fopen("/proc/stat", "r");
    if (fp!= NULL) {
        char line[BUF_SIZE];
        unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
        fgets(line, sizeof(line), fp);
        sscanf(line, "cpu  %llu %llu %llu %llu %llu %llu %llu %llu", &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal);
        fclose(fp);
        return user + nice + system + idle + iowait + irq + softirq + steal;
    }
    return 0;
}

void get_disk_io_counters(unsigned long long *read_bytes, unsigned long long *write_bytes) {
    FILE *fp = fopen("/proc/diskstats", "r");
    if (fp!= NULL) {
        char line[BUF_SIZE];
        while (fgets(line, sizeof(line), fp)!= NULL) {
            char dev_name[64];
            unsigned long long rd_sectors, wr_sectors;
            int major, minor;
            sscanf(line, "%d %d %s %*d %*d %llu %*d %*d %*d %llu", &major, &minor, dev_name, &rd_sectors, &wr_sectors);
            if (major > 0 && minor > 0) {
                *read_bytes += rd_sectors * 512;
                *write_bytes += wr_sectors * 512;
            }
        }
        fclose(fp);
    }
}

void get_process_name(int pid, char *name) {
    char comm_path[256];
    sprintf(comm_path, "/proc/%d/comm", pid);
    FILE *fp = fopen(comm_path, "r");
    if (fp!= NULL) {
        fgets(name, BUF_SIZE, fp);
        fclose(fp);
        strtok(name, "\n");
    }
}

int get_ppid(int pid) {
    char stat_path[256];
    sprintf(stat_path, "/proc/%d/stat", pid);
    FILE *fp = fopen(stat_path, "r");
    if (fp!= NULL) {
        int ppid;
        fscanf(fp, "%*d %*s %*c %d", &ppid);
        fclose(fp);
        return ppid;
    }
    return -1;
}

int main() {
    pid_t pid;
    pid_t ppid;
    long mem_usage_mb;
    IOInfo io_info;
    CPUInfo cpu_info, prev_cpu_info = {0, 0};
    struct rusage usage;
    unsigned long long total_read_bytes = 0;
    unsigned long long total_write_bytes = 0;
    unsigned long long prev_total_cpu_time = 0, total_cpu_time;
    double cpu_usage;

    prev_total_cpu_time = get_total_cpu_time();

    while (1) {
        total_read_bytes = 0;
        total_write_bytes = 0;

        get_disk_io_counters(&total_read_bytes, &total_write_bytes);

        DIR *dir = opendir("/proc");
        if (dir!= NULL) {
            struct dirent *entry;
            json_object *jobj = json_object_new_array();
            while ((entry = readdir(dir))!= NULL) {
                if (atoi(entry->d_name)!= 0) {
                    pid = atoi(entry->d_name);
                    ppid = get_ppid(pid);

                    get_io_info(pid, &io_info);
                    get_cpu_info(pid, &cpu_info);

                    total_cpu_time = get_total_cpu_time();
                    double process_cpu_delta = (cpu_info.user_time + cpu_info.system_time) - (prev_cpu_info.user_time + prev_cpu_info.system_time);
                    double total_cpu_delta = total_cpu_time - prev_total_cpu_time;

                    if (total_cpu_delta > 0) {
                        cpu_usage = (process_cpu_delta / sysconf(_SC_CLK_TCK)) / (total_cpu_delta / sysconf(_SC_CLK_TCK)) * 100.0;
                        cpu_usage = cpu_usage / (double)sysconf(_SC_NPROCESSORS_ONLN);
                    } else {
                        cpu_usage = 0.0;
                    }

                    prev_cpu_info = cpu_info;
                    prev_total_cpu_time = total_cpu_time;

                    if (getrusage(RUSAGE_SELF, &usage) == 0) {
                        mem_usage_mb = usage.ru_maxrss / 1024;
                    }

                    char process_name[BUF_SIZE];
                    get_process_name(pid, process_name);

                    json_object *jproc = json_object_new_object();
                    json_object_object_add(jproc, "pid", json_object_new_int(pid));
                    json_object_object_add(jproc, "name", json_object_new_string(process_name));
                    json_object_object_add(jproc, "ppid", json_object_new_int(ppid));
                    json_object_object_add(jproc, "mem_usage_mb", json_object_new_int(mem_usage_mb));
                    json_object_object_add(jproc, "cpu_usage", json_object_new_double(cpu_usage));
                    json_object_object_add(jproc, "total_read_bytes", json_object_new_uint64(io_info.read_bytes));
                    json_object_object_add(jproc, "total_write_bytes", json_object_new_uint64(io_info.write_bytes));

                    json_object_array_add(jobj, jproc);
                }
            }
            closedir(dir);

            FILE *fp_json = fopen("processes.json", "w");
            if (fp_json!= NULL) {
                fprintf(fp_json, "%s", json_object_to_json_string(jobj));
                fclose(fp_json);
            }

            json_object_put(jobj);
        }

        sleep(INTERVAL);
    }

    return 0;
}