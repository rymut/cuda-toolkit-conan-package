# CUDA Toolkit Conan Packages

This repository contains Conan 2.0 packages for Nvidia CUDA Toolkit.

## Status

- [x] nvcc
    - [x] package recipe
    - [x] test package recipe
        - [x] working under Windows (MSVC) / Linux 
- [ ] cudart working
    - [x] package recipe
    - [x] test package recipe
        - [x] working under Windows (MSVC) / Linux
    - [ ] installing only shared or static libs
- [ ] nvvm working correctly as separate package
    - [ ] package recipe
    - [ ] test package recipe

## License

This repository is licensed under [MIT license](../LICENSE).

Disclaimer: Using any of the packages contained in the repository automatically means that user read & agree to [NVidia CUDA Toolkit EULA](../EULA.CUDA-Toolkit).

## Packages

### Nvidia NVCC component

#### nvcrt

Nvidia Compiler Runtime containing headers `include/crt/*`, `include/fatbin_section.h` required by cudart & nvcc

#### nvcc

Nvidia Compiler - exposes `nvcc` as tool.

### Nvidia Runtime component

#### cuda-runtime (CUDA::cudart_static & CUDA::cudart)

Nvidia CUDA Runtime creates:

- `cudart` library containing only shared or shatic library (depending on `self.option.shared`)
- `cudart_deps` link to `CUDA::cudart_static_deps` (no link)

Headers copied from cudart package:

- builtin_types.h 
- channel_descriptor.h
- common_functions.h
- cuda_d3d10_interop.h
- cuda_d3d11_interop.h
- cuda_d3d9_interop.h
- cuda_egl_interop.h
- cuda_gl_interop.h
- cuda_occupancy.h
- cuda_runtime.h
- cuda_runtime_api.h
- cuda_texture_types.h
- cuda_surface_types.h
- cudart_platform.h
- device_atomic_functions.h
- device_atomic_functions.hpp
- device_double_functions.h
- device_types.h
- driver_functions.h
- driver_types.h
- host_config.h
- host_defines.h
- library_types.h
- math_constants.h
- math_functions.h
- device_functions.h
- device_launch_parameters.h
- texture_types.h
- texture_fetch_functions.h
- texture_indirect_functions.h
- vector_functions.h
- vector_functions.hpp
- surface_indirect_functions.h
- surface_functions.h
- sm_60_atomic_functions.h
- sm_60_atomic_functions.hpp
- sm_61_intrinsics.h
- sm_61_intrinsics.hpp
- sm_20_atomic_functions.h
- sm_20_atomic_functions.hpp
- sm_20_intrinsics.h
- sm_20_intrinsics.hpp
- sm_30_intrinsics.h
- sm_30_intrinsics.hpp
- sm_32_atomic_functions.h
- sm_32_atomic_functions.hpp
- sm_32_intrinsics.h
- sm_32_intrinsics.hpp
- sm_35_atomic_functions.h
- sm_35_intrinsics.h
- surface_types.h
- vector_types.h
- cuda_device_runtime_api.h

#### cudadevrt/cuda-device-runtime - CUDA device runtime 

Always static library without headers - required by `nvcc`

Nvidia CUDA Device runtime - contains `cudadevrt` static library (no headers?)
Create CUDA::cudadevrt - used only by nvcc during linking device-link

#### nvcuda/cuda-driver (CUDA::cuda_driver)

Nvidia cuda.lib dynamic library for driver (links driver nvcuda.dll in windows)

Headers nvcuda: 

- cuda.h
- cuComplex.h
- cudaD3D10.h
- cudaD3D10Typedefs.h
- cudaD3D11.h
- cudaD3D11Typedefs.h
- cudaD3D9.h
- cudaD3D9Typedefs.h
- cudaGL.h
- cudaGLTypedefs.h
- cudaTypedefs.h


#### cudacrt (cuda common runtime files) - only headers

Math API headers are placed between multiple packages

Headers copied from cudart package:

- cuda_bf16.h
- cuda_bf16.hpp
- cuda_fp16.h
- cuda_fp16.hpp
- cuda_fp8.h
- cuda_fp8.hpp
- mma.h (mixed math arithmemetic)

See https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html?highlight=nvfunctional#polymorphic-function-wrappers

Headers copied from cudart package
- nvfunctional

coporative groups see. https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#cooperative-groups
- cooperative_groups.h 
- cuda_awbarrier.h
- cuda_awbarrier_helpers.h
- cuda_awbarrier_primitives.h


cuda extensions see. https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#c-language-extensions
- cuda_pipeline_helpers.h
- cuda_pipeline_primitives.h
- cuda_pipeline.h


some profiler things (missing cudaProfiler header):
- cudaProfilerTypedefs.h