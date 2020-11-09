#ifndef BTWSIM_SRC_DYNAMICS_MODELDYNAMICS_H_
#define BTWSIM_SRC_DYNAMICS_MODELDYNAMICS_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

class ModelDynamics {
 public:
  enum dynamics { classical, random2, nnn };

  virtual long InitializeMap(std::vector<std::vector<int>> &grid) = 0;
  virtual int AddGrain(std::deque<std::pair<int, int>> &crits,
                       std::vector<std::vector<int>> &grid) = 0;
  virtual int Evolve(std::deque<std::pair<int, int>> &crits,
                     std::vector<std::vector<int>> &grid) = 0;
};

#endif  // BTWSIM_SRC_DYNAMICS_MODELDYNAMICS_H_
