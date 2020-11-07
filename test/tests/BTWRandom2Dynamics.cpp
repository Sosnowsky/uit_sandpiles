#include "../src/dynamics/BTWRandom2Dynamics.h"
#include <gtest/gtest.h>

class BTWRandom2DynamicsTest : public BTWRandom2Dynamics,
                               public ::testing::Test {
 public:
  BTWRandom2DynamicsTest() : BTWRandom2Dynamics() {}

 protected:
  ~BTWRandom2DynamicsTest() override = default;
};

TEST_F(BTWRandom2DynamicsTest, EvolveClassical) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[1][1] = 4;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(1, 1);
  ASSERT_EQ(Evolve(crits, grid), 0);
  ASSERT_EQ(grid[1][1], 2);
  ASSERT_TRUE(grid[2][1] == 1 xor grid[0][1] == 1);
  ASSERT_TRUE(grid[1][2] == 1 xor grid[1][0] == 1);
}

TEST_F(BTWRandom2DynamicsTest, NewCrits) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[1][1] = 4;
  grid[0][1] = 3;
  grid[2][1] = 3;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(1, 1);
  ASSERT_EQ(Evolve(crits, grid), 0);
  ASSERT_EQ(grid[1][1], 2);
  ASSERT_EQ(crits.size(), 1);
}
