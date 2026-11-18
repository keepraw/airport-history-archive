# TAO at the 2000 cutoff

The evidence supports continuous IATA `TAO` coverage at Qingdao Liuting in
`[2000-01-01, 2021-08-12)`. The proposed latest start is the cutoff. The
original allocation date remains unknown. The existing Liuting `airportId`
is `apt_f470ecb5-c6dc-4516-a233-37302da2115b`.

- China Eastern's April–October 1991 timetable lists **Qingdao TAO** in the
  Hefei departure table. PDF page 3 establishes the effective period and
  printed page 16 shows the code. [China Eastern timetable](https://www.timetableimages.com/ttimages/mu/mu9104/mu9104.pdf)
- The 1997 China Northwest timetable corroborates Qingdao passenger service.
  Its Qingdao departure table records the city name. The physical-site evidence
  includes the chronology of Cangkou's return to military use and Liuting's
  continued operation across its 1999 status change and 2000 expansion.
  [China Northwest timetable](https://www.timetableimages.com/ttimages/wh/wh9703/wh9703.pdf)
  [Liuting and Cangkou chronology](https://news.bandao.cn/a/533446.html)
- The locked BTS Master Coordinate row `1512701` independently locates
  Liuting. Its `TAO` value is in USDOT's statistical namespace.
  [BTS source lock](../source-lock.json)
- ANA Cargo cites its 2016 TAO procedures. Documented IATA approval and the
  executed local-midnight transfer establish Jiaodong as the successor on
  2021-08-12. [ANA Cargo](https://www.anacargo.jp/en/news/210430_E.html)
  [IATA approval report](https://news.qingdaonews.com/qingdao/2019-03/22/content_20304508.htm)
  [Transfer report](https://www.xinhuanet.com/2021-08/12/c_1127752897.htm)

The prepared continuity record uses the existing airport identity and retains
the original formal assignments. The admission dossier carries the dated
primary observation, locator, source hashes and exact claim scope. It awaits
owner acceptance under the existing per-record admission gate.
[Pending admission](admission-proposal.json)

## Resolver measurement

| Outcome | Formal 0.12.0 in this PR | Pending TAO proposal replay |
| --- | ---: | ---: |
| TAO dates resolved to Liuting | 1,821 | 7,894 |
| TAO dates resolved to Jiaodong | 1,900 | 1,900 |
| TAO uncertain dates | 6,098 | 25 |
| TAO conflicts | 0 | 0 |
| Newly resolved TAO code/date queries versus the inherited formal data | **0** | **6,073** |

On 2000-01-01, formal TAO is still `uncertain`. On 2021-08-12 it resolves to
Jiaodong. The 25 dates beginning 2026-10-25 require a later evidence bound at
Jiaodong. The comparison ran the production resolver on all 451,674 supported
formal code/date combinations per dataset. It recorded 114,402 resolved queries
with zero gains, losses or identity changes versus the inherited formal data.
The replay counts distinct code/date queries. Flight records were unavailable.
[Resolver audit](audit.json)

```sh
node scripts/evidence/tao_boundary_audit.ts --check
```
