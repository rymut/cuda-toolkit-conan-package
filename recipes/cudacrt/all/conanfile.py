from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists
import shutil

required_conan_version = ">=1.47.0"

class CudaCommonRtConan(ConanFile):
    name = "cudacrt"
    description = "NVIDIA CUDA Runtime - Common files"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = ["Nvidia CUDA Toolkit EULA"]
    topics = ("cuda", "nvidia", "runtime", "cudart", "pre-build")
    settings = "os", "arch"
    package_type = "header-library"
    no_copy_source = True

    def build(self):
        src = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        get(self, **src, strip_root=True)

        headers_driver = ["cuda.h", "cuC*", "cudaD3*", "cudaGL*", "cudaType*"]
        headers_runtime = ["*_types.h*", "*_interop.h*", "sm_*.h*", "*_functions.h*", "*_runtime*", "math_*", "*device_*", "cudart*", "host_*", "channel_*", "*_occupancy*"]
        for headers in headers_crt + headers_driver:
            rm(self, headers, join(self.build_folder, "include"))

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        if exists(join(self.build_folder, "include", "cooperative_groups")):
            copy(self, "*", join(self.build_folder, "include", "cooperative_groups"), join(self.package_folder, "include", "cooperative_groups"))
        headers_crt = ["cuda_bf*", "cuda_fp*", "mma.h*", "cooperative_groups*", "*_awbarrier_*", "*_pipeline_*", "*Profiler*", "nvfunctional"]
        for headers in headers_crt:
            copy(self, headers, join(self.build_folder, "include"), join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.libs = []
