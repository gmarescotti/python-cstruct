/* gcc -std=c99 -Wall variable_length.c -o variable_length && ./variable_length */

#include <stdio.h>
#include <stdlib.h>

typedef struct {
    uint8_t length;
    uint8_t data[];
} st_pkg;

void test(uint8_t n) {
    size_t allocated_size = sizeof(st_pkg) + n * sizeof(uint8_t);
    printf("n: %i\n", n);
    printf("allocated_size: %zu\n", allocated_size);
    st_pkg* tmp = malloc(allocated_size);
    if (!tmp) {
        perror("malloc");
        exit(EXIT_FAILURE);
    };
    tmp->length = n;
    for (uint8_t i=0; i < tmp->length; i++) {
        tmp->data[i] = i;
    }
    free(tmp);
}

int main() {
    test(0);
    test(5);
    return 0;
}

