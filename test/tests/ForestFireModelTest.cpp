#include <gtest/gtest.h>
#include "../src/ForestFireModel.h"

class ForestFireModelTest : public ::testing::Test {
 protected:
  ForestFireModelTest() = default;
  ~ForestFireModelTest() override = default;

 public:
  ForestFireModel model = ForestFireModel("test.txt", 200);
};

TEST_F(ForestFireModelTest, CriticalSitesAtStart) {
  model.InitializeMap();
  std::vector<std::vector<site_state>> &map = model.GetMap();
  int empty_sites = 0;
  int tree_sites = 0;
  int burning_sites = 0;
  for (int i = 0; i < map.size(); i++) {
    for (int j = 0; j < map.size(); j++) {
      int state = map[i][j];
      if (state == 0) {
        ++empty_sites;
      }
      if (state == 1) {
        ++tree_sites;
      }
      if (state == 2) {
        ++burning_sites;
      }
    }
  }
  ASSERT_EQ(model.GetBurningTrees(), burning_sites);
  ASSERT_EQ(model.GetTrees(), tree_sites);
}

TEST_F(ForestFireModelTest, Step) {
  model.InitializeMap();
  model.Run(100, 0.01, 100);
  model.GetTrees();
}
