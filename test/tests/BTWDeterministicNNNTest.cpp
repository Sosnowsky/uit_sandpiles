#include <gtest/gtest.h>
#include "../src/dynamics/BTWDeterministicNNN.h"

class BTWDeterministicNNNTest : public BTWDeterministicNNN,
                                public ::testing::Test {
 public:
  BTWDeterministicNNNTest() : BTWDeterministicNNN() {}

 protected:
  ~BTWDeterministicNNNTest() override = default;
};

TEST_F(BTWDeterministicNNNTest, Evolve) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[1][1] = 8;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(1, 1);
  ASSERT_EQ(Evolve(crits, grid), 0);
  ASSERT_EQ(grid[1][1], 0);
  ASSERT_TRUE(grid[2][1] == 1 and grid[0][1] == 1);
  ASSERT_TRUE(grid[1][2] == 1 and grid[1][0] == 1);
  ASSERT_TRUE(grid[2][2] == 1 and grid[2][0] == 1);
  ASSERT_TRUE(grid[0][2] == 1 and grid[0][0] == 1);
  ASSERT_TRUE(crits.empty());
}

TEST_F(BTWDeterministicNNNTest, Propagate) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[1][1] = 8;
  grid[2][2] = 7;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(1, 1);
  ASSERT_EQ(Evolve(crits, grid), 0);
  ASSERT_EQ(crits.size(), 1);
  ASSERT_TRUE(grid[2][2] == 8);
}

TEST_F(BTWDeterministicNNNTest, GrainsLost) {
  std::vector<std::vector<int>> grid =
      std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  grid[0][0] = 8;
  std::deque<std::pair<int, int>> crits;
  crits.emplace_back(0, 0);
  ASSERT_EQ(Evolve(crits, grid), -5);
}
