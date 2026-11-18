# Keepraw Airport History — 全球历史机场代码（IATA 优先）取证与解析差分报告

本目录保存下一阶段全球历史机场代码（重点聚焦 **IATA 历史代码分配、同址更码、跨物理机场代码转移及旧场代码保留**）的原始证据锁、复用原件核验、逐案证据评级、Schema `3.0.0` 候选数据提案、Owner 审批材料以及基于生产解析器 `resolveAirport()` 的真实差分测量结果。

> **合规与边界声明**：本批次严格遵守仓库规则——未修改 `Keepraw-Fly`；未在无正式准入授权情况下修改 `data/airports.json`；未重扫全球数据库或重新下载已锁定原件（复用 24 份已锁定原件，新增获取 33 份未锁定一手原件）；完整原件与提取文本全部保存在 gitignored 的 `work/iata-forensics-wave/` 中，仓库内仅保留元数据、三层 SHA-256 哈希、字符级短引用锚点及原创分析。

---

## A. 最新研究状态审计（Latest Research State Audit）

### 1. 仓库与正式数据基线

| 指标 | 当前核验值 | 说明 |
| --- | --- | --- |
| `main` 最新提交 SHA | `d2e92ea35709e5c7d0697c71eee680bb6be37a30` | PR #37 合并提交 `749dac9`，位于 PR #36 (`bb10464`) 与 PR #35 (`9351651`) 之后 |
| `data/airports.json` SHA-256 | `4573fb7e6fac8e02c8e3f57443599385dffada17b250a29f1a18964f6d6d8cc9` | 与基线逐字节一致 |
| 正式数据版本 (`dataVersion`) | `0.12.0` | 未做未经授权修改 |
| 数据 Schema (`schemaVersion`) | `3.0.0` | 半开区间 `[validFrom, validTo)` |
| 正式物理机场 (`airports`) | **46** | 永久 `apt_<UUIDv4>` 物理机场实体 |
| 正式代码分配 (`assignments`) | **55** | **IATA: 28**，**ICAO: 27** |
| 正式来源 (`sources`) | **112** | 全部为 `verificationStatus: "verified"` |
| 正式名称记录 (`names`) | **3** | 历史官方名称记录 |
| 最近新增正式记录 | `VANM`、`VEAY`、`VOSH`（3 条印度 ICAO） | 每条仅确认 `[2026-06-12, 2026-07-09)` 共 **27** 个完整本地日期 |

### 2. 正式库中「已有永久 `airportId` 但缺少正式 IATA 分配」的 24 座物理机场精确盘点

在 `data/airports.json` 现有的 **46** 座正式物理机场中，仅有 **22** 座拥有正式 IATA 分配（对应 28 条 IATA 分配记录），其余 **24 座正式物理机场目前没有任何正式 IATA 分配（`IATA=0`）**：

1. **11 座印度商业机场（仅有依据 AAI eAIP 窄授权准入的 ICAO 分配，无 IATA 分配）**：
   - `apt_5e325674-a832-4106-807e-7e1e1ef951fe`（Navi Mumbai `VANM` → IATA `NMI`）
   - `apt_96e253c6-48ee-4ca3-b9a1-c34b49df0a68`（Ayodhya `VEAY` → IATA `AYJ`）
   - `apt_1130a628-5e21-4e68-b3e0-178487751f67`（Shivamogga `VOSH` → IATA `RQY`）
   - `apt_fa1bf7a7-a97d-4676-9c9a-7871eda47767`（Shirdi `VASD` → IATA `SAG`）
   - `apt_58a2554f-6a9b-4ad7-bc2c-2550ad21b962`（Kannur `VOKN` → IATA `CNN`）
   - `apt_9acf6a6b-6e22-48c6-881c-d602429a9268`（Itanagar Hollongi `VEHO` → IATA `HGI`）
   - `apt_9e24d5d7-5e1a-4489-b936-2737c438921e`（Sindhudurg `VOSR` → IATA `SDW`）
   - `apt_66034969-b902-4ede-8011-cc87a23070b7`（Kalaburagi `VOGB` → IATA `GBI`）
   - `apt_0342f79b-a035-43b6-88bf-52b9a5e9622f`（Kushinagar `VEKI` → IATA `KBK`）
   - `apt_162c7dfd-e70b-48c7-bbe5-282ede0a5cc9`（Pakyong `VEPY` → IATA `PYG`）
   - `apt_5d260013-75b3-4ec4-8915-7c5ff2a47fc3`（Kurnool `VOKU` → IATA `KJB`）
2. **6 座中国迁建新旧物理机场（已有永久 `airportId`，但当前正式分配数为 0）**：
   - 连云港（`LYG`）：旧白塔埠 `apt_6f1a6ff3-98db-4e58-95fc-cc78bd5aa836` 与新花果山 `apt_64b5eaa6-a984-4816-86d9-d8eb71c91451`
   - 泸州（`LZO`）：旧蓝田 `apt_56b57bca-08d5-4b5e-944e-1e9cce968a0a` 与新云龙 `apt_f11bdf7d-d81d-46fc-a94f-8c8c42d4e245`
   - 宜宾（`YBP`）：旧菜坝 `apt_bbf9f2c1-fc01-4ed7-a4aa-74e6ed8ca45f` 与新五粮液 `apt_8354da99-7d18-4329-bf7b-4ed042a4ad72`
3. **4 座美国迁建新旧物理机场（仅有 ICAO 或 0 分配，无正式 IATA 分配）**：
   - 巴拿马城（`PFN` / `ECP`）：旧场 `apt_d3a329f9-73d0-43f5-90c2-0ba0a0a2e5be`（仅有 `KPFN`）与新场 `apt_74a05fd5-53fa-40f8-a3a6-de8cfd7d5e99`（仅有 `KECP`）
   - 威利斯顿（`ISN` / `XWA`）：旧场 `apt_ba1f9f8c-1849-4092-9e91-d641bddb6bc6`（仅有 `KISN`）与新场 `apt_661b72ea-f84d-4cec-ae34-fddd5e579b3d`（0 分配）
4. **2 座西班牙穆尔西亚迁建新旧物理机场（无正式 IATA 分配）**：
   - 旧圣哈维尔 `apt_a456f7d0-80f7-48b2-81b0-0d762d5d4b12`（仅有 `LELC`，缺 `MJV`）与新穆尔西亚国际机场 `apt_f50aecf6-9778-4db7-9027-0e751ffab63a`（0 分配，缺 `RMU`）
5. **1 座印尼三马林达旧物理机场（无正式 IATA 分配）**：
   - 旧特明东机场 `apt_967383b9-116c-4c3b-a8fb-c67515a3eb83`（0 分配，缺 `SRI`；新场 APT Pranoto `apt_80ab4c35-b89f-40af-a368-bc71b3716d5a` 已有 `AAP`）

