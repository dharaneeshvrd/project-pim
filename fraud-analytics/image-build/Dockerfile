# Use RHEL9.3 UBI as the base image
FROM registry.access.redhat.com/ubi9/ubi

# Update image and install necessary libraries
RUN yum update --disableplugin=subscription-manager -y && \
    yum install -y git wget gcc gcc-c++ libgcc cmake make python3.12-pip python3.12 python3.12-devel libjpeg-turbo gcc-gfortran rsync libxcrypt-compat graphviz unixODBC-devel gcc-toolset-13 unzip java-11-openjdk java-11-openjdk-devel zip patch openssl-devel sqlite-devel lz4-devel bzip2-devel brotli-devel llvm-devel libevent-devel freetype-devel gmp-devel  libjpeg-turbo-devel cargo zlib-devel libffi-devel numactl-libs libzstd --disableplugin=subscription-manager && \
    yum clean all -y

# Install EPEL repository and nmon
RUN dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \
    dnf -y install nmon && \
    dnf clean all

# Setting up Python environment
ENV VIRTUAL_ENV="/testenv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SITE_PACKAGE_PATH="$VIRTUAL_ENV/lib64/python3.12/site-packages/"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$SITE_PACKAGE_PATH/libprotobuf/lib64/:$SITE_PACKAGE_PATH/openblas/lib/:$SITE_PACKAGE_PATH/:$SITE_PACKAGE_PATH/ffmpeg/lib/:$SITE_PACKAGE_PATH/libvpx/lib/:$SITE_PACKAGE_PATH/lame/lib/:$SITE_PACKAGE_PATH/hdf5/lib/"
ENV PYTHONPATH="$SITE_PACKAGE_PATH:$PYTHONPATH"
ENV CPATH="$VIRTUAL_ENV/include:$CPATH"

# Set Python3.12 as default
RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
RUN alternatives --set python3 /usr/bin/python3.12

# Copy requirements, wheels
COPY wheels /wheels
COPY requirements.txt .

# Create venv and install open-ce wheels
RUN python3.12 -m venv testenv
ENV PATH="/testenv/bin:$PATH"
RUN source testenv/bin/activate && \
	pip install --upgrade pip && \
	pip install cmake pyyaml packaging && \
        pip install -r requirements.txt


# Copy degradation_fix.patch
COPY degradation_fix.patch /testenv/lib64/python3.12/site-packages/

RUN cd /testenv/lib64/python3.12/site-packages/ && ls 

# Clone OpenBLAS to build from source
RUN source testenv/bin/activate && \
	cd /testenv/lib64/python3.12/site-packages/ && \
	git clone https://github.com/OpenMathLib/OpenBLAS.git && \
	cd OpenBLAS/ && \
	sed -i 's/if (width < switch_ratio && width > 1) {/if (width < switch_ratio) {/g' driver/level3/level3_thread.c && \
	#git rev-parse HEAD && \
	#patch -p1 --reject < ../degradation_fix.patch && \
	#cat ../degradation_fix.patch && \
	#cat driver/level3/level3_thread.c && \
	#patch -p1 < ../degradation_fix.patch && \
        #git apply ../degradation_fix.patch && \
	#git status && \
	make TARGET=POWER7 BINARY=64 USE_OPENMP=1 DYNAMIC_ARCH=1 && \
	cd ..; cd openblas/lib; mkdir bkup; mv libopenblas* bkup/ && \
	cd ../../OpenBLAS && \
	cp libopenblas* ../openblas/lib/ && \
	ln -sf libopenblasp-r0.3.29.dev.so libopenblas.so && \
	ln -sf libopenblasp-r0.3.29.dev.so libopenblas.so.0 && \
	ln -sf libopenblasp-r0.3.29.dev.a libopenblas.a

# Enable GCC 13
ENV CC=/opt/rh/gcc-toolset-13/root/usr/bin/gcc
ENV CXX=/opt/rh/gcc-toolset-13/root/usr/bin/g++
ENV PATH=/opt/rh/gcc-toolset-13/root/usr/bin:$PATH

# Confirm GCC & G++ are accessible
RUN $CC --version && $CXX --version

#RUN source /opt/rh/gcc-toolset-13/enable && \
#    source testenv/bin/activate && \
#    export CC=/opt/rh/gcc-toolset-13/root/usr/bin/gcc && \
#    export CXX=/opt/rh/gcc-toolset-13/root/usr/bin/g++ && \
#    export SITE_PACKAGE_PATH=$VIRTUAL_ENV/lib64/python3.12/site-packages/ && \
#    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$SITE_PACKAGE_PATH/libprotobuf/lib64/:$SITE_PACKAGE_PATH/openblas/lib/:$SITE_PACKAGE_PATH/:$SITE_PACKAGE_PATH/ffmpeg/lib/:$SITE_PACKAGE_PATH/libvpx/lib/:$SITE_PACKAGE_PATH/lame/lib/" && \
#    git clone --recursive -b v2.6.0 https://github.com/pytorch/pytorch.git && \
#    cd pytorch/ && \
#    git submodule sync && \
#    git submodule update --init --recursive --jobs 1 && \
#    USE_NNPACK=0 USE_XNNPACK=0 USE_QNNPACK=0 USE_PYTORCH_QNNPACK=1 python setup.py develop 2>&1 | tee build.log && \
#    python setup.py install

RUN source /opt/rh/gcc-toolset-13/enable && \
    source testenv/bin/activate && \
    export CC=/opt/rh/gcc-toolset-13/root/usr/bin/gcc && \
    export CXX=/opt/rh/gcc-toolset-13/root/usr/bin/g++ && \
    export SITE_PACKAGE_PATH=$VIRTUAL_ENV/lib64/python3.12/site-packages/ && \
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$SITE_PACKAGE_PATH/libprotobuf/lib64/:$SITE_PACKAGE_PATH/openblas/lib/:$SITE_PACKAGE_PATH/:$SITE_PACKAGE_PATH/ffmpeg/lib/:$SITE_PACKAGE_PATH/libvpx/lib/:$SITE_PACKAGE_PATH/lame/lib/"

RUN source testenv/bin/activate && \
	pip install pandas transformers accelerate

# Copy additional files
COPY extra/* /extra/
COPY linux_inference_endpoint.py /

# Expose port 5000
EXPOSE 5000

# Set the default command to run your Python script
CMD ["python3", "linux_inference_endpoint.py"]
