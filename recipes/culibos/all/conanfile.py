from conan import ConanFile
from conan.tools.files import get, symlinks, copy, replace_in_file, rename, rm, rmdir
from os.path import join, exists
import shutil

required_conan_version = ">=1.47.0"

class CudaLibOsConan(ConanFile):
    name = "culibos"
    description = "NVIDIA CUDA Library OS"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = ["Nvidia CUDA Toolkit EULA"]
    topics = ("cuda", "nvidia", "runtime", "culibos", "pre-build")
    settings = "os", "arch"
    package_type = "static-library"
    no_copy_source = True

    def build(self):
        src = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        get(self, **src, strip_root=True)

        if exists(join(self.build_folder, "lib", "x64")):
            copy(self, "*", join(self.build_folder, "lib", "x64"), join(self.build_folder, "lib"))
            rmdir(self, join(self.build_folder, "lib", "x64"))
        if exists(join(self.build_folder, "lib64")):
            rename(self, join(self.build_folder, "lib64"), join(self.build_folder, "lib"))
        if exists(join(self.build_folder, "include", "cooperative_groups")):
            rmdir(self, join(self.build_folder, "include", "cooperative_groups"))

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        copy(self, "*culibos.*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_aliases", ["CUDA::culibos"])
        self.cpp_info.libs = ["culibos"]

