#include "BTWModel.h"
#include <algorithm>
#include <deque>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>
#include "ModelUtils.h"

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
void BTWModel::Run(int pre_steps, int steps, double frequency_grains,
                   Mode mode) {
  if (frequency_grains < 0) return RunClassical(pre_steps, steps);
  if (frequency_grains > 1) {
    std::cout << "ERROR: Frequency should be <= 1" << std::endl;
    return;
  }
  RunClassical(pre_steps, 0, true);

  int total_grains_to_add = int(steps * frequency_grains);
  std::vector<int> add_grain_times;

  std::default_random_engine generator;
  std::uniform_int_distribution<int> distribution(0, steps);

  for (int i = 0; i < total_grains_to_add; i++) {
    add_grain_times.push_back(distribution(generator));
  }

  std::sort(add_grain_times.begin(), add_grain_times.end(), std::less<>());

  int t = 0;
  int grain_inx = 0;

  auto update = [&]() {
    Step(mode);
    t++;
    SaveData();
    CheckStatsAndWriteIfNecessary();

    if (t % 1000000 == 0) {
      float perc = float(t) / float(steps + pre_steps) * 100;
      std::cout << "Done " << perc << "%" << std::endl;
    }
  };

  while (grain_inx < add_grain_times.size()) {
    while (t < add_grain_times[grain_inx]) update();

    // Time to add a grain
    std::pair<int, int> pos_added = AddGrain();
    if (m_grid[pos_added.first][pos_added.second] >= 4)
      m_criticals.emplace_back(pos_added.first, pos_added.second);
    grain_inx++;
  }

  while (t < steps) update();
}

void BTWModel::RunClassical(int pre_steps, int steps, bool print) {
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
      std::cout << "Done " << perc << "% total " << m_total_grains << std::endl;
    }

    if (m_criticals.empty()) {
      std::pair<int, int> pos_added = AddGrain();
      if (m_grid[pos_added.first][pos_added.second] >= 4)
        m_criticals.emplace_back(pos_added.first, pos_added.second);
    } else
      Step(Mode::classical);

    if (t > pre_steps) {
      SaveData();
      CheckStatsAndWriteIfNecessary();
    }
  }
}

void BTWModel::CheckStatsAndWriteIfNecessary() {
  if (m_criticals.size() > m_treshold) {
    if (m_quiet != 0) {
      m_stats << m_durations << "," << m_area << "," << m_quiet << std::endl;
      m_quiet = 0;
      m_durations = 0;
      m_area = 0;
    }
    m_durations++;
    m_area += m_criticals.size();
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

void BTWModel::SaveData() {
  m_output << m_criticals.size() << "," << m_total_grains << std::endl;
}

void BTWModel::Step(Mode mode) {
  std::deque<std::pair<int, int>>
      new_crits;  // Stores the positions of unstable guys

  for (auto &p : m_criticals) {
    switch (mode) {
      case random_2:
        Evolve1(new_crits, p);
        break;
      case classical:
        EvolveClassical(new_crits, p);
        break;
    }
  }

  m_criticals = new_crits;
}

void BTWModel::Evolve1(std::deque<std::pair<int, int>> &crits,
                       std::pair<int, int> site) {
  int i = site.first;
  int j = site.second;
  int grains_lost = 0;

  auto propagate = [&](int a, int b) {
    if (a >= 0 and a < m_size and b >= 0 and b < m_size) {
      if (++m_grid[a][b] == 4) {
        crits.emplace_back(a, b);
      }
    } else
      ++grains_lost;
  };

  // Increment and store for all neighbors
  m_grid[i][j] -= 2;
  propagate(i + ModelUtils::GetRandomNeighbor(), j);
  propagate(i, j + ModelUtils::GetRandomNeighbor());

  if (m_grid[i][j] >= 4) {
    crits.emplace_back(i, j);
  }
  m_total_grains -= grains_lost;
}

void BTWModel::EvolveClassical(std::deque<std::pair<int, int>> &crits,
                               std::pair<int, int> site) {
  int i = site.first;
  int j = site.second;
  int grains_lost = 0;

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

  if (m_grid[i][j] >= 4) {
    crits.emplace_back(i, j);
  }
  m_total_grains -= grains_lost;
}

std::pair<int, int> BTWModel::AddGrain() {
  int i = rand() % m_size;
  int j = rand() % m_size;
  m_grid[i][j]++;
  m_total_grains++;
  return {i, j};
}

int BTWModel::GetCriticalSites() { return m_criticals.size(); }
