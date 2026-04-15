#include <stdlib.h>

void good_case() {
    char *p = (char *)malloc(128);
    if (p == NULL) {
        return;
    }
    free(p);
}
