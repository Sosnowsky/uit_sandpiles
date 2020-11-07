#ifndef BTWSIM_SRC_DYNAMICS_BTWRANDOM2DYNAMICS_H_
#define BTWSIM_SRC_DYNAMICS_BTWRANDOM2DYNAMICS_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include "ModelDynamics.h"

class BTWRandom2Dynamics : public ModelDynamics {
 public:
  long InitializeMap(std::vector<std::vector<int>> &grid) override;
  int AddGrain(std::deque<std::pair<int, int>> &crits,
               std::vector<std::vector<int>> &grid) override;

  /**
   * Evolves the given site, and places any new crits in the given deque.
   * Evolves according to the rules: m_grid[i][j] -= 2; propagate(i +
   * ModelUtils::GetRandomNeighbor(), j); propagate(i, j +
   * ModelUtils::GetRandomNeighbor());
   * @param crits
   * @param site
   */
  int Evolve(std::deque<std::pair<int, int>> &crits,
             std::vector<std::vector<int>> &grid) override;
};

#endif  // BTWSIM_SRC_DYNAMICS_BTWRANDOM2DYNAMICS_H_
