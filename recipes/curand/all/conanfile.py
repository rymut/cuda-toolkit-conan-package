from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, symlinks, rm, rmdir, rename
from conan.tools.scm import Version
from os import chmod, sep
from os.path import join, exists
from re import match

required_conan_version = ">=1.47.0"

class CuRandConan(ConanFile):
    name = "curand"
    description = "cuRAND the CUDA random number generation library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("curand", "cuda", "nvidia", "pre-build")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": True
    }
    no_copy_source = True

    def validate(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only windows and linux os is supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only x86_64 is supported")
        if self._is_windows and self.options.shared == False:
            raise ConanInvalidConfiguration("Windows only supports shared library")

    def build(self):
        srcs = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        license_path = join(self.build_folder, "LICENSE")
        for src in srcs:
            get(self, **src, strip_root=True)
            if exists(license_path):
                chmod(license_path, 0o666)
        if exists(join(self.build_folder, "lib", "x64")):
            copy(self, "*", join(self.build_folder, "lib", "x64"), join(self.build_folder, "lib"))
            rmdir(self, join(self.build_folder, "lib", "x64"))
        if exists(join(self.build_folder, "lib64")):
            rename(self, join(self.build_folder, "lib64"), join(self.build_folder, "lib"))
        if self._is_windows:
            copy(self, "*.dll", join(self.build_folder, "lib"), join(self.build_folder, "bin"))
            rm(self, "*.dll", join(self.build_folder, "lib"))

    @property
    def release_version(self):
        match = re.compile(r"^[^\/]+\/([^\.@]*\.[^\.@]*)").match(self.version)
        return match.group(1)

    def requirements(self):
        if not self.options.shared:
            self.requires("cublibos/[>={self.release_version}")

    def package(self):
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        if self.options.shared:
            copy(self, "*.so*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
            copy(self, "*.lib", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
            copy(self, "*.dll", join(self.build_folder, "bin"), join(self.package_folder, "bin"))
        else:
            copy(self, "*_static.a", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        copy(self, "*", join(self.build_folder, "include"), join(self.package_folder, "include"))

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        self.cpp_info.bindirs = ["bin"] if self._is_windows else ["lib"]
        self.cpp_info.set_property("cmake_target_aliases", ["CUDA::curand", "CUDA::curand_static"])
        if not self.options.shared:
            self.cpp_info.requires = ["cublibos::cublibos"]
            self.cpp_info.libs = ["curand"]
        else:
            self.cpp_info.libs = ["curand_static"]
