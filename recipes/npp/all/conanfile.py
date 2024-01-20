from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, symlinks, export_conandata_patches, rm, rmdir, rename, replace_in_file
from conan.tools.scm import Version
from os import chmod, sep
from os.path import join, exists
from re import match

required_conan_version = ">=1.47.0"

class NppConan(ConanFile):
    name = "npp"
    description = "NVIDIA CUDA NPP"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("npp", "cuda", "nvidia")
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

    def export_sources(self):
        export_conandata_patches(self)

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
        others = ["npp.h", "nppdefs.h", "nppcore.h", "nppi.h", "npps.h"]
        includes = {
            "nppitc": ["nppi_threshold_and_compare_operations.h"],
            "nppisu": ["nppi_support_functions.h"],
            "nppist": ["nppi_statistics_functions.h", "nppi_linear_transforms.h"],
            "nppim": ["nppi_morphological_operations.h"],
            "nppig": ["nppi_geometry_transforms.h"],
            "nppif": ["nppi_filter_functions.h"],
            "nppidei": ["nppi_data_exchange_and_initialization.h"],
            "nppicom": ["nppi_compression_functions.h"], #removed in cuda 11.0
            "nppicc": ["nppi_color_conversion.h"],
            "nppial": ["nppi_arithmetic_and_logical_operations.h"]
        }
        self.cpp_info.components["nppc"].set_property("cmake_target_aliases", ["CUDA::nppc", "CUDA::nppc_static"])
        if self.options.shared:
            self.cpp_info.components["nppc"].requires += ["nppc"]
        else:
            self.cpp_info.components["nppc"].requires += ["nppc_static"]
        self.cpp_info.components["global"].bindirs = ["bin"] if self._is_windows else ["lib"]
        for name in ["nppial", "nppicc", "nppidei", "nppif", "nppig", "nppim", "nppist", "nppitc", "npps", "nppicom", "nppisu"]:
            self.cpp_info.components[name].set_property("cmake_target_aliases", [f"CUDA::{name}", f"CUDA::{name}_static"])
            if not self.options.shared:
                self.cpp_info.components[name].requires += ["nppc", "culibos::culibos"]
                self.cpp_info.components[name].libs = [f"{name}_static"]
            else:
                self.cpp_info.components[name].requires += ["nppc"]
                self.cpp_info.components[name].libs = [name]
