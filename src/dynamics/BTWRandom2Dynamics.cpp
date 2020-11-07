#include "BTWRandom2Dynamics.h"
#include <deque>
#include <utility>
#include <vector>
#include "ModelUtils.h"

long BTWRandom2Dynamics::InitializeMap(std::vector<std::vector<int>> &grid) {
  int size = grid.size();
  long total_grains = 0;
  for (int i = 0; i < size; i++) {
    std::vector<int> row;
    for (int j = 0; j < size; j++) {
      int amount = ModelUtils::GetRandomInt() % 4;
      total_grains += amount;
      grid[i][j] = amount;
    }
  }
  return total_grains;
}

int BTWRandom2Dynamics::AddGrain(std::deque<std::pair<int, int>> &crits,
                                 std::vector<std::vector<int>> &grid) {
  int size = grid.size();

  int i = ModelUtils::GetRandomInt() % size;
  int j = ModelUtils::GetRandomInt() % size;
  grid[i][j]++;

  if (grid[i][j] >= 4) crits.emplace_back(i, j);
  return 1;
}

int BTWRandom2Dynamics::Evolve(std::deque<std::pair<int, int>> &crits,
                               std::vector<std::vector<int>> &grid) {
  std::deque<std::pair<int, int>>
      new_crits;  // Stores the positions of unstable guys
  int size = grid.size();
  int grains_lost = 0;
  for (auto &p : crits) {
    int i = p.first;
    int j = p.second;
    if (grid[i][j] < 4) continue;

    auto propagate = [&](int a, int b) {
      if (a >= 0 and a < size and b >= 0 and b < size) {
        if (++grid[a][b] >= 4) {
          new_crits.emplace_back(a, b);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    grid[i][j] -= 2;
    propagate(i + ModelUtils::GetRandomNeighbor(), j);
    propagate(i, j + ModelUtils::GetRandomNeighbor());

    if (grid[i][j] >= 4) {
      new_crits.emplace_back(i, j);
    }
  }
  crits = new_crits;
  return -grains_lost;
}
