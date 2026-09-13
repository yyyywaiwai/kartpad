#include "toml.hpp"
#include <sstream>
#include <cassert>
#include <cstdio>
int main() {
  const char* cases[] = {
    "[paths]\n\"nand_root\" = \"elsewhere\"",
    "[paths]\n'nand_root' = 'elsewhere'",
    "paths.nand_root = \"elsewhere\"",
    "\"paths\".\"nand_root\" = \"elsewhere\"",
    "paths = { nand_root = \"elsewhere\" }",
    "paths = { \"nand_root\" = \"elsewhere\" }",
    "[\"paths\"]\nnand_root = \"elsewhere\"",
    "[paths]\n\"na\\u006ed_root\" = \"elsewhere\"",
  };
  for (const auto* text : cases) {
    std::istringstream input(text);
    const auto document = toml::parse(input, "rating-config-fixture");
    assert(toml::find<std::string>(document, "paths", "nand_root") == "elsewhere");
  }
  std::puts("PASS 8 custom NAND configurations using runtime toml11 parser");
}
