#include "BTW3dModel.h"
#include "ModelUtils.h"
#include <algorithm>
#include <deque>
#include <iostream>
#include <random>
#include <string>
#include <tuple>
#include <vector>

BTW3dModel::BTW3dModel(std::string output_filename, int size) : m_size(size) {
  m_output.open(output_filename);
  m_output << "critical_cells,total_grains" << std::endl;
}

void BTW3dModel::InitializeMap() {
  m_grid = std::vector<std::vector<std::vector<int>>>(
      m_size,
      std::vector<std::vector<int>>(m_size, std::vector<int>(m_size, 0)));
  for (int i = 0; i < m_size; i++) {
    for (int j = 0; j < m_size; j++) {
      for (int k = 0; k < m_size; k++) {
        int amount = ModelUtils::GetRandomInt() % 6;
        m_grid[i][j][k] = amount;
        m_total_grains += amount;
      }
    }
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
void BTW3dModel::Run(int pre_steps, int steps, double frequency_grains) {
  if (frequency_grains < 0)
    return RunClassical(pre_steps, steps);
  if (frequency_grains > 1) {
    std::cout << "ERROR: Frequency should be <= 1" << std::endl;
    return;
  }
  RunClassical(pre_steps, 0, false);
  int period_grains = int(1 / frequency_grains);

  int t = 0;

  while (t < steps) {
    Step();
    t++;
    SaveData();

    if (t % 1000000 == 0) {
      float perc = float(t) / float(steps + pre_steps) * 100;
      std::cout << "Done " << perc << "%" << std::endl;
    }
    if (t % period_grains == 0) {
      // Time to add a grain
      auto [i, j, k] = AddGrain();
      if (m_grid[i][j][k] >= 4)
        m_criticals.emplace_back(i, j, k);
    }
  }
}

void BTW3dModel::RunClassical(int pre_steps, int steps, bool print) {
  bool arrived_at_soc = false;
  for (int t = 0; t < steps + pre_steps; t++) {
    if (!arrived_at_soc and
        float(m_total_grains) / float(m_size * m_size) > 2.125) {
      arrived_at_soc = true;
      std::cout << "Arrived at critical density 2.125 at step: " << t
                << std::endl;
    }

    if (t % 1000000 == 0 && print) {
      float perc = float(t) / float(steps + pre_steps) * 100;
      std::cout << "Done " << perc << "%" << std::endl;
    }

    if (m_criticals.empty()) {
      auto [i, j, k] = AddGrain();
      if (m_grid[i][j][k] >= 6)
        m_criticals.emplace_back(i, j, k);
    } else
      Step();

    if (t > pre_steps) {
      SaveData();
    }
  }
}

void BTW3dModel::SaveData() {
  m_output << m_criticals.size() << "," << m_total_grains << std::endl;
}

void BTW3dModel::Step() {
  int grains_lost = 0;
  std::deque<std::tuple<int, int, int>>
      new_crits; // Stores the positions of unstable guys

  for (auto [i, j, k] : m_criticals) {
    auto propagate = [&](int a, int b, int c) {
      if (a >= 0 and a < m_size and b >= 0 and b < m_size and c >= 0 and
          c < m_size) {
        if (++m_grid[a][b][c] == 6) {
          new_crits.emplace_back(a, b, c);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    m_grid[i][j][k] -= 6;
    propagate(i + 1, j, k);
    propagate(i - 1, j, k);
    propagate(i, j + 1, k);
    propagate(i, j - 1, k);
    propagate(i, j, k + 1);
    propagate(i, j, k - 1);
  }

  m_total_grains -= grains_lost;
  m_criticals = new_crits;
}

std::tuple<int, int, int> BTW3dModel::AddGrain() {
  int i = ModelUtils::GetRandomInt() % m_size;
  int j = ModelUtils::GetRandomInt() % m_size;
  int k = ModelUtils::GetRandomInt() % m_size;
  m_grid[i][j][k]++;
  m_total_grains++;
  return {i, j, k};
}

int BTW3dModel::GetCriticalSites() { return m_criticals.size(); }

int BTW3dModel::GetTotalGrains() { return m_total_grains; }

std::vector<std::vector<std::vector<int>>> &BTW3dModel::GetGrid() {
  return m_grid;
}