### 3. 已完成的全球研究资产与待处理高价值队列

- **`research/evidence/global-code-expansion/`（PR #34）**：完成 1,240,058 个来源修订候选、117,356 个已选历史候选、88,330 个事件组、2,484 个代码关联候选（2,012 IATA / 472 ICAO）、493 个地理复用线索、1,198 个高价值事件组与 845 个取证聚类。扣除已准入的 3 条印度 ICAO 后，`remaining-high-value-queue.json` 剩余 **1,195** 个高价值事件组（其中 **1,111** 个含 IATA）。
- **`research/evidence/global-code-next/`（PR #35）**：完成 32 条边界型候选分配（4 条 IATA：`PBI`、`DJT`、2 条 `BLR`；28 条 ICAO：2 条 `KPBI`/`KDJT` + 26 条乌兹别克斯坦 `UT* → UZ*`）及 16 个物理机场身份绑定的集中式 Owner 决策包（Scope SHA-256: `a2622375de0b06ae716dcfeda26b87e68a66b2a72183a0393e8c255cd847ff5b`），处于待 Owner 批准状态。
- **`research/evidence/global-public-data/`（PR #36 / PR #37）**：完成 21,477 个 Wikidata 实体、16,231 个 OSM 机场对象和 560 个美国 BTS 映射对账，并准备了基于 FAA NASR `2026-10-01` 与 `2026-10-29` 两期 `APT_BASE.csv` 的 **2,458 条美国 ICAO 候选分配**（区间 `[2026-10-02, 2026-10-28)`，反事实新增 63,908 个 resolved 查询，IATA 新增提案为 0）。
- **当前有效准入授权范围**：
  1. `AAI_AIP_AD2_CONTINUITY_AUTHORIZATION` / `AAI_GLOBAL_EXPANSION_CONTINUITY_GRANT`：**仅限已批准的印度 ICAO（`AD 2` 受控页面，间隔 ≤112 天）**，严禁扩展到印度 IATA 或其他国家。
  2. `KR_AIP_AD2_CONTINUITY_AUTHORIZATION`：**仅限韩国 MOLIT eAIP 已批准的 ICAO**（间隔 ≤14 天）。
  3. `CN_CAAC_NAME_RELOCATION_CONTINUITY_AUTHORIZATION`：**仅限已锁定的中国前期准入批次哈希**，不自动覆盖 `LYG`/`LZO`/`YBP`/`ENY`/`AKA`。
  4. 默认人工审查路径（`scripts/reference/admissions.py::validate_admission`）：要求已核验的一手带日期原始来源 + 显式边界与连续性评估 + Owner 真实审查批准记录。

---

## B. 下一批研究优先级排序（Next-Batch Research Priorities）

| 优先级 | 案例 / 候选集 | 代码体系 | 预期解析收益与核心价值 | 证据成熟度 | 授权与准入条件 |
| :---: | --- | --- | --- | --- | --- |
| **P1** | **美国西棕榈滩 `PBI → DJT` / `KPBI → KDJT`（含跨批次 UUID 冲突消解）** | IATA + ICAO | 消解 `global-code-next` (`apt_eb176a20...`) 与 `global-public-data` (`apt_f12cc00a...`) 在 `ourAirports: 3766` 上的重复机场身份冲突，挽救并确认 `KDJT` `[2026-10-02, 2026-10-28)` 的 **26 个真实 `not_found → resolved` 日期**；补齐 `2026-08-18` 当日机场官方公告、加拿大航空（Air Canada）独立航司切换通知及 `iata.org` 发行机构原站证据（证明 `PBI` 转为城市代码保留） | **Tier 1**（4 个独立发行家族交叉印证） | 待 Owner 统一批次批准 + 合并时执行 UUID 归一 |
| **P2** | **吉尔吉斯斯坦玛纳斯 `FRU → BSZ`（同址更码，ICAO `UCFM` 不变）** | IATA | 获取 `iata.org` 原站 `BSZ` 现行分配与 `FRU` 撤销证据；获取乌拉尔航空（Ural Airlines）`2025-08-11` 官方通知，查明 **IATA Resolution 763** 自 `2025-05-09` 起算 90 天生效日（`2025-08-09` 周六）与航司/媒体首个工作日发布日（`2025-08-11` 周一）的法理关系 | **Tier 2**（原站代码身份已闭环；精确切换时刻仍待 `UCFM` NOTAM `A0134/25` 与 `A0140/25` 原始电文） | 保留为 `[2025-08-09, 2025-08-12)` 边界型 `pending` 提案，不提前固化单日边界 |
| **P3** | **印度班加罗尔 `BLR` 跨物理机场转移（HAL `VOBG` → Devanahalli `VOBL`）** | IATA | 跨物理机场（相距 ~30 km）同码交接典范；印度民航部（MoCA）官方宪报 `S.O. 1170(E)` 与修正案 `S.O. 1181(E)` 明确规定 `BLR` 于 `2008-05-24 00:01` 转移至新场，而旧场 HAL 保留 `VOBG` 继续运行 | **Tier 1**（法定公报直接规定代码转移） | 满足印度版权法第 52(1)(q)(i) 条公报例外；待 Owner 批准 `global-code-next` 边界批次 |
| **P4** | **正式库内 13 座缺 IATA 物理机场的 `iata.org` 发行机构身份绑定（11 座印度机场 `NMI`/`AYJ`/`RQY`/`SAG`/`CNN`/`HGI`/`SDW`/`GBI`/`KBK`/`PYG`/`KJB` + 美国 `ECP` + 西班牙 `RMU`）** | IATA | 直接填补 `data/airports.json` 中已有永久 `airportId` 但缺少 IATA 记录的空白，全部取得 `iata.org` 原始页面哈希与提取锚点 | **Tier 2**（发行机构代码绑定已确证，历史起止日期未知） | 严格保留 `validFrom=null, validTo=null` 及 `pending` 状态，绝不借用 AAI ICAO 区间 |
| **P5** | **柬埔寨金边 `PNH` / `KTI`（跨机场复用前手 Kratie）与塞内加尔达喀尔 `DKR` / `DSS`（旧场保留代码反证）** | IATA | `iata.org` 原站证实 `PNH` 已从现行目录撤销、`KTI` 已唯一绑定至德崇国际机场（不再绑定桔井 Kratie）；同时证实达喀尔旧场 `Leopold Sedar Senghor` 至今仍在 `iata.org` 保留 `DKR`（证伪「2017-12-07 停航即代码撤销」的错误假设） | **Tier 1（代码状态与反证）** / **Tier 3（精确历史撤码日）** | 维持正式库现有保守开放边界，防止错误关闭 `DKR` |
| **P6** | **中国迁建（`LYG`、`LZO`、`YBP`、`ENY`、`AKA`、`WUZ`）、日本名古屋（`NGO`/`NKM`）及欧美印跨场更码（`PFN`/`ECP`、`MJV`/`RMU`、`SRI`/`AAP`）** | IATA | 已锁定 2018 民航局航线目录、2021 连云港转场公告、名古屋/中部机场官方 FAQ 及 `iata.org` 新旧码查询（证实 `PFN`、`MJV`、`SRI` 已撤销），明确剩余缺口为「含显式代码切换条款的一手航行通告/IATA 通知」 | **Tier 3**（物理迁建与当前代码明确，缺一手代码生效文书） | 暂不准入，等待获取 CAAC AIC/SUP 或日本 MLIT CAB 2005 AIRAC 原件 |

