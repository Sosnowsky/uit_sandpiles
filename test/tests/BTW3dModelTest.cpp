#include <gtest/gtest.h>
#include "../src/BTW3dModel.h"

class BTW3dModelTest : public ::testing::Test {
 protected:
  BTW3dModelTest() = default;
  ~BTW3dModelTest() override = default;

 public:
  BTW3dModel model = BTW3dModel("test.txt", 100);
};

TEST_F(BTW3dModelTest, CriticalSitesAtStart) {
  model.InitializeMap();
  model.Run(0, 1000, 1);
  std::vector<std::vector<std::vector<int>>> &map = model.GetGrid();
  long total_grains = 0;
  for (auto &i : map) {
    for (auto &j : i) {
      for (auto &k : j) {
        total_grains += k;
      }
    }
  }
  ASSERT_EQ(model.GetTotalGrains(), total_grains);
}
