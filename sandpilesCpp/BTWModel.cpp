#include "BTWModel.h"
#include <deque>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

BTWModel::BTWModel(std::string output_filename, std::string stats_filename,
                   int size)
    : m_size(size) {
  m_output.open(output_filename);
  m_stats.open(stats_filename);
  m_output << "critical_cells,total_grains" << std::endl;
  m_stats << "duration,area,quiet" << std::endl;
}

void BTWModel::InitializeMap() {
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

/**
 * Only output data only when we arrived to critical state, we consider that we
 * arrived to critical state if the average number of grains is over 2.11 per
 * cell (not a very good identification, but good enough to reduce the length of
 * the time series).
 * @param pre_steps
 * @param steps
 */
void BTWModel::Run(int pre_steps, int steps) {
  bool arrived_at_soc = false;
  std::deque<std::pair<int, int>> crits;

  for (int t = 0; t < steps + pre_steps; t++) {
    if (!arrived_at_soc and
        float(m_total_grains) / float(m_size * m_size) > 2.14)
      arrived_at_soc = true;

    if (t % 100000 == 0) std::cout << "Done " << t << std::endl;

    if (crits.empty()) {
      std::pair<int, int> pos_added = AddGrain();
      if (m_grid[pos_added.first][pos_added.second] >= 4)
        crits.emplace_back(pos_added.first, pos_added.second);
    } else
      crits = Step(crits);

    if (arrived_at_soc and t > pre_steps) {
      SaveData(crits.size());
      CheckStatsAndWriteIfNecessary(crits.size());
    }
  }
}

void BTWModel::CheckStatsAndWriteIfNecessary(long crits) {
  if (crits > m_treshold) {
    if (m_quiet != 0) {
      m_stats << m_durations << "," << m_area << "," << m_quiet << std::endl;
      m_quiet = 0;
      m_durations = 0;
      m_area = 0;
    }
    m_durations++;
    m_area += crits;
  } else {
    m_quiet++;
  }
}

void BTWModel::PrintMap() {
  for (auto &i : m_grid) {
    for (int j : i) {
      std::cout << j << " ";
    }
    std::cout << std::endl;
  }
  std::cout << std::endl;
}

void BTWModel::SaveData(int crits) {
  m_output << crits << "," << m_total_grains << std::endl;
}

std::deque<std::pair<int, int>> BTWModel::Step(
    std::deque<std::pair<int, int>> old_crits) {
  int grains_lost = 0;
  std::deque<std::pair<int, int>>
      crits;  // Stores the positions of unstable guys

  for (auto &p : old_crits) {
    int i = p.first;
    int j = p.second;

    auto propagate = [&](int a, int b) {
      if (a >= 0 and a < m_size and b >= 0 and b < m_size) {
        if (++m_grid[a][b] == 4) {
          crits.emplace_back(a, b);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    m_grid[i][j] -= 4;
    propagate(i + 1, j);
    propagate(i - 1, j);
    propagate(i, j + 1);
    propagate(i, j - 1);
  }

  m_total_grains -= grains_lost;
  return crits;
}

std::pair<int, int> BTWModel::AddGrain() {
  int i = rand() % m_size;
  int j = rand() % m_size;
  m_grid[i][j]++;
  m_total_grains++;
  return {i, j};
}