---

## C. 原始证据取证成果（Primary Evidence Forensic Results）

本轮在不重抓任何已锁定 URL 的前提下，新获取 **33 份一手原始资料**（外加记录 1 个 SSL 超时不可达端点），全部保存在 `work/iata-forensics-wave/`，元数据与引用锚点锁定于 [source-lock.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/source-lock.json)，复用的 **24 份已锁定原件**核验记录于 [reused-evidence.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/reused-evidence.json)。

### 1. 本轮新获取的 34 条取证记录汇总表

| `sourceId` | 来源机构 / `sourceFamily` | 原始 URL | `originalSha256` | `extractedTextSha256` | `normalizedTextSha256` | 引用位置 (`characterStart..End`) | 证据证明的事实 / 不能证明的事实 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `forensics-iata-lookup-djt` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=DJT | `70dca7ffe7300e64…` | `4372a8e1ac7bd864…` | `8bdb12b8f62991a8…` | `5362..5490`: `You searched for "DJT" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves active IATA assignment DJT to West Palm Beach airport, not historical effective date |
| `forensics-iata-lookup-pbi` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=PBI | `a3f490e5b7416f25…` | `8bebe4400893fe28…` | `c8a40ac3c6c99e8f…` | `5362..5468`: `You searched for "PBI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves PBI is retained as West Palm Beach Metropolitan Area code rather than an individual airport code |
| `forensics-us-flydjt-articles-index` | Palm Beach County Department of Airports (`US-PALM-BEACH-COUNTY-OPERATOR`) | https://flydjt.org/articles/ | `0acb317c426c8216…` | `b6dc45606ff2a26b…` | `9e59c8c126fb4e60…` | `2485..2540`: `Airport IATA Code Changes from PBI to DJT Aug. 1…` | Index listing dated operator releases: Aug. 18, 2026 IATA code change release, Jul. 14, 2026 name-change release, Mar. 31, 2026 legislation release |
| `forensics-us-flydjt-iata-article` | Palm Beach County Department of Airports (`US-PALM-BEACH-COUNTY-OPERATOR`) | https://flydjt.org/articles/post/airport-iata-code-changes-from-pbi-to-djt/ | `d806933e3866b7e8…` | `96357cb56bf080d1…` | `f99ee07779ab4023…` | `2380..2543`: `West Palm Beach, FL (Aug. 18, 2026) – The airpor…` | Same-day official operator execution release dated 2026-08-18 confirming IATA PBI to DJT effective 2026-08-18 and distinguishing 2026-07-09 name change |
| `forensics-us-flydjt-rename-announcement` | Palm Beach County Department of Airports (`US-PALM-BEACH-COUNTY-OPERATOR`) | https://flydjt.org/articles/post/palm-beach-international-airport-to-be-renamed-president-donald-j-trump-international-airport/ | `79d7c2268b13af50…` | `dbb64b2ea225cd05…` | `5b232b2f6657ad4b…` | `2382..2624`: `West Palm Beach, FL (March 31, 2026) — On March …` | Operator release dated 2026-03-31 explaining March 30, 2026 state rename statute (effective July 1, 2026) does not change airport code PBI |
| `forensics-ca-aircanada-djt-notice` | Air Canada (`CA-AIR-CANADA-CARRIER-OPS`) | https://www.aircanada.com/us/en/aco/home/book/travel-news-and-updates/2026/airport-code-change-for-west-palm-beach.html | `d06a5e2f6024f768…` | `d9a67e66b014203e…` | `2dbe145b28b56c75…` | `4286..4518`: `West Palm Beach airport code changing from PBI t…` | Carrier operational cutover notice published 2026-07-31 establishing PBI usage until August 18, 2026 and DJT usage starting August 18, 2026 across bookings, boarding passes and displays |
| `forensics-iata-lookup-bsz` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=BSZ | `abc63e2c8a2ff63d…` | `f8da4f0834b4ca2f…` | `3e49181eafe77e40…` | `5362..5453`: `You searched for "BSZ" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA directly assigns BSZ to Bishkek Manas Intl on iata.org |
| `forensics-iata-lookup-fru` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=FRU | `f29162bdebfc5cd2…` | `f84b542395a9fecf…` | `4798a0eeca0062f5…` | `5362..5406`: `You searched for "FRU" No Airport Code found…` | Current issuing-body code directory observation captured 2026-11-18; proves FRU is no longer an active IATA airport or metropolitan location code |
| `forensics-kg-operator-slug-bsz` | Airports of Kyrgyzstan (JSC Manas International Airport) (`KG-AIRPORT-OPERATOR`) | https://airport.kg/ru/news/mezhdunarodnyy-aeroport-manas-smenit-iata-kod-s-fru-na-bsz-s-9-avgusta-2025-goda | `2ec5fc3177b1e7ba…` | `69752f2313b2f017…` | `69752f2313b2f017…` | `0..4`: `News…` | URL slug preserves 9 August 2025 announcement reference; HTML body is a client-rendered shell ('News') without standalone article text |
| `forensics-ru-uralairlines-bsz` | JSC Ural Airlines (`RU-URAL-AIRLINES-CARRIER-OPS`) | https://cargo.uralairlines.ru/en/news/aeroport-manas-v-bishkeke-smenil-kod-iata-s-fru-na-bsz | `048acbfd5157bb83…` | `48de4605aacdabed…` | `769d6f2213d084f5…` | `431..662`: `The "Manas" Airport in Bishkek has changed its I…` | Carrier operational notice published Monday 2025-08-11 referencing IATA Resolution 763 and the 90-day effective period from the May 9, 2025 IATA notification (which equals 2025-08-09) |
| `forensics-uz-uzairways-bsz` | Uzbekistan Airways (`UZ-UZBEKISTAN-AIRWAYS-CARRIER-OPS`) | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG208_sTxLJBqhuETYOcMNsAh8GvyEdYf9yWIt2y9UgI73K9T4lQxDCNBxJB_Fk9j5OE4L5Z5NL6lSeLunsjeRmkGlgESVHpE5NBQyVgg7z_ywD7sqA0Qq_ekYSNr_w | `null` (SSL timeout) | `null` | `null` | 无（连接失败记录） | Retrieval failure only; no source original acquired |
| `forensics-iata-lookup-kti` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=KTI | `9a03eb25babdcad2…` | `dda6d4f7a8903289…` | `d3a0ac87c788e811…` | `5362..5465`: `You searched for "KTI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves KTI is currently assigned to Phnom Penh Techo International (and no longer listed for Kratie) |
| `forensics-iata-lookup-pnh` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=PNH | `589d330cc815af07…` | `07d9d4c0f44d10ed…` | `352db15f6f1b2ec3…` | `5362..5406`: `You searched for "PNH" No Airport Code found…` | Current issuing-body code directory observation captured 2026-11-18; proves PNH is withdrawn from IATA's active airport code directory |
| `forensics-iata-lookup-dkr` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=DKR | `9dd8b6972705e95f…` | `de4332d40b9ec7f4…` | `e2483ae3af8e786a…` | `5362..5490`: `You searched for "DKR" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; disproves withdrawal of DKR from Leopold Sedar Senghor after 2017 commercial transfer to DSS |
| `forensics-iata-lookup-dss` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=DSS | `727c55501e07bcc8…` | `5c7f75a963ade9f6…` | `ca3138838d82e96f…` | `5362..5459`: `You searched for "DSS" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves DSS is assigned to Dakar Blaise Diagne Intl |
| `forensics-iata-lookup-ist` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=IST | `e35bb202de541f71…` | `90386961790974a2…` | `989e91072ebd3708…` | `5362..5491`: `You searched for "IST" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IST is assigned to Istanbul Airport and Istanbul Metropolitan Area |
| `forensics-iata-lookup-isl` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=ISL | `e315a8b972683dea…` | `984daa8d0c3bbca2…` | `9aaa61afc26f12a4…` | `5362..5451`: `You searched for "ISL" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves ISL remains assigned to Istanbul Ataturk in IATA's active directory |
| `forensics-iata-lookup-ecp` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=ECP | `602a8d228f563598…` | `f41944f44855ebfb…` | `2a3a70669758a531…` | `5362..5503`: `You searched for "ECP" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves ECP is assigned to Panama City NW Florida Beaches Int |
| `forensics-iata-lookup-pfn` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=PFN | `925a8675442a5dec…` | `8ed83790f89e83b8…` | `63108b8ee31b87e9…` | `5362..5406`: `You searched for "PFN" No Airport Code found…` | Current issuing-body code directory observation captured 2026-11-18; proves PFN is withdrawn from IATA's active directory |
| `forensics-iata-lookup-rmu` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=RMU | `12ac00b428803ed3…` | `679473013eb7ae41…` | `15f0d847f82d56bc…` | `5362..5463`: `You searched for "RMU" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves RMU is assigned to Murcia Intl Region de Murcia |
| `forensics-iata-lookup-mjv` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=MJV | `2c52319ff99598c9…` | `b9ac9d26630c5b7f…` | `2460eb159b5b03b4…` | `5362..5406`: `You searched for "MJV" No Airport Code found…` | Current issuing-body code directory observation captured 2026-11-18; proves MJV (Murcia-San Javier) is withdrawn from IATA's active directory |
| `forensics-iata-lookup-aap` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=AAP | `9c62ca18bd686fe7…` | `adc67488da44116d…` | `71dfda90d0fff1ce…` | `5362..5466`: `You searched for "AAP" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves AAP is assigned to Samarinda AP Tumenggung Pranoto |
| `forensics-iata-lookup-sri` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=SRI | `7b912828127bbcac…` | `5d74630226263f22…` | `816494b88f063153…` | `5362..5496`: `You searched for "SRI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves SRI is no longer assigned to Samarinda Temindung (search only matches 'Sri' substring in airport names ATQ and PUT) |
| `forensics-iata-lookup-nmi` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=NMI | `d245a8a4fc27a63b…` | `478bab048bd9ab92…` | `64cd642d5cc8564e…` | `5362..5467`: `You searched for "NMI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns NMI to Navi Mumbai International (formal airportId apt_5e325674-a832-4106-807e-7e1e1ef951fe) |
| `forensics-iata-lookup-ayj` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=AYJ | `335c562e8b96e8b3…` | `1337f8a050b4dde0…` | `17b467c2303bda60…` | `5362..5458`: `You searched for "AYJ" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns AYJ to Ayodhya Airport (formal airportId apt_96e253c6-48ee-4ca3-b9a1-c34b49df0a68) |
| `forensics-iata-lookup-rqy` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=RQY | `0292da9cfb10cea7…` | `740382fc31dd9d77…` | `7fe9fc915aa22bcd…` | `5362..5464`: `You searched for "RQY" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns RQY to Shivamogga Airport (formal airportId apt_1130a628-5e21-4e68-b3e0-178487751f67) |
| `forensics-iata-lookup-sag` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=SAG | `71bd98148c91c61c…` | `2d47222386229885…` | `595f18e969d73c48…` | `5362..5456`: `You searched for "SAG" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns SAG to Shirdi Airport (formal airportId apt_59887ec2-9f97-4c36-a9cc-d7fb8dc9394f) |
| `forensics-iata-lookup-sdw` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=SDW | `666cd12b91305a94…` | `c338f4d03d04b533…` | `5d24ff1210900753…` | `5362..5452`: `You searched for "SDW" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns SDW to Sindhudurg (formal airportId apt_d5a97eb3-84c6-4fb2-910c-563f94f01d83) |
| `forensics-iata-lookup-hgi` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=HGI | `843e571abfeddd78…` | `a0f08998f9f4ff53…` | `13e790fb51a4cdd3…` | `5362..5452`: `You searched for "HGI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns HGI to Itanagar Hollongi / Donyi Polo Airport (formal airportId apt_c0bf8cd9-edd8-4b02-b8b8-1ff20705fd27) |
| `forensics-iata-lookup-cnn` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=CNN | `311571b5103bd624…` | `170c33728f4f1c75…` | `adf492018f25851c…` | `5362..5454`: `You searched for "CNN" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns CNN to Kannur International Airport (formal airportId apt_0548fd99-c0f2-4ced-b44c-c02e0ef8f2fd) |
| `forensics-iata-lookup-gbi` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=GBI | `19fc903bd20d971d…` | `7e74557192798738…` | `0248395eea5df607…` | `5362..5454`: `You searched for "GBI" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns GBI to Kalaburagi Airport (formal airportId apt_fb82d2f0-322c-414b-9c83-2d49dc6f7958) |
| `forensics-iata-lookup-kbk` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=KBK | `ba502e048408605f…` | `4deab5f3ac978979…` | `b915443c533e05fc…` | `5362..5470`: `You searched for "KBK" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns KBK to Kushinagar International Airport (formal airportId apt_74a774b7-2c51-4e7b-9b56-68c4d97e2f4b) |
| `forensics-iata-lookup-pyg` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=PYG | `ed83b764703a6fdb…` | `3a30e186ecd82070…` | `8fbacd3dcbac43dd…` | `5362..5450`: `You searched for "PYG" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns PYG to Pakyong Airport (formal airportId apt_b46610c5-1d06-44be-9a50-5bfceaa69ef0) |
| `forensics-iata-lookup-kjb` | International Air Transport Association (IATA) (`IATA-OFFICIAL-CODE-SEARCH`) | https://www.iata.org/en/publications/directories/code-search/?airport.search=KJB | `a9d1a7129434dcf7…` | `7b381bf1f7fce979…` | `2790a7ea9707f258…` | `5362..5458`: `You searched for "KJB" City Name Airport Name 3-…` | Current issuing-body code directory observation captured 2026-11-18; proves IATA assigns KJB to Kurnool Airport (formal airportId apt_1f12d4b0-2c3a-4b4e-9558-59e78102b83e) |

