#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <json-c/json.h>

#define MAX_PATH 256

void dir_to_json(const char *dir_path, struct json_object *j_dir) {
    DIR *dir;
    struct dirent *ent;
    struct stat statbuf;
    char path[MAX_PATH];

    dir = opendir(dir_path);
    if (dir == NULL) {
        perror("opendir");
        return;
    }

    json_object *j_children = json_object_new_array();
    json_object_object_add(j_dir, "children", j_children);

    int num_children = 0;
    long total_size = 0;

    while ((ent = readdir(dir))!= NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
            continue;

        snprintf(path, MAX_PATH, "%s/%s", dir_path, ent->d_name);
        stat(path, &statbuf);

        struct json_object *j_child = json_object_new_object();
        json_object_object_add(j_child, "name", json_object_new_string(ent->d_name));
        json_object_object_add(j_child, "size", json_object_new_int64(statbuf.st_size));

        if (S_ISDIR(statbuf.st_mode)) {
            json_object_object_add(j_child, "type", json_object_new_string("directory"));
        } else {
            json_object_object_add(j_child, "type", json_object_new_string("file"));
        }

        json_object_array_add(j_children, j_child);
        num_children++;
        total_size += statbuf.st_size;
    }

    closedir(dir);

    json_object_object_add(j_dir, "num_children", json_object_new_int(num_children));
    json_object_object_add(j_dir, "total_size", json_object_new_int64(total_size));
}
int main(int argc, char *argv[]) {
    if (argc!= 2) {
        fprintf(stderr, "Usage: %s <directory_path>\n", argv[0]);
        return 1;
    }

    const char *dir_path = argv[1];

    struct json_object *j_dir = json_object_new_object();
    json_object_object_add(j_dir, "path", json_object_new_string(dir_path));

    dir_to_json(dir_path, j_dir);

    char *json_string = json_object_to_json_string(j_dir);

    FILE *fp = fopen("navigation.json", "w");
    if (fp == NULL) {
        perror("fopen");
        return 1;
    }

    fwrite(json_string, strlen(json_string), 1, fp);
    fclose(fp);

    json_object_put(j_dir);
    free(json_string);

    return 0;
}