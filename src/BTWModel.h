#ifndef SANDPILESCPP__BTWMODEL_H_
#define SANDPILESCPP__BTWMODEL_H_

#include "dynamics/ModelDynamics.h"
#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <memory>
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
  BTWModel(const std::string &output_filename,
           const std::string &stats_filename, int size,
           std::unique_ptr<ModelDynamics> dynamics);

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
   * @param pre_run Whether the system should run to criticality without writing
   * output.
   * @param steps Number of steps run writing data.
   * @param frequency_grains How often should grains be added on average. If set
   * to -1, it runs the classical slow driven model, for 1 > frequency_grains >
   * 0, (steps * frequency_grains) grains will be added at uniformly randomly
   * distributed times after pre_steps have been run.
   */
  void Run(bool pre_run, int steps, double frequency_grains);

  /**
   * Prints the grid data in std output. Only used for debug/dev.
   */
  void PrintMap();
  int GetCriticalSites();

protected:
  constexpr static double MAX_CHANGE_TO_SOC =
      0.001; // Used to detect when the systems arrives at SOC

  std::unique_ptr<ModelDynamics> m_dynamics;
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

  void RunToCriticality();
  void HandleRunningModel(double frequency);
  void CheckStatsAndWriteIfNecessary();
  void SaveData();
};

#endif // SANDPILESCPP__BTWMODEL_H_
