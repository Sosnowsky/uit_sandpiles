#include "../src/dynamics/BTWClassicalDynamics.h"
#include <gtest/gtest.h>

class BTWClassicalModelTest : public BTWClassicalDynamics,
                              public ::testing::Test {
 public:
  BTWClassicalModelTest() : BTWClassicalDynamics() {}

 protected:
  ~BTWClassicalModelTest() override = default;
};

TEST_F(BTWClassicalModelTest, EvolveClassical) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[1][1] = 4;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(1, 1);
  ASSERT_EQ(Evolve(crits, grid), 0);
  ASSERT_EQ(grid[1][1], 0);
  ASSERT_TRUE(grid[2][1] == 1 and grid[0][1] == 1);
  ASSERT_TRUE(grid[1][2] == 1 and grid[1][0] == 1);
}
