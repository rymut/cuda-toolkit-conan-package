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

### nvcrt

Nvidia Compiler Runtime containing headers `include/crt/*`, `include/fatbin_section.h` required by cudart & nvcc

### nvcc

Nvidia Compiler - exposes `nvcc` as tool.

### cudart

Nvidia CUDA Runtime - contains `cudart` library containing only shared or shatic library (depending on `self.option.shared`)

