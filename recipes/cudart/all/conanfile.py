from conan import ConanFile

required_conan_version = ">=1.47.0"

class CudaRtConan(ConanFile):
    name = "cudart"
    description = "NVIDIA CUDA Runtime"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("cuda", "nvidia", "runtime", "cudart")
    settings = "os", "arch"
    options = {}
    default_options = {}
    no_copy_source = True

    def requirements(self):
        cudart = {
            "12.0.107": "12.0.76"
        }
        self.requires(f"nvcc/{cudart.get(self.version, self.version)}", run=True, libs=True, headers=True)

    def package_info(self):
        components = ["cudart", "cudart_static", "cudart_static_deps"]
        for name in components:
            self.cpp_info.components[name].libdirs = []
            self.cpp_info.components[name].resdirs = []
            self.cpp_info.components[name].bindirs = []
            self.cpp_info.components[name].includedirs = []
            self.cpp_info.components[name].libs = []
            self.cpp_info.components[name].requires = [f"nvcc::{name}"]
