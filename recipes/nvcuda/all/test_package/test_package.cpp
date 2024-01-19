#if _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif
#include <cstdio>

typedef void (*entry_point_t)(void);

int main(void)
{
    #if _WIN32
    HMODULE module = LoadLibrary("test_library.dll");
    if (module == NULL) {
        printf("missing nvcuda driver");
        return EXIT_SUCCESS;
    }
    entry_point_t entry_point = (entry_point_t)GetProcAddress(module, "test_library_main");
    if (entry_point != NULL) {
        entry_point();
    } else {
        printf("missing entrypoint");
    }
    FreeLibrary(module);
    module = NULL;
    #else
    void *module = dlopen("test_library.so", RTLD_NOW);
    if (module == NULL) {
        printf("missing nvcuda driver");
        return EXIT_SUCCESS;
    }
    entry_point_t entry_point = (entry_point_t)dlsym(module, "test_library_main");
    if (entry_point != NULL) {
        entry_point();
    } else {
        printf("missing entrypoint");
    }
    dlclose(module);
    module = NULL;
    #endif
    return EXIT_SUCCESS;
}
