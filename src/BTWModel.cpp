#include "BTWModel.h"
#include "ModelUtils.h"
#include <iostream>
#include <string>
#include <utility>
#include <vector>

BTWModel::BTWModel(const std::string &output_filename,
                   const std::string &stats_filename, int size,
                   std::unique_ptr<ModelDynamics> mode)
    : m_size(size), m_dynamics(std::move(mode)) {
  m_output.open(output_filename);
  m_stats.open(stats_filename);
  m_output << "critical_cells,total_grains" << std::endl;
  m_stats << "duration,area,quiet" << std::endl;
}

void BTWModel::InitializeMap() {
  m_grid = std::vector<std::vector<int>>(m_size, std::vector<int>(m_size, 0));
  m_total_grains = m_dynamics->InitializeMap(m_grid);
}

/**
 * Only output data only when we arrived to critical state, we consider that we
 * arrived to critical state if the average number of grains is over 2.11 per
 * cell (not a very good identification, but good enough to reduce the length of
 * the time series).
 * @param pre_steps
 * @param steps
 */
void BTWModel::Run(bool run, int steps, double frequency) {
  if (run)
    RunToCriticality();

  for (int t = 0; t < steps; t++) {
    if (t % (1000 * 1000) == 0) {
      float perc = float(t) / float(steps) * 100;
      std::cout << "Done " << perc << "% total " << m_total_grains << std::endl;
    }

    if (frequency > 0)
      HandleRunningModel(frequency);

    if (m_criticals.empty() and frequency <= 0) {
      m_total_grains += m_dynamics->AddGrain(m_criticals, m_grid);
    } else
      m_total_grains += m_dynamics->Evolve(m_criticals, m_grid);

    SaveData();
    CheckStatsAndWriteIfNecessary();
  }
}

/**
 * For frequency in (0, 1] add a grain with probability frequency. For frequency
 * > 1 add int(frequency) grains.
 * @param frequency
 */
void BTWModel::HandleRunningModel(double frequency) {
  if (frequency > 0 and frequency <= 1 and
      ModelUtils::GetRandomDouble() < frequency) {
    m_total_grains += m_dynamics->AddGrain(m_criticals, m_grid);
    return;
  }
  if (frequency > 1) {
    int to_add = int(frequency);
    while (to_add--)
      m_total_grains += m_dynamics->AddGrain(m_criticals, m_grid);
  }
}

/**
 * Runs the model without writing the data, until the change in total grains is small.
 */
void BTWModel::RunToCriticality() {
  while (true) {
    long grains_before = m_total_grains;
    std::cout << "Waiting to arrive to criticality... Total grains: "
              << m_total_grains << std::endl;
    for (int i = 0; i < m_size * m_size; i++) {
      if (m_criticals.empty()) {
        m_total_grains += m_dynamics->AddGrain(m_criticals, m_grid);
      } else
        m_total_grains += m_dynamics->Evolve(m_criticals, m_grid);
    }
    long grains_after = m_total_grains;
    if (std::abs(float(grains_after - grains_before) / float(grains_before)) <
        MAX_CHANGE_TO_SOC) {
      return;
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

int BTWModel::GetCriticalSites() { return m_criticals.size(); }
