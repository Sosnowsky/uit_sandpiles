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
  void InitializeMap();
  void Run(int pre_steps, int steps);
  void CheckStatsAndWriteIfNecessary(long crits);
  void PrintMap();
  void SaveData(int crits);
  std::deque<std::pair<int, int>> Step(
      std::deque<std::pair<int, int>> old_crits);
  std::pair<int, int> AddGrain();

 private:
  std::vector<std::vector<int>> m_grid;
  const int m_size = 2048;
  const int m_steps = 200 * 1000 * 1000;
  const int m_pre_steps = 20 * 1000 * 1000;
  long m_total_grains = 0;
  std::ofstream m_output;
  std::ofstream m_stats;

  int m_treshold = 63;
  long m_durations = 0;
  long m_area = 0;
  long m_quiet = 0;
};