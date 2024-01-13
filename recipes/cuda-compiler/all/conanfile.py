from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks
from conan.tools.scm import Version
import os
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

class CudaCompilerConan(ConanFile):
    name = "cuda-compiler"
    description = "NVIDIA CUDA Compiler"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("cuda", "nvidia", "compiler")
    settings = "os", "arch"
    package_type = "unknown"
    options = {
        "with_cuobjdump": [True, False],
        "with_nvcc": [True, False],
        "with_cxxfilt": [True, False],
        "with_nvprune": [True, False],
    }
    default_options = {
        "with_cuobjdump": False,
        "with_nvcc": True,
        "with_cxxfilt": False,
        "with_nvprune": False,
    }
    no_copy_source = True

    def requirements(self):
        nvcc = { 
            "12.3.1": "12.3.103",
            "11.6.0": "11.6.55",
        }
        cudart = {
            "12.3.1": "12.3.101",
            "11.6.0": "11.6.55",            
        }
        if self.options.with_nvcc:
            self.requires(f"nvcc/{nvcc.get(self.version, self.version)}", headers=True, libs=True, build=False, run=True, visible=True)
            self.requires(f"cudart/{cudart.get(self.version, self.version)}", headers=True, libs=True, run=True, visible=True)

    def package_info(self):
        nvcc = self.dependencies["nvcc"]
        for item in nvcc.conf_info.items():
            name, value = item
            if isinstance(value, list):
                for val in value:
                    self.conf_info.append(name, val)
                pass
            elif isinstance(value, dict):
                self.conf_info.update(name, value)
            elif isinstance(value, str):
                self.conf_info.define(name, value)
