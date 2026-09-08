#include "kartpad/mii/player_identity.h"
#include <fstream>
#include <filesystem>
int main(int argc, char** argv) {
  if (argc != 2) return 1;
  const std::filesystem::path root(argv[1]);
  auto database = kartpad::mii::CreateSeedDatabase({2, 17, 171, 16, 32, 48});
  std::vector<uint8_t> save(kartpad::mii::kRksysSize, 0);
  std::copy_n("RKSD0006", 8, save.begin());
  const auto id = kartpad::mii::MiiCreateId(database, 0);
  for (size_t slot = 0; slot < 2; ++slot) {
    const size_t offset = 8 + slot * kartpad::mii::kRksysLicenseSize;
    std::copy_n("RKPD", 4, save.begin() + offset);
    std::copy(id.begin(), id.end(), save.begin() + offset + kartpad::mii::kRksysCreateIdOffset);
    kartpad::mii::WriteMiiName(save, offset + kartpad::mii::kRksysMiiNameOffset, "Player");
    save[offset + 0x90] = 0x72;
  }
  kartpad::mii::UpdateRksysCrc(save);
  for (const auto& [name, bytes] : {std::pair{"mii.dat", database}, std::pair{"save.dat", save}}) {
    std::ofstream out(root / name, std::ios::binary);
    out.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    if (!out) return 2;
  }
}
