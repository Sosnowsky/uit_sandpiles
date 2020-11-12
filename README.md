Small c++ implementation of some cellular automata models exhibiting self organized criticality.

#### Clone repo
```
git clone https://github.com/Sosnowsky/uit_sandpiles.git 
```
#### Install cmake and boost
```
sudo apt-get update
sudo apt install cmake
sudo apt-get install libboost-all-dev
sudo apt-get install build-essential
```
#### Build
```
cd uit_sandpiles/
mkdir build
cd build/
cmake ..
cmake --build .
cd src/
./btwsim -h
```


