#include <cuda.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef __cplusplus
#define EXTERN_SCOPE extern "C"
#else
#define EXTERN_SCOPE
#endif

#ifdef _WIN32
#define EXPORTS __declspec(dllexport)
#else
#define EXPORTS
#endif

EXTERN_SCOPE EXPORTS void test_library_main(void)
{
    int runtimeVersion = 0, driverVersion = 0;
    CUresult status = cuDriverGetVersion(&driverVersion);
    const char *error = NULL;
    cuGetErrorName(status, &error);
    if (error != NULL) {
        printf("driver version available: %d (status %d: \"%s\")\n", driverVersion, status, error);
    } else {
        printf("driver version available: %d (status %d: \"%s\")\n", driverVersion, status, "unknown");
    }
}
