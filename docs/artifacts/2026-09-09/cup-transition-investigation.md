# Cup completion transition investigation

#131 now confirms Original and Retro; its mention of online does not establish
an identical ceremony transition without matching context. No shared cause with
#128 is established. No additional cup runs or reimports were requested.

Astra Medium inspected pinned symbols and current base translation. GP awards
section is 0x35 (VS awards0x36). Six inspected awards entrypoints are present
without explicit unsupported-operation stubs, including AwardFade::OnInit
0x805BB3BC, AwardResults::OnInit0x805BC1B0, PrepareCup0x805BCF30,
AwardCupModel::Load0x8074C8A8, AwardsMgr::Init0x8078823C and
LoadPlayers0x80789340. This rejects simple omission of these functions, not all
translation or dispatch defects. No definite defect was reproduced.

Pinned Pulsar SlotExpansion.cpp FormatTrackPath bypasses custom track remapping
for MODE_AWARD. CrashExtra.cpp identifies winningrun_demo.szs and
loser_demo.szs. These shared retail resources are useful discriminators; their
absence or corruption on the reporter device is not established.

Next classify the already requested matching process-exits.json entry and final
console excerpt. Existing self-exit/native/Java crash/low-memory reason and
status distinguish paths. Guest/runtime failures may log OS::Panic, OS::Fatal,
PPCHalt, Missing translated function or guest access violations; preserve
relevant PC/LR/CTR to match symbols. DVD read errors suggest checking the named
resource before proposing reimport. Only a classified memory/renderer failure
would justify a same-device 1x versus reported3x transition comparison.

No new instrumentation, code patch, build or physical test in this review.
