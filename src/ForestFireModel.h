//
// Created by sosnovsky on 11/4/20.
//

#ifndef BTWSIM_SRC_FORESTFIREMODEL_H_
#define BTWSIM_SRC_FORESTFIREMODEL_H_

#endif //BTWSIM_SRC_FORESTFIREMODEL_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

enum first_state { empty, tree, burning };

class ForestFireModel {
 public:
  /**
   * Initializes a grid of size {@link size} (number of sites given by sites ^
   * 2), output is used to store the timeseries consisting of the total number
   * of unstable sites and the total number of grains in the grid at any given
   * time.
   * @param output_filename
   * @param stats_filename
   */
  ForestFireModel(std::string output_filename, std::string stats_filename, int size);

  /**
   * Initializes the grid randomly.
   */
  void InitializeMap();

  /**
   * Runs the forest fire model for (pre_steps + steps) steps, without writing the data for
   * the first pre_steps steps (in order to avoid writing data before reaching
   * SOC). Implements the model described in :
   * https://en.wikipedia.org/wiki/Forest-fire_model
   * @param pre_steps Number of steps run without writing data.
   * @param steps Number of steps run writing data.
   */
  void Run(int pre_steps, int steps, double fire_probability, double grow_probability);

  /**
   * Prints the grid data in std output. Only used for debug/dev.
   */
  void PrintMap();
  std::pair<int, int> AddGrain();
  int GetCriticalSites();

 private:
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
  void Step();

  /**
   * Runs the infinitely slowly driven model.
   */
  void RunClassical(int pre_steps, int steps, bool print = true);

  /**
   * Runs the running model.
   */
  void RunRunning(int pre_steps, int steps, double frequency_grains);
};
