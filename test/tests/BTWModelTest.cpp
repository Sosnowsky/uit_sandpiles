#include <gtest/gtest.h>
#include "../src/BTWModel.h"

class BTWModelTest : public ::testing::Test {
 protected:
  BTWModel model =
      BTWModel("", "", 50, std::unique_ptr<ModelDynamics>(nullptr));
};

TEST_F(BTWModelTest, CriticalSitesAtStart) {
  ASSERT_EQ(model.GetCriticalSites(), 0);
}

int main(int argc, char **argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}