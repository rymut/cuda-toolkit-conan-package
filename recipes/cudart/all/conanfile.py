from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists
import shutil

required_conan_version = ">=1.47.0"

class CudaRtConan(ConanFile):
    name = "cudart"
    description = "NVIDIA CUDA Runtime"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = ["Nvidia CUDA Toolkit EULA"]
    topics = ("cuda", "nvidia", "runtime", "cudart", "pre-build")
    settings = "os", "arch"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": True
    }
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
        if self._is_windows:
            copy(self, "*.dll", join(self.build_folder, "lib"), join(self.build_folder, "bin"))
            rm(self, "*.dll", join(self.build_folder, "lib"))
        if exists(join(self.build_folder, "include", "cooperative_groups")):
            rmdir(self, join(self.build_folder, "include", "cooperative_groups"))
        headers_crt = ["cuda_bf*", "cuda_fp*", "mma.h*", "cooperative_groups*", "*_awbarrier_*", "*_pipeline_*", "*Profiler*", "nvfunctional"]
        headers_driver = ["cuda.h", "cuC*", "cudaD3*", "cudaGL*", "cudaType*"]
        for headers in headers_crt + headers_driver:
            rm(self, headers, join(self.build_folder, "include"))
        if self.options.shared:
            rm(self, "*cudart_static.*", join(self.build_folder, "lib"))
            if self._is_windows:
                shutil.copy(join(self.build_folder, "lib", "cudart.lib"), join(self.build_folder, "lib", "cudart_static.lib"))
            else:
                os.symlink(join(self.build_folder, "lib", "libcudart.so"), join(self.build_folder, "lib", "libcudart_static.so"))
                absolute_to_relative_symlinks(self, join(self.build_folder, "lib"))
        else:
            rmdir(self, join(self.build_folder, "bin"))
            rm(self, "*cudart.*", join(self.build_folder, "lib"))
            if self._is_windows:
                shutil.copy(join(self.build_folder, "lib", "cudart_static.lib"), join(self.build_folder, "lib", "cudart.lib"))
            else:
                os.symlink(join(self.build_folder, "lib", "libcudart_static.a"), join(self.build_folder, "lib", "libcudart.a"))
                absolute_to_relative_symlinks(self, join(self.build_folder, "lib"))

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def requirements(self):
        cudart = {
            "12.3.101": "12.3.103",
            "12.0.107": "12.0.76"
        }
        self.requires(f"nvcrt/{cudart.get(self.version, self.version)}", run=True, headers=True, transitive_headers=True, libs=True, transitive_libs=True)

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        copy(self, "*cudart*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        if self.options.shared:
            copy(self, "*", join(self.build_folder, "bin"), join(self.package_folder, "bin"))

        headers_runtime = ["*_types.h*", "*_interop.h*", "sm_*.h*", "*_functions.h*", "*_runtime*", "math_*", "*device_*", "cudart*", "host_*", "channel_*", "*_occupancy*"]
        for headers in headers_runtime:
            copy(self, headers, join(self.build_folder, "include"), join(self.package_folder, "include"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    def package_info(self):
        self.cpp_info.components["cudart_deps"].set_property("cmake_target_aliases", ["CUDA::cudart_static_deps"])
        self.cpp_info.components["cudart_deps"].libdirs = []
        self.cpp_info.components["cudart_deps"].bindirs = []
        self.cpp_info.components["cudart_deps"].libs = []
        if not self.options.shared and self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart_static_deps"].system_libs = ["pthread", "rt"]

        # cudart libraries
        self.cpp_info.components["cudart"].set_property("cmake_target_aliases", ["CUDA::cudart", "CUDA::cudart_static"])
        self.cpp_info.components["cudart"].libs = ["cudart"]
        self.cpp_info.components["cudart"].includedirs = ["include"]
        self.cpp_info.components["cudart"].requires = ["nvcrt::nvcrt", "cudart_deps"]
        if self.options.shared and self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart"].system_libs = ["dl"]

        self.buildenv_info.define("cudart_PATH", self.package_folder)
        self.runenv_info.define("cudart_PATH", self.package_folder)
