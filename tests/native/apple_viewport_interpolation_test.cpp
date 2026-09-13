// Synthetic camera transforms only: no game files or captured player state.
#include "gx_test_common.hpp"
#include "gx/frame_interpolation.hpp"

namespace {
using namespace aurora;
using namespace aurora::gx;
constexpr size_t PositionOffset = sizeof(Mat4x4<float>);
constexpr size_t NormalOffset = PositionOffset + MaxPnMtx * sizeof(Mat3x4<float>);
using Uniform = std::array<uint8_t, NormalOffset + MaxPnMtx * sizeof(Mat3x4<float>)>;

Mat3x4<float> matrixAt(float x) {
  return {{1, 0, 0, x}, {0, 1, 0, 0}, {0, 0, 1, 0}};
}

auto record(Uniform& source, float x, float viewportY, bool indexed,
            HashType geometry = 1) {
  g_gxState.logicalViewport = {0, viewportY, 640, 240, 0, 1};
  g_gxState.currentPnMtx = 0;
  g_gxState.pnMtx[0].pos = matrixAt(x);
  g_gxState.pnMtx[0].nrm = matrixAt(0);
  std::memcpy(source.data() + PositionOffset, &g_gxState.pnMtx[0].pos, sizeof(Mat3x4<float>));
  std::memcpy(source.data() + NormalOffset, &g_gxState.pnMtx[0].nrm, sizeof(Mat3x4<float>));
  return record_interpolation_draw({.combined = geometry, .pipeline = 2, .texture = 3,
                                    .matrixTopology = 4}, {}, 1,
      {.sourceUniformData = source.data(), .uniformSize = source.size(),
       .projectionOffset = 0, .positionOffset = PositionOffset,
       .normalOffset = NormalOffset, .currentMatrix = 0, .indexedMatrices = indexed});
}

float interpolatedX(size_t allocation) {
  const auto& data = gfx::testing::uniform_allocation(allocation);
  Mat3x4<float> matrix{};
  std::memcpy(&matrix, data.data() + PositionOffset, sizeof(matrix));
  return matrix.m0.w();
}

class AppleViewportInterpolation : public testing::TestWithParam<bool> {
  void SetUp() override {
    set_frame_interpolation_fps(0);
    begin_frame_interpolation();
    set_frame_interpolation_fps(120);
  }
  void TearDown() override {
    set_frame_interpolation_fps(0);
    begin_frame_interpolation();
    gfx::testing::reset_uniform_allocations();
    g_gxState.logicalViewport = {};
  }
};

TEST_P(AppleViewportInterpolation, KeepsExactAndDeformedDrawsInTheirOwnCamera) {
  for (const bool deformed : {false, true}) {
    set_frame_interpolation_fps(0);
    begin_frame_interpolation();
    set_frame_interpolation_fps(120);
    Uniform previous[2]{}, current[2]{};
    begin_frame_interpolation();
    record(previous[0], 0, 0, GetParam());
    record(previous[1], 100, 240, GetParam());
    finalize_frame_interpolation();
    gfx::testing::reset_uniform_allocations();
    begin_frame_interpolation();
    // Each camera's object is now nearest the OTHER camera's previous transform.
    // Reverse submission order as well; camera membership must win over proximity.
    ASSERT_NE(record(current[1], 10, 240, GetParam(), deformed ? 5 : 1)[0].size, 0u);
    ASSERT_NE(record(current[0], 90, 0, GetParam(), deformed ? 5 : 1)[0].size, 0u);
    finalize_frame_interpolation();
    EXPECT_FLOAT_EQ(interpolatedX(0), 55) << "deformed=" << deformed;
    EXPECT_FLOAT_EQ(interpolatedX(1), 45) << "deformed=" << deformed;
  }
}

TEST_P(AppleViewportInterpolation, StillMatchesReorderedDrawsWithinOneCamera) {
  Uniform previous[2]{}, current[2]{};
  begin_frame_interpolation();
  record(previous[0], 0, 0, GetParam());
  record(previous[1], 100, 0, GetParam());
  finalize_frame_interpolation();
  gfx::testing::reset_uniform_allocations();
  begin_frame_interpolation();
  record(current[0], 90, 0, GetParam());
  record(current[1], 10, 0, GetParam());
  finalize_frame_interpolation();
  EXPECT_FLOAT_EQ(interpolatedX(0), 95);
  EXPECT_FLOAT_EQ(interpolatedX(1), 5);
}

TEST_P(AppleViewportInterpolation, NewViewportDoesNotBorrowAnOldCamera) {
  Uniform previous{}, current{};
  begin_frame_interpolation();
  record(previous, 0, 0, GetParam());
  finalize_frame_interpolation();
  gfx::testing::reset_uniform_allocations();
  begin_frame_interpolation();
  const auto ranges = record(current, 100, 240, GetParam());
  finalize_frame_interpolation();
  // Indexed draws may stage a copy to support sibling palette matching. With no
  // sibling in this viewport that copy must retain the current transform.
  if (ranges[0].size != 0) EXPECT_FLOAT_EQ(interpolatedX(0), 100);
  else EXPECT_FALSE(GetParam());
}

TEST_P(AppleViewportInterpolation, PaletteSiblingsShareOnlyWithinTheirViewport) {
  if (!GetParam()) GTEST_SKIP() << "Palette sharing applies only to indexed draws";
  Uniform previous[2]{}, current[3]{};
  begin_frame_interpolation();
  record(previous[0], 0, 0, true);
  record(previous[1], 100, 240, true);
  finalize_frame_interpolation();
  gfx::testing::reset_uniform_allocations();
  begin_frame_interpolation();
  // Equal current matrix bytes do not imply equal camera histories.
  record(current[0], 50, 0, true);
  record(current[1], 50, 240, true);
  record(current[2], 50, 0, true, 99); // New mesh chunk borrows its top-view sibling.
  finalize_frame_interpolation();
  EXPECT_FLOAT_EQ(interpolatedX(0), 25);
  EXPECT_FLOAT_EQ(interpolatedX(1), 75);
  EXPECT_FLOAT_EQ(interpolatedX(2), 25);
}

INSTANTIATE_TEST_SUITE_P(RigidAndIndexed, AppleViewportInterpolation, testing::Bool());
} // namespace
