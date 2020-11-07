
#ifndef BTWSIM_SRC_DYNAMICS_BTWCLASSICAL_H_
#define BTWSIM_SRC_DYNAMICS_BTWCLASSICAL_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include "ModelDynamics.h"

class BTWClassicalDynamics : public ModelDynamics {
 public:
  long InitializeMap(std::vector<std::vector<int>> &grid) override;
  int AddGrain(std::deque<std::pair<int, int>> &crits,
               std::vector<std::vector<int>> &grid) override;
  int Evolve(std::deque<std::pair<int, int>> &crits,
             std::vector<std::vector<int>> &grid) override;
};

#endif  // BTWSIM_SRC_DYNAMICS_BTWCLASSICAL_H_
