#include "ForestFireModel.h"
#include <algorithm>
#include <deque>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

ForestFireModel::ForestFireModel(std::string output_filename, int size)
    : m_size(size) {
  m_output.open(output_filename);
  m_output << "burning_trees,trees" << std::endl;
}

void ForestFireModel::InitializeMap() {
  m_trees = 0;
  for (int i = 0; i < m_size; i++) {
    std::vector<site_state> row;
    for (int j = 0; j < m_size; j++) {
      int amount = rand() % 2;
      if (amount == site_state::tree) m_trees++;
      row.push_back(site_state(amount));
    }
    m_grid.push_back(row);
  }
}

std::vector<std::vector<site_state>> &ForestFireModel::GetMap() {
  return m_grid;
}

int ForestFireModel::GetBurningTrees() const {
  return m_burning_tree_pos.size();
}

int ForestFireModel::GetTrees() const { return m_trees; }

void ForestFireModel::PrintMap() {
  for (auto &i : m_grid) {
    for (int j : i) {
      std::cout << j << " ";
    }
    std::cout << std::endl;
  }
  std::cout << std::endl;
}

void ForestFireModel::Step() {
  std::deque<std::pair<int, int>> new_burning_tree_pos;

  for (auto &p : m_burning_tree_pos) {
    int i = p.first;
    int j = p.second;

    auto propagate = [&](int a, int b) {
      if (a >= 0 and a < m_size and b >= 0 and b < m_size and
          m_grid[a][b] == site_state::tree) {
        m_trees--;
        m_grid[a][b] = site_state::burning;
        new_burning_tree_pos.emplace_back(a, b);
      }
    };

    m_grid[i][j] = site_state::empty;
    propagate(i + 1, j);
    propagate(i - 1, j);
    propagate(i, j + 1);
    propagate(i, j - 1);
  }
  m_burning_tree_pos = new_burning_tree_pos;
}

void ForestFireModel::SetTreeOnFire() {
  int i = rand() % m_size;
  int j = rand() % m_size;
  if (m_grid[i][j] == site_state::tree) {
    m_grid[i][j] = site_state::burning;
    m_burning_tree_pos.emplace_back(i, j);
    m_trees--;
  }
}

void ForestFireModel::GrowTree() {
  int i = rand() % m_size;
  int j = rand() % m_size;
  if (m_grid[i][j] == site_state::empty) {
    m_grid[i][j] = site_state::tree;
    m_trees++;
  }
}

void ForestFireModel::Run(int steps, double fire_probability,
                          int grow_trees_per_time_step) {
  for (int i = 0; i < steps; i++) {
    if (i % 1000000 == 0)
      std::cout << "Done " << float(i) / float(steps) << std::endl;
    Step();
    for (int j = 0; j < grow_trees_per_time_step; ++j) {
      GrowTree();
    }
    if (float(rand() % 10000) / 10000 < fire_probability) {
      SetTreeOnFire();
    }
    SaveData();
  }
}

void ForestFireModel::SaveData() {
  m_output << m_burning_tree_pos.size() << "," << m_trees << std::endl;
}
