#include <gtest/gtest.h>
#include "../src/BTWModel.h"

class BTWModelTest : public ::testing::Test {
 protected:
  BTWModelTest() = default;
  ~BTWModelTest() override = default;
 public:
  BTWModel model = BTWModel("", "", 50);
};

TEST_F(BTWModelTest, CriticalSitesAtStart) {
  ASSERT_EQ(model.GetCriticalSites(), 0);
}

int main(int argc, char **argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}