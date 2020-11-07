#ifndef BTWSIM_SRC_FORESTFIREMODEL_H_
#define BTWSIM_SRC_FORESTFIREMODEL_H_

#include <chrono>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

enum site_state { empty, tree, burning };

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
  ForestFireModel(std::string output_filename, int size);

  /**
   * Initializes the grid randomly.
   */
  void InitializeMap();

  /**
   * Runs the forest fire model for steps steps implements the model described
   * in : https://en.wikipedia.org/wiki/Forest-fire_model With some
   * modifications to make it run faster: each timestamp
   * grow_trees_per_time_step sites are chosen randomly, if they are empty, a
   * new tree is grown. Each timestamp, with probability fire_probability, a
   * site is chosen randomly, if it is a tree, it is set on fire.
   * @param pre_steps Number of steps run without writing data.
   * @param steps Number of steps run writing data.
   */
  void Run(int steps, double fire_probability, int grow_trees_per_time_step);

  int GetBurningTrees() const;
  int GetTrees() const;

  std::vector<std::vector<site_state>> &GetMap();
  /**
   * Prints the grid data in std output. Only used for debug/dev.
   */
  void PrintMap();

 private:
  std::vector<std::vector<site_state>> m_grid;
  const int m_size;
  int m_trees;
  std::deque<std::pair<int, int>> m_burning_tree_pos;
  std::ofstream m_output;
  std::ofstream m_stats;

  void SaveData();
  void Step();
  void SetTreeOnFire();
  void GrowTree();
};

#endif  // BTWSIM_SRC_FORESTFIREMODEL_H_
