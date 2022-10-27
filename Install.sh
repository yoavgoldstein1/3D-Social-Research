#!/bin/sh

# Author : Yoav Goldstein

sudo killall apt apt-get
pip install pyrealsense2
pip install seaborn
pip install keyboard
sudo apt-get -qq install -y libatlas-base-dev libprotobuf-dev libleveldb-dev libsnappy-dev libhdf5-serial-dev protobuf-compiler libgflags-dev libgoogle-glog-dev liblmdb-dev opencl-headers ocl-icd-opencl-dev libviennacl-dev
sudo apt install libgoogle-glog-dev
sudo apt-get install -y libopencv-dev
sudo apt-get install -y libboost-all-dev
sudo apt-get install -y ffmpeg
pip install opencv-python


# Remove old installation directories
sudo rm -rf openpose/
sudo rm -rf openpose.avi
sudo rm -rf output.mp4
sudo rm -rf video.mp4
sudo rm -rf youtube.mp4
sudo rm -rf build
sudo rm -rf Outputs
sudo rm -rf cmake*