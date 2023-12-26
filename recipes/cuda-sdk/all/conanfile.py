import os
from conan import ConanFile
from conans.errors import ConanInvalidConfiguration
import shutil
from conan.tools.scm import Version
from conan.tools.files import download, copy, unzip, rm, symlinks

class CudaSdkConan(ConanFile):
    name = "cudasdk"
    description = "Nvidia CUDA SDK toolkit"
    url = "https://github.com/rymut/conan-center-index-cuda-sdk"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("nvcc", "cuda", "nvidia", "SDK")
    exports = ['FindCUDASDK.cmake']
    exports_sources = ["FindCUDASDK.cmake"] 
    settings = "os", "arch"
    options = {
        # package layout - legacy = nvcc/visualstudiointegration , modern = bin/lib/extras
        "layout": ["legacy", "modern"],
        "cccl": [True, False],
        "cudnn": [True, False],
        "cudnn_version": ["none", "ANY"],
        "cudart": [True, False], 
        "cuobjdump": [True, False], 
        "cupti": [True, False], 
        "cuxxfit": [True, False], 
        "gdb": [True, False],
        "memcheck": [True, False], 
        "nvcc": [True, False], 
        "nvdisasm": [True, False], 
        "nvprof": [True, False],
        "nvprune": [True, False],
        "nvrtc": [True, False],
        "nvtx": [True, False], # windows only 
        "sanitizer_api": [True, False],
        # libraries 
        "nvml": [True, False], 
        "thrust": [True, False],
        "cublas": [True, False],
        "cufft": [True, False],
        "curand": [True, False],
        "cusolver": [True, False],
        "cusparse": [True, False],
        "npp": [True, False],
        "nvjpeg": [True, False],
        # integration elements true for visual studio usage
        "visual_studio_integration": [True, False] 
    }
    default_options = {
        "layout": "legacy",
        "cccl": True,
        "cudnn": False,
        "cudnn_version": "none",
        "cudart": True, 
        "cuobjdump": True, 
        "gdb": True,
        "cupti": True, 
        "cuxxfit": True, 
        "memcheck": True, 
        "nvcc": True, 
        "nvdisasm": True, 
        "nvml": True, 
        "nvprof": True,
        "nvprune": True,
        "nvrtc": True,
        "nvtx": True, # windows only 
        "sanitizer_api": True,
        "thrust": True,
        "cublas": True,
        "cufft": True,
        "curand": True,
        "cusolver": True,
        "cusparse": True,
        "npp": True,
        "nvjpeg": True,
        "visual_studio_integration": True
    }
    no_copy_source = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        if self.options.cccl:
            self.requires("thrust/1.17.2")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("7zip/19.00")

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.gdb
            del self.options.cccl
        if self.settings.os != "Windows":
            del self.options.visual_studio_integration
    
    def validate(self):
        if self.settings.os != "Windows" and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only windows and linux os is supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only x86_64 is supported")
        if self.options.cudnn == True and self.options.cudnn_version == "None":
            raise ConanInvalidConfiguration("Setting cudnn_version must be set when cudnn is true")
        if self.options.cudnn == False and self.options.cudnn_version != "none":
            raise ConanInvalidConfiguration("Setting cudnn_version cannot be set when cudnn is false")
        if self.options.cudnn:
            if not os.path.exists(self._filepath_cudnn) or not os.path.isfile(self._filepath_cudnn):
                raise ConanInvalidConfiguration("Building with cudnn=True require setting CUDNN_PATH variable containing {}".format(self._filename_cudnn))

    @property
    def _filename(self):
        filename = "cuda_{}.run".format(self.version) 
        if self.settings.os == "Windows":
            filename = "cuda_{}.exe".format(self.version) 
        return filename
    
    @property
    def _filename_cudnn(self):
        return "cudnn_{}.zip".format(self.options.cudnn_version)
    
    @property
    def _path_cudnn(self):
        return os.environ.get('CUDNN_PATH')

    @property
    def _filepath_cudnn(self):
        return os.path.join(self._path_cudnn, self._filename_cudnn)

    def build(self):
        if self.options.cudnn:
            unzip(self._path_cudnn, destination="cudnn", strip_root=True)
        src = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        download(self, **src, filename=self._filename)
        if "Windows" == str(self.settings.os):
            self.run("7z x {}".format(self._filename))
        elif "Linux" == str(self.settings.os):
            self.run("./{} --extract={}".format(self._filename, self.build_folder))

    def _package_linux(self):
        targets = os.path.join("targets", "{}-linux".format(self.settings.arch))
        inc_dst = os.path.join(targets, "include")
        lib_dst = os.path.join(targets, "lib")
        # only windows settings for now
        #copy(self, "FindCUDASDK.cmake", ".", ".")
        copy(self, "version.*", self.build_folder, self.package_folder)
        # copy license files
        copy(self, "EULA.txt", self.build_folder, os.path.join(self.package_folder, "licenses"))
        # os.path.join("cuda_documentation", "Doc"))
        if self.options.cccl:
            copy(self, "*", os.path.join(self.build_folder, "cuda_cccl"), self.package_folder)
        if self.options.thrust == False:
            rm(self, "*", os.path.join(self.package_folder, inc_dir, "thrust"))
            rm(self, "*", os.path.join(self.package_folder, lib_dir, "cmake", "thrust"))
        if self.options.cudart:
            copy(self, "*", os.path.join(self.build_folder, "cuda_cudart"), self.package_folder)
        if self.options.cuobjdump:
            copy(self, "*", os.path.join(self.build_folder, "cuda_cuobjdump"), self.package_folder)
        if self.options.cupti:
            copy(self, "*", os.path.join(self.build_folder, "cuda_cupti"), self.package_folder)
            rm(self, "*", os.path.join(self.package_folder, "doc"))
            rm(self, "*", os.path.join(self.package_folder, "samples"))
        if self.options.cuxxfit:
            copy(self, "*", os.path.join(self.build_folder, "cuda_cuxxfit"), self.package_folder)
        # skip cuda_demo_suite
        # skip cuda_documentation
        if self.options.gdb:
            copy(self, "*", os.path.join(self.build_folder, "cuda_gdb"), self.package_folder)
        if self.options.memcheck:
            copy(self, "*", os.path.join(self.build_folder, "cuda_memcheck"), self.package_folder)
        # skip nsight
        if self.options.nvcc:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvcc"), self.package_folder)
        if self.options.nvdisasm:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvdisasm"), self.package_folder)
        if self.options.nvml:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvml_dev"), self.package_folder)
        if self.options.nvprof:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvprof"), self.package_folder)
        if self.options.nvprune:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvprune"), self.package_folder)
        if self.options.nvrtc:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvrtc"), self.package_folder)
        if self.options.nvtx:
            copy(self, "*", os.path.join(self.build_folder, "cuda_nvtx"), self.package_folder)
        # skip nvvp
        # skip cuda_samples
        if self.options.sanitizer_api:
            copy(self, "*", os.path.join(self.build_folder, "cuda_sanitizer_api"), self.package_folder)
        # skip integration
        if self.options.cublas:
            copy(self, "*", os.path.join(self.build_folder, "libcublas"), self.package_folder)
            rm(self, "cublas_version.txt", os.path.join(self.package_folder))
        if self.options.cufft:
            copy(self, "*", os.path.join(self.build_folder, "libcufft"), self.package_folder)
        if self.options.curand:
            copy(self, "*", os.path.join(self.build_folder, "libcurand"), self.package_folder)            
        if self.options.cusolver:
            copy(self, "*", os.path.join(self.build_folder, "libcusolver"), self.package_folder)            
        if self.options.cusparse:
            copy(self, "*", os.path.join(self.build_folder, "libcusparse"), self.package_folder)
        if self.options.npp:
            copy(self, "*", os.path.join(self.build_folder, "libnpp"), self.package_folder)
        if self.options.nvjpeg:
            copy(self, "*", os.path.join(self.build_folder, "libnvjpeg"), self.package_folder)
        # skip nsight_compute
        # skip nsigth_systems
        if self.options.cudnn:
            self.copy("LICENSE", "licenses", os.path.join("cudnn"))
            self.copy("*", os.path.join("nvcc", "include"), os.path.join("cudnn", "include"))
            self.copy("*", os.path.join("nvcc", "lib", "x64"), os.path.join("cudnn", "lib"))
            self.copy("*", os.path.join("nvcc", "bin"), os.path.join("cudnn", "bin"))
        os.symlink(os.path.join(self.package_folder, inc_dst), os.path.join(self.package_folder, "include"))
        os.symlink(os.path.join(self.package_folder, lib_dst), os.path.join(self.package_folder, "lib64"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)


    def _package_windows(self):
        # only windows settings for now
        self.copy("FindCUDASDK.cmake", ".", ".")
        self.copy("version.*", "nvcc", "CUDAToolkit")
        # copy license files
        self.copy("EULA.txt", "licenses", os.path.join("cuda_documentation", "Doc"))
        if self.options.cudart:
            self.copy("*", "nvcc", os.path.join("cuda_cudart", "cudart"))
        if self.options.cuobjdump:
            self.copy("*", "nvcc", os.path.join("cuda_cuobjdump", "cuobjdump"))
        if self.options.cupti:
            self.copy("*", "nvcc", os.path.join("cuda_cupti", "cupti"))
        if self.options.cuxxfit:
            self.copy("*", "nvcc", os.path.join("cuda_cuxxfit", "cuxxfit"))
        if self.options.memcheck:
            self.copy("*", "nvcc", os.path.join("cuda_memcheck", "memcheck"))
        if self.options.nvcc:
            self.copy("*", "nvcc", os.path.join("cuda_nvcc", "nvcc"))
        if self.options.nvdisasm:
            self.copy("*", "nvcc", os.path.join("cuda_nvdisasm", "nvdisasm"))
        if self.options.nvml:
            self.copy("*", "nvcc", os.path.join("cuda_nvml_dev", "nvml_dev"))
        if self.options.nvprof:
            self.copy("*", "nvcc", os.path.join("cuda_nvprof", "nvprof"))
        if self.options.nvprune:
            self.copy("*", "nvcc", os.path.join("cuda_nvprune", "nvprune"))
        if self.options.nvrtc:
            self.copy("*", "nvcc", os.path.join("cuda_nvrtc", "nvrtc"))
            self.copy("*", "nvcc", os.path.join("cuda_nvrtc", "nvrtc_dev"))
        if self.options.sanitizer_api:
            self.copy("*", "nvcc", os.path.join("cuda_sanitizer_api"), "sanitizer")
        if self.options.cublas:
            self.copy("*", "nvcc", os.path.join("libcublas", "cublas"))
            self.copy("*", "nvcc", os.path.join("libcublas", "cublas_dev"))
        if self.options.thrust:
            self.copy("*", "nvcc", os.path.join("cuda_thrust", "thrust"))
            self.copy("*", "nvcc", os.path.join("cuda_cccl", "thrust")) # newer packages
        if self.settings.os == "Windows":
            if self.options.nvtx:
                self.copy("*", "nvcc", os.path.join("cuda_nvtx", "nvtx"))
            if self.options.visual_studio_integration:
                self.copy("*", "", "visual_studio_integration")
        if self.options.cufft:
            self.copy("*", "nvcc", os.path.join("libcufft", "cufft"))
            self.copy("*", "nvcc", os.path.join("libcufft", "cufft_dev"))
        if self.options.curand:
            self.copy("*", "nvcc", os.path.join("libcurand", "curand"))
            self.copy("*", "nvcc", os.path.join("libcurand", "curand_dev"))
        if self.options.cusolver:
            self.copy("*", "nvcc", os.path.join("libcusolver", "cusolver"))
            self.copy("*", "nvcc", os.path.join("libcusolver", "cusolver_dev"))
        if self.options.cusparse:
            self.copy("*", "nvcc", os.path.join("libcusparse", "cusparse"))
            self.copy("*", "nvcc", os.path.join("libcusparse", "cusparse_dev"))
        if self.options.npp:
            self.copy("*", "nvcc", os.path.join("libnpp", "npp"))
            self.copy("*", "nvcc", os.path.join("libnpp", "npp_dev"))
        if self.options.nvjpeg:
            self.copy("*", "nvcc", os.path.join("libnvjpeg", "nvjpeg"))
            self.copy("*", "nvcc", os.path.join("libnvjpeg", "nvjpeg_dev"))
        if self.options.cudnn:
            self.copy("LICENSE", "licenses", os.path.join("cudnn"))
            self.copy("*", os.path.join("nvcc", "include"), os.path.join("cudnn", "include"))
            self.copy("*", os.path.join("nvcc", "lib", "x64"), os.path.join("cudnn", "lib"))
            self.copy("*", os.path.join("nvcc", "bin"), os.path.join("cudnn", "bin"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "nvcc"), "*.nvi")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "CUDAVisualStudioIntegration"), "*.nvi")

    def package(self):
        if self.settings.os == "Linux":
            self._package_linux()
        elif self.settings.os == "Windows":
            self._package_windows()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CUDASDK"
        self.cpp_info.names["cmake_find_package_multi"] = "CUDASDK"

        components = ["cudart", "cudart_static", "cuda_driver", "cublas", "cublas_static", "cufft", "cufftw", 
                          "cufft_static", "cufftw_static", "curand", "curand_static", "cusolver", "cusolver_static",
                          "cusparse", "cusparse_static", "cupti", "cupti_static", "nppc", "nppc_static", "nppial",
                          "nppial_static", "nppicc", "nppicc_static", "nppicom", "nppicom_static", "nppidei", 
                          "nppidei_static", "nppif", "nppif_static", "nppig", "nppig_static", "nppim", "nppim_static",
                          "nppist", "nppist_static", "nppisu", "nppisu_static", "nppitc", "nppitc_static", "npps", 
                          "npps_static", "nvblas", "nvrtc", "nvml", "OpenCL", "culibos"]

        self_ver = Version(self.version)
        if self_ver >= Version("9.2.0"):
            components += ["cufft_static_nocallback"]
        if self_ver >= Version("10.0"):
            components += ["nvjpeg", "nvjpeg_static", "nvtx3"]
        if self_ver < Version("10.0"):
            components += ["nvToolsExt"]
        if self_ver >= Version("10.1"):
            components += ["cublasLt", "cublasLt_static"]
        if self_ver < Version("11.0"):
            components += ["nvgraph", "nvgraph_static"]
        if self_ver >= Version("11.4"):
            components += ["cuFile", "cuFile_static", "cuFile_rdma", "cuFile_rdma_static"]
        if self_ver >= Version("11.1"):
            components += ["nvptxcompiler"]
        
        for component in components:
            name = component.lower()
            self.cpp_info.components[name].set_property("cmake_target_name", "CUDASDK::" + component)
            self.cpp_info.components[name].lib = []
            self.cpp_info.components[name].libdirs = []
            self.cpp_info.components[name].resdirs = []
            self.cpp_info.components[name].bindirs = []
            self.cpp_info.components[name].includedirs = []
        # not sure due to policy CMP0149
        #self.conf_info["tools.microsoft:winsdk_version="]
            
        # setting sdk path information
        self.env_info.CUDASDK_PATH = self.package_folder
        self.env_info.CUDASDK_VERSION = self.version
        if self.settings.os == "Windows":
            self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", os.path.join(self.package_folder))
            # setting toolkit & cuda root 
            self.env_info.CUDAToolkit_ROOT = os.path.join(self.package_folder, "nvcc")
            self.env_info.CUDA_PATH = os.path.join(self.package_folder, "nvcc")
            # adding nvcc to path
            self.env_info.PATH.append(os.path.join(self.package_folder, "nvcc", "bin"))
        else:        
            self.conf_info.update("tools.build:compiler_executables", { "cuda": os.path.join(self.package_folder, "bin", "nvcc") })
            #self.buildenv_info.define("CUDAToolkit_ROOT", os.path.join(self.package_folder, "bin"))
            
            # setting toolkit & cuda root 
            #self.env_info.CUDAToolkit_ROOT = self.package_folder
            #self.env_info.CUDA_PATH = self.package_folder, "nvcc"
            # adding nvcc to path
            #self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
            pass