> **完整 64 位 SHA-256 与逐条 `quoteSha256`**：请直接查阅 [source-lock.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/source-lock.json) 与 [reused-evidence.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/reused-evidence.json)。

### 2. 重点案例 A：Palm Beach International Airport（`PBI → DJT` / `KPBI → KDJT`）深度取证

1. **跨批次物理机场 UUID 冲突重大发现与消解**：
   - 在审查现有资产时发现：同一物理机场（West Palm Beach，`ourAirports: "3766"`，FAA Site `03555.*A`）在 `global-code-expansion` / `global-code-next` 中被分配了候选 ID `apt_eb176a20-e0e3-438d-a330-a7b81185232d`，而在 `global-public-data/proposed-data.json`（`public-faa-03555-icao`）中却生成了另一个候选 ID `apt_f12cc00a-7d95-478e-bc87-a67c836379a3`。
   - **全库排查结果**：对 `global-public-data` 的 2,502 座候选机场与 `global-code-next`、`global-batch-5`、`priority-market-batch-6` 进行交叉比对后确认，**`ourAirports=3766` 是全库唯一存在跨批次 UUID 分裂的物理机场**。
   - **对生产解析器的致命影响**：`src/resolve.ts` 第 112–119 行要求同一查询日期下所有候选分配必须指向同一个 `airportId`（`result.candidates.every(c => c.airport.airportId === first.airport.airportId)`），否则即便存在 `certain` 区间也会降级为 `uncertain`；同时 `src/validate.ts` 第 37–42 行会因重复 `ourAirports: "3766"` 直接报错。将该机场统一归并至 `apt_eb176a20-e0e3-438d-a330-a7b81185232d` 后，`validateDataset()` 零错误通过，且 `KDJT` 在 `[2026-10-02, 2026-10-28)` 的 **26 个完整本地日期全部恢复为 `resolved`**。
