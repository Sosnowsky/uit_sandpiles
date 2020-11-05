#ifndef SANDPILESCPP__BTWMODEL_H_
#define SANDPILESCPP__BTWMODEL_H_

#endif  // SANDPILESCPP__BTWMODEL_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

class BTWModel {
 public:
  /**
   * Initializes a grid of size {@link size} (number of sites given by sites ^
   * 2), output is used to store the timeseries consisting of the total number
   * of unstable sites and the total number of grains in the grid at any given
   * time.
   * @param output_filename
   * @param stats_filename
   */
  BTWModel(std::string output_filename, std::string stats_filename, int size);

  enum Mode { classical, random_2 };

  /**
   * Initializes the grid randomly.
   */
  void InitializeMap();

  /**
   * Runs the model for (pre_steps + steps) steps, without writing the data for
   * the first pre_steps steps (in order to avoid writing data before reaching
   * SOC).
   * TODO: Drop pre_steps argument by detecting criticality automatically
   * (simplest is to reach state with approximately constant number of total
   * grains).
   * @param pre_steps Number of steps run without writing data.
   * @param steps Number of steps run writing data.
   * @param frequency_grains How often should grains be added on average. If set
   * to -1, it runs the classical slow driven model, for 1 > frequency_grains >
   * 0, (steps * frequency_grains) grains will be added at uniformly randomly
   * distributed times after pre_steps have been run.
   */
  void Run(int pre_steps, int steps, double frequency_grains, Mode mode);

  /**
   * Prints the grid data in std output. Only used for debug/dev.
   */
  void PrintMap();
  std::pair<int, int> AddGrain();
  int GetCriticalSites();

 protected:
  std::vector<std::vector<int>> m_grid;
  std::deque<std::pair<int, int>> m_criticals;
  const int m_size;
  long m_total_grains = 0;
  std::ofstream m_output;
  std::ofstream m_stats;

  int m_treshold = 63;
  long m_durations = 0;
  long m_area = 0;
  long m_quiet = 0;

  void CheckStatsAndWriteIfNecessary();
  void SaveData();
  void Step(Mode mode);

  /**
   * Evolves the given site, and places any new crits in the given deque.
   * Evolves according to the rules: m_grid[i][j] -= 2; propagate(i +
   * ModelUtils::GetRandomNeighbor(), j); propagate(i, j +
   * ModelUtils::GetRandomNeighbor());
   * @param crits
   * @param site
   */
  void Evolve1(std::deque<std::pair<int, int>> &crits,
               std::pair<int, int> site);

  /**
   * Classical algorithm
   * @param crits
   * @param site
   */
  void EvolveClassical(std::deque<std::pair<int, int>> &crits,
                       std::pair<int, int> site);

  /**
   * Runs the infinitely slowly driven model.
   */
  void RunClassical(int pre_steps, int steps, bool print = true);
};