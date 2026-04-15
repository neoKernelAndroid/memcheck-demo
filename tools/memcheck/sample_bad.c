#include <stdlib.h>

void bad_case() {
    char *p = (char *)malloc(128);
    (void)p;
}