2. **IATA 与 ICAO 分离取证结论**：
   - **IATA (`PBI → DJT`)**：
     - **发行机构 `iata.org` 原始证据**：`forensics-iata-lookup-djt`（原始 SHA-256: `70dca7ffe7300e641b39dbbfc8cd85bbeef0dcbe599a4fa75a9761109e8f527a`，字符位置 `5370..5496`）确认 `West Palm Beach | President Donald J. Trump International | DJT`。`forensics-iata-lookup-pbi`（原始 SHA-256: `a3f490e5b7416f2574586ad0e5d88931285312818e6c7d6fea55543bba896b6c`，字符位置 `5370..5473`）揭示 **IATA 并未彻底注销 `PBI`，而是将 `PBI` 保留为西棕榈滩城市/大都会区代码（`West Palm Beach | Metropolitan Area | PBI`）**，将单体机场代码切换为 `DJT`。
     - **运营商切换当日（`2026-08-18`）一手公告**：通过抓取 `flydjt.org/articles/`（`forensics-us-flydjt-articles-index`），发现并获取了此前批次未收录的 `2026-08-18` 当日官方新闻稿 `forensics-us-flydjt-iata-article`（原始 SHA-256: `d806933e3866b7e8859a95ff21ba0931bd84a0757ddce8a975f1b9c405f85a0d`，字符位置 `1966..2126`）：`West Palm Beach, FL (Aug. 18, 2026) – The airport code for President Donald J. Trump International Airport has officially changed from PBI to DJT, effective today.`
     - **州法律不改码一手反证（`2026-03-31`）**：`forensics-us-flydjt-rename-announcement`（原始 SHA-256: `79d7c2268b13af50c8b50c6820fb443c6cf3a4f7e7ad64ab42ffdc6c196a7b6a`，字符位置 `2493..2582`）明确指出：`The law takes effect July 1, 2026. The legislation does not change the airport’s code, PBI.` 证明 `2026-03-30` 签署日与 `2026-07-01` 州法生效日均不是代码生效日。
     - **独立航空公司（Air Canada）订座与行李系统切换证据（`2026-07-31`）**：`forensics-ca-aircanada-djt-notice`（原始 SHA-256: `d06a5e2f6024f768a907031dc747ca40e606b2bde35b1037bcff8be957acd7e6`，字符位置 `2923..3121`）明确指令旅客与系统：`Until August 18, continue to use the airport code PBI when searching for flights, checking baggage information or viewing airline schedules. Starting August 18, you’ll need to use the new airport code, DJT.` 打破了此前仅有郡机场管理局单一来源家族的局限。
   - **ICAO (`KPBI → KDJT`)**：
     - 复用已锁定的一手联邦文件 `next-us-faa-notice8900780`（`N 8900.780`）、`next-us-faa-info26011-official`（`InFO 26011`）、`next-us-nws-kdjt-implementation`（`SCN 26-56`）及郡机场管理局 `2026-07-09` 执行报告 `next-us-pbi-actual-name-change`，确认 ICAO `KPBI → KDJT` 变化日为 `2026-07-09`（早于 IATA 变化日 40 天）。
     - 结合已锁定的两期 FAA NASR `APT_BASE.csv`（`2026-10-01` 与 `2026-10-29`），在消解 UUID 冲突后确认 `KDJT` 的受控有界区间 `[2026-10-02, 2026-10-28)`（26 个完整本地日）。

### 3. 重点案例 B：Manas International Airport（`FRU → BSZ` / `UCFM`）深度取证

1. **发行机构 `iata.org` 原站核验（解决 AKI 第三方镜像顾虑）**：
   - `forensics-iata-lookup-bsz`（原始 SHA-256: `abc63e2c8a2ff63de561239c7a90a89fdb21416b91750ad67456aeb255f05d36`，字符位置 `5370..5458`）在 `iata.org` 原站直接证实 `Bishkek | Manas Intl | BSZ`。
   - `forensics-iata-lookup-fru`（原始 SHA-256: `f29162bdebfc5cd2196d3b2f0c6ffa3758adf4f3f715175907f294458ff3de1b`，字符位置 `5370..5416`）在 `iata.org` 原站直接证实 `You searched for "FRU" No Airport Code found`（`FRU` 已从现行目录撤销）。
