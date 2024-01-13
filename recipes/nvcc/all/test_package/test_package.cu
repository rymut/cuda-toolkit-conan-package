#include <cuda_runtime_api.h>
#include <stdio.h>
#include <stdlib.h>

__global__ void kernel(int *a, int *b) {
    a[threadIdx.x] = b[threadIdx.x];
}
int main(void)
{
    int devs = 0;
    cudaError_t status = cudaGetDeviceCount(&devs);
    printf("devs available: %d (status %d: \"%s\")\n", devs, status, cudaGetErrorString(status));
    return EXIT_SUCCESS;
}
