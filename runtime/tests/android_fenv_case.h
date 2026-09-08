#pragma once
#include <cstdint>
struct AndroidFpCaseResult {
  std::uint64_t value;
  std::uint32_t fpscr, exception;
  bool write;
  int host_flags;
};
using AndroidFpEvaluator = AndroidFpCaseResult (*)(unsigned, std::uint32_t, double, double, double);
extern "C" AndroidFpCaseResult ReferenceFp(unsigned, std::uint32_t, double, double, double);
extern "C" AndroidFpCaseResult CandidateFp(unsigned, std::uint32_t, double, double, double);