2. **`2025-08-09` 与 `2025-08-11` 日期差异的法理与实务查明**：
   - 新获取的乌拉尔航空官方通知 `forensics-ru-uralairlines-bsz`（原始 SHA-256: `048acbfd5157bb8397217213957e855decc1a5586900c89f2f4887f5e705b97c`，发布日期 `8/11/2025`，字符位置 `366..687`）明确记载：
     > `The "Manas" Airport in Bishkek has changed its IATA code from FRU to BSZ. The decision was made in accordance with the provisions of IATA Resolution 763, which regulates the procedure for changing codes in the international system. The code change will take effect after a 90-day period from the date of receipt of the official notification from IATA, sent on May 9, 2025.`
   - **法理与日历还原**：依据 **IATA Resolution 763**，代码变更自 `2025-05-09` 正式通知发出满 3 个月/90 天公告期后于 **`2025-08-09`（周六）** 生效（与 AKI 镜像的 `2025-05-09` 通知正文 `will become effective on the 9th of August, 2025` 及运营商 `airport.kg/ru/news/15` 的 `с 9 августа 2025 года` 完全一致）；而 **`2025-08-11`（周一）** 是周六生效后的第一个工作日，航司货运/客运公告（如乌拉尔航空 `8/11/2025`）及媒体对 NOTAM/系统切换的回顾报道均在该周一发布。
3. **NOTAM `A0134/25` 与 `A0140/25` 核查状态**：
   - 检索确认 `UCFM` 的 `NOTAM A0134/25` 系通告玛纳斯机场 IATA 代码由 `FRU` 变更为 `BSZ` 的航行通告，而 `A0140/25` 为随后的同序列 2025 年 `UCFM` 航行通告。但由于吉尔吉斯斯坦空中航行服务机构（`kan.kg`）与民航局（`caa.kg`）未公开免认证的历史 NOTAM 原始电文库（`Q)`/`A)`/`B)`/`C)`/`E)` 全文），在未取得 `A0134/25` 与 `A0140/25` 原始电文前，不能武断判定 `A0140/25` 是否对生效时刻做了修正。
   - 因此，遵循第 4B 节与第 6 节严苛标准：在候选提案中将 `proposal-manas-iata-fru` 的 `validTo` 与 `proposal-manas-iata-bsz` 的 `validFrom` 保守表示为跨度区间 `{"earliest": "2025-08-09", "latest": "2025-08-12", "precision": "unknown"}`（完整涵盖 8 月 9 日至 8 月 11 日三天），保留 `pending` 状态，且**绝不据此推导 ICAO 代码 `UCFM` 的有效期**。

---

## D. 候选数据提案与 Owner 审批材料（Formal Data Proposals & Pending Package）

- **正式库状态**：由于当前没有针对美国、吉尔吉斯斯坦或印度 IATA 的自动准入授权，**本轮对 `data/airports.json` 保持零修改**。
- **结构化候选提案（[candidate-proposals.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/candidate-proposals.json)）**：
  - 包含 **4 座待准入物理机场**（归并后的西棕榈滩 `apt_eb176a20-e0e3-438d-a330-a7b81185232d`、玛纳斯 `apt_82a9b73d-530e-4f4a-9456-7f53c88246bc`、班加罗尔旧场 HAL `apt_ab3830d2-4506-46d5-8ff9-c2d5f46ce268`、班加罗尔新场 Kempegowda `apt_bf9260e8-2d9b-413b-81d9-c6842d53cbf7`）并直接复用 `data/airports.json` 中已有的 **13 座正式物理机场**（11 座印度机场 + 美国 `KECP` + 西班牙 `RMU`）。
  - 包含 **22 条 Schema `3.0.0` 候选分配（19 条 IATA + 3 条 ICAO）** 与 **38 条候选来源**，全部标记为 `verificationStatus: "pending"`、`verifiedOn: null`。
- **Owner 审批包（[owner-approval-packet.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/owner-approval-packet.json)）**：
  - 汇总了三项具体决策建议：（1）统一 `ourAirports: 3766` 的物理机场 UUID 为 `apt_eb176a20-e0e3-438d-a330-a7b81185232d`；（2）通过人工审查路径审核西棕榈滩 5 条记录与班加罗尔 `BLR` 2 条记录；（3）将玛纳斯 `FRU`/`BSZ` 及 13 条无日期边界的 `iata.org` 身份观察继续保留为 `pending`。

---

## E. 生产解析器 `resolveAirport()` 覆盖率差分报告（Production Resolver Differential）

