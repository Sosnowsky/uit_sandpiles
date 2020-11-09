#ifndef BTWSIM_SRC_DYNAMICS_BTWDETERMINISTICNNN_H_
#define BTWSIM_SRC_DYNAMICS_BTWDETERMINISTICNNN_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include "ModelDynamics.h"

class BTWDeterministicNNN : public ModelDynamics {
 public:
  long InitializeMap(std::vector<std::vector<int>> &grid) override;
  int AddGrain(std::deque<std::pair<int, int>> &crits,
               std::vector<std::vector<int>> &grid) override;
  int Evolve(std::deque<std::pair<int, int>> &crits,
             std::vector<std::vector<int>> &grid) override;

 private:
  static const int CRITICAL_TRESHOLD = 8;
};

#endif  // BTWSIM_SRC_DYNAMICS_BTWDETERMINISTICNNN_H_
