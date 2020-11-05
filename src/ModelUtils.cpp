#include "ModelUtils.h"
#include <algorithm>

double ModelUtils::GetRandomDouble() { return float(rand() % 10000) / 10000; }

int ModelUtils::GetRandomInt() { return rand(); }

int ModelUtils::GetRandomNeighbor() { return GetRandomInt() % 2 == 0 ? 1 : -1; }
