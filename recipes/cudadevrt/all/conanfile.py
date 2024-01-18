from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists
import shutil

required_conan_version = ">=1.47.0"

class CudaDeviceRtConan(ConanFile):
    name = "cudadevrt"
    description = "NVIDIA CUDA Device Runtime"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = ["Nvidia CUDA Toolkit EULA"]
    topics = ("cuda", "nvidia", "runtime", "cudart", "pre-build")
    settings = "os", "arch"
    package_type = "shared-library"
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

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        copy(self, "*cudadevrt*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_aliases", ["CUDA::cudadevrt"])
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.resdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["cudadevrt"]
        self.buildenv_info.define("cudadevrt_PATH", self.package_folder)
        self.runenv_info.define("cudadevrt_PATH", self.package_folder)
