#include <gtest/gtest.h>
#include "../src/BTWModel.h"

class BTWModelTest : public BTWModel, public ::testing::Test {
 public:
  BTWModelTest() : BTWModel("", "", 50) {}

 protected:
  ~BTWModelTest() override = default;
};

TEST_F(BTWModelTest, EvolveClassical) {
  m_grid = std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  m_grid[1][1] = 4;
  std::deque<std::pair<int, int>> crits;
  EvolveClassical(crits, {1, 1});
  ASSERT_EQ(m_grid[1][1], 0);
  ASSERT_TRUE(m_grid[2][1] == 1 and m_grid[0][1] == 1);
  ASSERT_TRUE(m_grid[1][2] == 1 and m_grid[1][0] == 1);
}

TEST_F(BTWModelTest, Evolve1) {
  m_grid = std::vector<std::vector<int>>(50, std::vector<int>(50, 0));
  m_grid[1][1] = 4;
  std::deque<std::pair<int, int>> crits;
  Evolve1(crits, {1, 1});
  ASSERT_EQ(m_grid[1][1], 2);
  ASSERT_TRUE(m_grid[2][1] == 1 or m_grid[0][1] == 1);
  ASSERT_TRUE(m_grid[1][2] == 1 or m_grid[1][0] == 1);
}

TEST_F(BTWModelTest, CriticalSitesAtStart) { ASSERT_EQ(GetCriticalSites(), 0); }

int main(int argc, char **argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}