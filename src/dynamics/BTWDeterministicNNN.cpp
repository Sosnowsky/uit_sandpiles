#include "BTWDeterministicNNN.h"
#include <deque>
#include <utility>
#include <vector>
#include "ModelUtils.h"

long BTWDeterministicNNN::InitializeMap(std::vector<std::vector<int>> &grid) {
  int size = grid.size();
  long total_grains = 0;
  for (int i = 0; i < size; i++) {
    std::vector<int> row;
    for (int j = 0; j < size; j++) {
      int amount = ModelUtils::GetRandomInt() % CRITICAL_TRESHOLD;
      total_grains += amount;
      grid[i][j] = amount;
    }
  }
  return total_grains;
}

int BTWDeterministicNNN::AddGrain(std::deque<std::pair<int, int>> &crits,
                                  std::vector<std::vector<int>> &grid) {
  int size = grid.size();

  int i = ModelUtils::GetRandomInt() % size;
  int j = ModelUtils::GetRandomInt() % size;
  grid[i][j]++;

  if (grid[i][j] >= CRITICAL_TRESHOLD) crits.emplace_back(i, j);
  return 1;
}

int BTWDeterministicNNN::Evolve(std::deque<std::pair<int, int>> &crits,
                                std::vector<std::vector<int>> &grid) {
  std::deque<std::pair<int, int>>
      new_crits;  // Stores the positions of unstable guys
  int size = grid.size();
  int grains_lost = 0;
  for (auto &p : crits) {
    int i = p.first;
    int j = p.second;
    if (grid[i][j] < CRITICAL_TRESHOLD) continue;

    auto propagate = [&](int a, int b) {
      if (a >= 0 and a < size and b >= 0 and b < size) {
        if (++grid[a][b] >= CRITICAL_TRESHOLD) {
          new_crits.emplace_back(a, b);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    grid[i][j] -= CRITICAL_TRESHOLD;
    propagate(i + 1, j + 1);
    propagate(i + 1, j);
    propagate(i + 1, j - 1);
    propagate(i, j + 1);
    propagate(i, j - 1);
    propagate(i - 1, j + 1);
    propagate(i - 1, j);
    propagate(i - 1, j - 1);

    if (grid[i][j] >= CRITICAL_TRESHOLD) {
      new_crits.emplace_back(i, j);
    }
  }
  crits = new_crits;
  return -grains_lost;
}
