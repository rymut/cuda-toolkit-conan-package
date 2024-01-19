from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists
import shutil

required_conan_version = ">=1.47.0"

class NvidiaCudaConan(ConanFile):
    name = "nvcuda"
    description = "NVIDIA CUDA Driver API"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = ["Nvidia CUDA Toolkit EULA"]
    topics = ("cuda", "nvidia", "runtime", "cudart", "pre-build")
    settings = "os", "arch"
    # requires nvidia driver dynamic library wo work
    package_type = "static-library"
    no_copy_source = True

    def build(self):
        src = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        get(self, **src, strip_root=True)

        # nvcc package
        if exists(join(self.build_folder, "lib", "x64")):
            copy(self, "*", join(self.build_folder, "lib", "x64"), join(self.build_folder, "lib"))
            rmdir(self, join(self.build_folder, "lib", "x64"))
        if exists(join(self.build_folder, "lib64")):
            rename(self, join(self.build_folder, "lib64"), join(self.build_folder, "lib"))
        if exists(join(self.build_folder, "include", "cooperative_groups")):
            rmdir(self, join(self.build_folder, "include", "cooperative_groups"))
        headers_crt = ["cuda_bf*", "cuda_fp*", "mma.h*", "cooperative_groups*", "*_awbarrier_*", "*_pipeline_*", "*Profiler*", "nvfunctional"]
        headers_runtime = ["*_types.h*", "*_interop.h*", "sm_*.h*", "*_functions.h*", "*_runtime*", "math_*", "*device_*", "cudart*", "host_*", "channel_*", "*_occupancy*"]
        for headers in headers_crt + headers_runtime:
            rm(self, headers, join(self.build_folder, "include"))

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        copy(self, "*cuda.*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        headers_driver = ["cuda.h", "cuC*", "cudaD3*", "cudaGL*", "cudaType*"]
        for headers in headers_driver:
            copy(self, headers, join(self.build_folder, "include"), join(self.package_folder, "include"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)


    def package_info(self):
        self.cpp_info.set_property("cmake_target_aliases", ["CUDA::cuda_driver"])
        if not self._is_windows:
            self.cpp_info.libdirs = ["lib/stubs"]
        self.cpp_info.libs = ["cuda"]

