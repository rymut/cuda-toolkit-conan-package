from conan import ConanFile
from conan.tools.files import copy, replace_in_file
from os.path import join

required_conan_version = ">=1.47.0"

class CudaRtConan(ConanFile):
    name = "cudart"
    description = "NVIDIA CUDA Runtime"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("cuda", "nvidia", "runtime", "cudart", "pre-build")
    settings = "os", "arch"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": True
    }
    no_copy_source = True

    def requirements(self):
        cudart = {
            "12.3.101": "12.3.103",
            "12.0.107": "12.0.76"
        }
        self.requires(f"nvcc/{cudart.get(self.version, self.version)}", libs=True, headers=True, transitive_headers=True, transitive_libs=True)

    def package_info(self):
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "res", "cudart_toolchain.cmake"))

        requires = {
            "cudart": "cudart_static",
            "cudart_deps": "cudart_static_deps"
        }
        if self.options.shared:
            requires = {"cudart": "cudart", "cudart_deps": None}
        components = ["cudart", "cudart_deps"]
        nvcc = self.dependencies["nvcc"].package_folder
        for name in components:
            self.cpp_info.components[name].libdirs = []
            self.cpp_info.components[name].resdirs = []
            self.cpp_info.components[name].bindirs = []
            self.cpp_info.components[name].includedirs = []
            self.cpp_info.components[name].libs = []
            require = requires.get(name, None)
            if require is not None:
                self.cpp_info.components[name].requires = [f"nvcc::{require}"]
