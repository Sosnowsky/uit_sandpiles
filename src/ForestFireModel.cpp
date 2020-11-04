#include "ForestFireModel.h"
#include <algorithm>
#include <deque>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

ForestFireModel::ForestFireModel(std::string output_filename, std::string stats_filename,
                                 int size)
    : m_size(size) {
  m_output.open(output_filename);
  m_stats.open(stats_filename);
  m_output << "critical_cells,total_grains" << std::endl;
  m_stats << "duration,area,quiet" << std::endl;
}

void ForestFireModel::InitializeMap() {
  for (int i = 0; i < m_size; i++) {
    std::vector<int> row;
    for (int j = 0; j < m_size; j++) {
      int amount = rand() % 4;
      if (amount < 3) {
        if (rand() % 4 != 1) amount++;
      }
      m_total_grains += amount;
      row.push_back(amount);
    }
    m_grid.push_back(row);
  }
}

void ForestFireModel::Run(int pre_steps, int steps, double fire_probability, double grow_probability) {

}
