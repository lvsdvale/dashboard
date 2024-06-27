#include <json-c/json.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>

#define PROC_DIR "/proc"
#define FD_DIR "/fd"

typedef struct {
    int pid;
    json_object *json;
} proc_info_t;

void get_fd_info(proc_info_t *proc) {
    char path[256];
    DIR *dir;
    struct dirent *ent;
    json_object *fd_array = json_object_new_array();

    snprintf(path, sizeof(path), "%s/%d%s", PROC_DIR, proc->pid, FD_DIR);
    dir = opendir(path);
    if (dir == NULL) {
        perror("opendir");
        return;
    }

    while ((ent = readdir(dir))!= NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
            continue;

        int fd = atoi(ent->d_name);
        char fd_path[256];
        snprintf(fd_path, sizeof(fd_path), "%s/%d%s/%s", PROC_DIR, proc->pid, FD_DIR, ent->d_name);
        char symlink[256];
        ssize_t len = readlink(fd_path, symlink, sizeof(symlink) - 1);
        if (len == -1) {
            perror("readlink");
            continue;
        }
        symlink[len] = '\0';

        json_object *fd_obj = json_object_new_object();
        json_object_object_add(fd_obj, "fd", json_object_new_int(fd));
        json_object_object_add(fd_obj, "path", json_object_new_string(symlink));
        json_object_array_add(fd_array, fd_obj);
    }

    closedir(dir);
    json_object_object_add(proc->json, "fds", fd_array);
}

void get_file_info(proc_info_t *proc) {
    char path[256];
    FILE *file;
    json_object *file_array = json_object_new_array();

    snprintf(path, sizeof(path), "%s/%d/maps", PROC_DIR, proc->pid);
    file = fopen(path, "r");
    if (file == NULL) {
        perror("fopen");
        return;
    }

    char line[256];
    while (fgets(line, sizeof(line), file)) {
        char *token = strtok(line, " ");
        if (token == NULL)
            continue;

        char *path = strtok(NULL, " ");
        if (path == NULL)
            continue;

        json_object *file_obj = json_object_new_object();
        json_object_object_add(file_obj, "path", json_object_new_string(path));
        json_object_array_add(file_array, file_obj);
    }

    fclose(file);
    json_object_object_add(proc->json, "files", file_array);
}

int main(int argc, char *argv[]) {
    if (argc!= 2) {
        fprintf(stderr, "Usage: %s <pid>\n", argv[0]);
        return 1;
    }

    int pid = atoi(argv[1]);
    proc_info_t proc;
    proc.pid = pid;
    proc.json = json_object_new_object();

    get_fd_info(&proc);
    get_file_info(&proc);

    json_object *root = json_object_new_object();
    json_object_object_add(root, "process", proc.json);

    char filename[256];
    snprintf(filename, sizeof(filename), "pid_information.json", pid);

    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        perror("fopen");
        return 1;
    }

    fprintf(fp, "%s\n", json_object_to_json_string(root));
    fclose(fp);

    json_object_put(root);

    return 0;
}