我们使用未修改的生产解析器 `src/resolve.ts::resolveAirport()` 与验证器 `src/validate.ts::validateDataset()` 对全部 22 条候选分配进行了实测，完整输出保存在 [resolver-diff.json](file:///c:/Users/forgo/Documents/airport-history/research/evidence/global-iata-forensics/resolver-diff.json)。

### 1. 为什么「仅有单一代码变化日期、外侧边界为 `null`」的候选记录产生 0 个 `resolved` 查询？

在 `src/time.ts` 第 11–26 行与 `src/resolve.ts` 第 56–60 行中：
- `bounds({earliest: null, latest: null})` 返回 `[-Infinity, Infinity]`。
- `interval(assignment)` 定义 `possible = [startMin, endMax]`，`certain = [startMax, endMin]`（即 `[validFrom.latest, validTo.earliest]`）。
- 当 `validFrom.latest === null`（左边界未知，`startMax = Infinity`）或 `validTo.earliest === null`（右边界未知，`endMin = -Infinity`）时，`certain` 区间数学上为空集（`certain[0] > certain[1]`），因此任何落在 `possible` 范围内的查询日期其 `temporalMatch` 均为 `"possible"` 而非 `"certain"`，生产 `resolveAirport()` 严格返回 `status: "uncertain"`。
- **如实报告结论**：单边界切换记录（如 `proposal-pbi-iata-pbi`、`proposal-pbi-iata-djt`、`proposal-pbi-icao-kpbi`、`proposal-pbi-icao-kdjt`、`proposal-manas-iata-fru`、`proposal-manas-iata-bsz`、`b5-proposal-hal-iata-blr`、`b5-proposal-kempegowda-iata-blr`）以及双端未知的目录观察记录（13 条正式机场 IATA 绑定）在各自单独验证时，**产生的 `not_found → resolved` 新增查询数严格为 0**，其实际效果是将有效半平面内的查询从 `not_found` 提升为携有完整候选机场与证据链的 `uncertain`（`not_found → uncertain`）。唯有当左右两端均具备受控日期边界（如 `proposal-pbi-icao-kdjt-nasr-20261002-20261028` 的 `[2026-10-02, 2026-10-28)`）时，才产生 **26 个真实的 `not_found → resolved` 本地日期**。

### 2. 场景级差分汇总表（分开报告 Pending、仅 IATA、仅 ICAO、UUID 冲突未消解演示、IATA+ICAO 合并）

| 场景 ID | 包含分配数（IATA / ICAO） | `validateDataset` 错误数 | 新增 `not_found → resolved` 天数 | 4 探针点 `not_found → resolved` | 4 探针点 `not_found → uncertain` | 原有正式 `resolved` 结果是否 100% 保持 | 跨机场同码冲突数 (`conflict`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pendingModeVerification`（全量 22 条保持 `pending`） | 22 (19 / 3) | **0** | **0** | 0 | 0 | **是（0 破坏）** | **0** |
| `scenario-1-iata-only-verified` | 19 (19 / 0) | **0** | **0** | 0 | 72 | **是（0 破坏）** | **0** |
| `scenario-2-icao-only-verified-reconciled-uuid` | 3 (0 / 3) | **0** | **26** | 2 | 8 | **是（0 破坏）** | **0** |
| `scenario-3-icao-unreconciled-uuid-collision-demo` | 3 (0 / 3) | **1** | **0** | 0 | 10 | **是（0 破坏）** | **0** |
| `scenario-4-combined-iata-and-icao-verified-reconciled` | 22 (19 / 3) | **0** | **26** | 2 | 80 | **是（0 破坏）** | **0** |

> **关键验证对比**：在 `scenario-3-icao-unreconciled-uuid-collision-demo` 中，若不消解 `apt_eb176a20-e0e3-438d-a330-a7b81185232d` 与 `apt_f12cc00a-7d95-478e-bc87-a67c836379a3` 的跨批次 UUID 分裂，`validateDataset()` 直接报错 `Duplicate OurAirports identity: 3766`，且 `KDJT` 在 `[2026-10-02, 2026-10-28)` 的 **26 个 `resolved` 日期全部退化为 0（降级为 `uncertain`）**；而在归并 UUID 后的 `scenario-2` 与 `scenario-4` 中，26 个 `resolved` 日期全部完好保留且零冲突。

### 3. 逐条候选分配四探针点（区间开始前一天、开始日、结束前一天、结束日）实测表

| `assignmentId` | 体系:代码 | 物理机场 `airportId` | 开始前一天 (`dayBeforeStart`) | 开始日 (`startDay`) | 结束前一天 (`dayBeforeEnd`) | 结束日 (`endDay`) | 新增 `not_found → resolved` 总天数 | 冲突数 |
| --- | :---: | --- | --- | --- | --- | --- | :---: | :---: |
| `proposal-pbi-iata-pbi` | `IATA:PBI` | `apt_eb176a20-e0e3-438d-a330-a7b81185232d` | `2000-01-01`: `not_found -> uncertain` | `2026-08-17`: `not_found -> uncertain` | `2026-08-18`: `not_found -> uncertain` | `2026-08-19`: `not_found -> not_found` | **0** | 0 |
| `proposal-pbi-iata-djt` | `IATA:DJT` | `apt_eb176a20-e0e3-438d-a330-a7b81185232d` | `2026-08-17`: `not_found -> not_found` | `2026-08-18`: `not_found -> uncertain` | `2026-08-19`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-pbi-icao-kpbi` | `ICAO:KPBI` | `apt_eb176a20-e0e3-438d-a330-a7b81185232d` | `2000-01-01`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-07-09`: `not_found -> uncertain` | `2026-07-10`: `not_found -> not_found` | **0** | 0 |
| `proposal-pbi-icao-kdjt` | `ICAO:KDJT` | `apt_eb176a20-e0e3-438d-a330-a7b81185232d` | `2026-07-08`: `not_found -> not_found` | `2026-07-09`: `not_found -> uncertain` | `2026-07-10`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-pbi-icao-kdjt-nasr-20261002-20261028` | `ICAO:KDJT` | `apt_eb176a20-e0e3-438d-a330-a7b81185232d` | `2026-09-30`: `not_found -> not_found` | `2026-10-02`: `not_found -> resolved` | `2026-10-27`: `not_found -> resolved` | `2026-10-28`: `not_found -> uncertain` | **26** | 0 |
| `proposal-manas-iata-fru` | `IATA:FRU` | `apt_82a9b73d-530e-4f4a-9456-7f53c88246bc` | `2000-01-01`: `not_found -> uncertain` | `2025-08-08`: `not_found -> uncertain` | `2025-08-09`: `not_found -> uncertain` | `2025-08-12`: `not_found -> not_found` | **0** | 0 |
| `proposal-manas-iata-bsz` | `IATA:BSZ` | `apt_82a9b73d-530e-4f4a-9456-7f53c88246bc` | `2025-08-08`: `not_found -> not_found` | `2025-08-09`: `not_found -> uncertain` | `2025-08-12`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `b5-proposal-hal-iata-blr` | `IATA:BLR` | `apt_ab3830d2-4506-46d5-8ff9-c2d5f46ce268` | `2000-01-01`: `not_found -> uncertain` | `2008-05-23`: `not_found -> uncertain` | `2008-05-24`: `not_found -> uncertain` | `2008-05-25`: `not_found -> not_found` | **0** | 0 |
| `b5-proposal-kempegowda-iata-blr` | `IATA:BLR` | `apt_bf9260e8-2d9b-413b-81d9-c6842d53cbf7` | `2008-05-23`: `not_found -> not_found` | `2008-05-24`: `not_found -> uncertain` | `2008-05-25`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vanm-iata-nmi` | `IATA:NMI` | `apt_5e325674-a832-4106-807e-7e1e1ef951fe` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-veay-iata-ayj` | `IATA:AYJ` | `apt_96e253c6-48ee-4ca3-b9a1-c34b49df0a68` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vosh-iata-rqy` | `IATA:RQY` | `apt_1130a628-5e21-4e68-b3e0-178487751f67` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vasd-iata-sag` | `IATA:SAG` | `apt_fa1bf7a7-a97d-4676-9c9a-7871eda47767` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vokn-iata-cnn` | `IATA:CNN` | `apt_58a2554f-6a9b-4ad7-bc2c-2550ad21b962` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-veho-iata-hgi` | `IATA:HGI` | `apt_9acf6a6b-6e22-48c6-881c-d602429a9268` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vosr-iata-sdw` | `IATA:SDW` | `apt_9e24d5d7-5e1a-4489-b936-2737c438921e` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vogb-iata-gbi` | `IATA:GBI` | `apt_66034969-b902-4ede-8011-cc87a23070b7` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-veki-iata-kbk` | `IATA:KBK` | `apt_0342f79b-a035-43b6-88bf-52b9a5e9622f` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-vepy-iata-pyg` | `IATA:PYG` | `apt_162c7dfd-e70b-48c7-bbe5-282ede0a5cc9` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-voku-iata-kjb` | `IATA:KJB` | `apt_5d260013-75b3-4ec4-8915-7c5ff2a47fc3` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-kecp-iata-ecp` | `IATA:ECP` | `apt_74a05fd5-53fa-40f8-a3a6-de8cfd7d5e99` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |
| `proposal-in-lemi-iata-rmu` | `IATA:RMU` | `apt_f50aecf6-9778-4db7-9027-0e751ffab63a` | `2026-06-11`: `not_found -> uncertain` | `2026-06-12`: `not_found -> uncertain` | `2026-07-08`: `not_found -> uncertain` | `2026-11-18`: `not_found -> uncertain` | **0** | 0 |

### 4. 玛纳斯（`FRU → BSZ`）三种边界精度变体的解析器敏感性实测

| 变体方案 | 边界定义 | `2025-08-08` (`FRU` / `BSZ`) | `2025-08-09` (`FRU` / `BSZ`) | `2025-08-10` (`FRU` / `BSZ`) | `2025-08-11` (`FRU` / `BSZ`) | `2025-08-12` (`FRU` / `BSZ`) | 新增 `resolved` 天数 |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `multiDay_20250809_20250812` | `[2025-08-09, 2025-08-12)` (`unknown`) | `uncertain` / `not_found` | `uncertain` / `uncertain` | `uncertain` / `uncertain` | `uncertain` / `uncertain` | `not_found` / `uncertain` | **0** |
| `resolution763Day_20250809_20250810` | `[2025-08-09, 2025-08-10)` (`day`) | `uncertain` / `not_found` | `uncertain` / `uncertain` | `not_found` / `uncertain` | `not_found` / `uncertain` | `not_found` / `uncertain` | **0** |
| `operationalReportDay_20250811_20250812` | `[2025-08-11, 2025-08-12)` (`day`) | `uncertain` / `not_found` | `uncertain` / `not_found` | `uncertain` / `not_found` | `uncertain` / `uncertain` | `not_found` / `uncertain` | **0** |

---

## F. 每个案例剩余的具体问题与下一步取证动作（Unresolved Questions & Next Actions）

| 案例 | 剩余具体证据缺口 | 下一步精确取证动作 |
| --- | --- | --- |
| **1. 西棕榈滩 (`PBI → DJT` / `KPBI → KDJT`)** | （1）缺少向航司/GDS 分发的 IATA Special Industry Notification 原始通知 PDF；（2）`PBI` 与 `KPBI` 的历史首次分配边界（`validFrom`）仍为 `unknown`。 | （1）在 Owner 审批 `global-code-next` 与 `global-public-data` 时执行 `apt_eb176a20-e0e3-438d-a330-a7b81185232d` UUID 归一；（2）查找公开监管备案中的 IATA `PBI → DJT` 原始通告及早期 FAA NFDC/NASR 历史版本以收紧 `PBI`/`KPBI` 左边界。 |
| **2. 玛纳斯 (`FRU → BSZ` / `UCFM`)** | （1）尚未取得吉尔吉斯斯坦 `kan.kg` / `caa.kg` 发布的 `UCFM` NOTAM `A0134/25` 与 `A0140/25` 原始电文（`Q)/A)/B)/C)/E)` 全文）；（2）尚未确认 `A0140/25` 是否修正了 `A0134/25` 的具体生效时刻。 | 获取吉尔吉斯斯坦航空航行服务机构（Kyrgyzaeronavigatsia）eAIP 修订/AIC 或 `A0134/25`、`A0140/25` 原始 NOTAM 报文，核实后将 `[2025-08-09, 2025-08-12)` 收敛为精确单日边界。 |
| **3. 班加罗尔 (`BLR` HAL → Kempegowda)** | `2008-05-24` 转移边界已由印度官方宪报 `S.O. 1170(E)` 与 `S.O. 1181(E)` 证明，但旧场 `validFrom` 与新场 `validTo` 的有界连续区间缺少带日期的 IATA 官方目录序列（AAI eAIP 不含 IATA 代码）。 | 等待 Owner 审批 `global-code-next` 边界批次以正式准入 `2008-05-24` 转移边界；后续寻找 MoCA/DGCA 带日期的航班时刻表或公报附件以建立有界区间。 |
| **4. 正式库内 13 座缺 IATA 分配机场（11 座印度机场 + `ECP` + `RMU`）** | `iata.org` 现行目录查询已证明当前代码绑定，但不含历史生效日期，且 AAI 授权仅限印度 ICAO。 | 获取印度 DGCA/MoCA 针对 `NMI`、`AYJ`、`RQY`、`SAG`、`CNN`、`HGI`、`SDW`、`GBI`、`KBK`、`PYG`、`KJB` 的带日期公报/航线批复，以及美国 DOT/FAA 对 `ECP`（2010）、西班牙 ENAIRE 对 `RMU`（2019）的带日期代码文件。 |
| **5. 柬埔寨 (`PNH` / `KTI` / Kratie)** | `iata.org` 已证明 `PNH` 被撤销且 `KTI` 已唯一归属金边德崇机场，但缺少桔井机场（`VDBG`）失去 `KTI` 的精确历史日期文件及 `PNH` 从 IATA 账本注销的精确日期文件。 | 获取柬埔寨 SSCA AIP Supplement / AIC 或 IATA 针对 `KTI` 重新分配与 `PNH` 注销的 Special Industry Notification。 |
| **6. 塞内加尔 (`DKR` / `DSS`) 与伊斯坦布尔 (`IST` / `ISL`)** | `iata.org` 已证实旧场至今保留 `DKR` 与 `ISL`；`DKR` 在 2017-12-07 之后的持续有效区间缺少带日期的官方连续性锚点，伊斯坦布尔新场 2018-10-29 至 2019-04-06 期间 `ISL` 的首次分配日仍缺一手公文。 | 获取 ASECNA AIP Senegal 历史修订及土耳其 DHMİ 2018/2019 AIRAC/AIC 原件。 |
| **7. 中国迁建 (`LYG`、`LZO`、`YBP`、`ENY`、`AKA`、`WUZ`) 与日本名古屋 (`NGO`/`NKM`)** | 现有民航局新闻稿与统计公报证明了物理转场日与城市机场运营，但未在转场条款中显式打印三字码交接时刻，且不在现有 7 对中国机场授权哈希范围内；名古屋/中部机场 FAQ 无日期。 | 获取中国民航局情报中心（`eaipchina.cn`）对应转场周期的 AIRAC AIP SUP/AIC 电报原件，以及日本国土交通省航空局（MLIT CAB）2005 年 2 月 AIRAC 原件。 |

