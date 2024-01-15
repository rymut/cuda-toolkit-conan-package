from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists

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
        copy(self, "*cu*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        dirs = ["bin", "include"]
        for name in dirs:
            if exists(join(self.build_folder, name)):
                copy(self, "*", join(self.build_folder, name), join(self.package_folder, name))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    def package_info(self):
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "res", "cudart_toolchain.cmake"))

        requires = {
            "cudart": "cudart_static",
            "cudart_deps": "cudart_static_deps"
        }
        self.cpp_info.components["global"].requires = ["nvcrt::nvcrt"]
        # cudart libraries
        self.cpp_info.components["cudart"].set_property("cmake_target_aliases", ["CUDA::cudart"])
        self.cpp_info.components["cudart"].libs = ["cudart"]
        self.cpp_info.components["cudart"].includedirs = ["include"]
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart"].system_libs = ["dl"]

        self.cpp_info.components["cudart_static_deps"].set_property("cmake_target_aliases", ["CUDA::cudart_static_deps"])
        self.cpp_info.components["cudart_static_deps"].libdirs = []
        self.cpp_info.components["cudart_static_deps"].bindirs = []
        self.cpp_info.components["cudart_static_deps"].libs = []

        # unix system_libs
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart_static_deps"].system_libs = ["pthread", "rt"]
        self.cpp_info.components["cudart_static"].set_property("cmake_target_aliases", ["CUDA::cudart_static"])
        self.cpp_info.components["cudart_static"].libs = ["cudart_static"]
        self.cpp_info.components["cudart_static"].requires = ["cudart_static_deps"]
        self.cpp_info.components["cudart_static"].includedirs = ["include"]

        self.cpp_info.components["cuda_driver"].set_property("cmake_target_aliases", ["CUDA::cuda_driver", "CUDA::cuda"])
        if not self._is_windows:
            self.cpp_info.components["cuda_driver"].libdirs = ["lib/stubs"]
        self.cpp_info.components["cuda_driver"].libs = ["cuda"]

        self.cpp_info.components["cudadevrt"].set_property("cmake_target_aliases", ["CUDA::cudadevrt"])
        self.cpp_info.components["cudadevrt"].libs = ["cudadevrt"]

        self.cpp_info.components["culibos"].set_property("cmake_target_aliases", ["CUDA::culibos"])
        if not self._is_windows:
            self.cpp_info.components["culibos"].libs = ["culibos"]

        self.buildenv_info.define("cudart_PATH", self.package_folder)
        self.runenv_info.define("cudart_PATH", self.package_folder)
