#ifndef BTWSIM_SRC_BTW3DMODEL_H_
#define BTWSIM_SRC_BTW3DMODEL_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

class BTW3dModel {
public:
  /**
   * Initializes a grid of size {@link size} (number of sites given by sites ^
   * 2), output is used to store the timeseries consisting of the total number
   * of unstable sites and the total number of grains in the grid at any given
   * time.
   * @param output_filename
   * @param stats_filename
   */
  BTW3dModel(std::string output_filename, int size);

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
   * @param frequency_grains Adds a grain every 1/frequency_grains steps
   */
  void Run(int pre_steps, int steps, double frequency_grains);

  /**
   * Prints the grid data in std output. Only used for debug/dev.
   */
  std::tuple<int, int, int> AddGrain();
  int GetCriticalSites();
  int GetTotalGrains();
  std::vector<std::vector<std::vector<int>>> &GetGrid();

private:
  std::vector<std::vector<std::vector<int>>> m_grid;
  std::deque<std::tuple<int, int, int>> m_criticals;
  const int m_size;
  long m_total_grains = 0;
  std::ofstream m_output;

  void SaveData();
  void Step();

  /**
   * Runs the infinitely slowly driven model.
   */
  void RunClassical(int pre_steps, int steps, bool print = true);
};

#endif // BTWSIM_SRC_BTW3DMODEL_H_
