# Formal IATA TAO coverage

The evidence supports continuous IATA `TAO` coverage at Qingdao Liuting in
`[2000-01-01, 2021-08-12)`. The owner authorized both physical-site intervals
for the supported product dates. The existing Liuting `airportId` is
`apt_f470ecb5-c6dc-4516-a233-37302da2115b`.

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

The formal 0.13.0 dataset uses the existing permanent airport IDs for
Liuting and Jiaodong. The Liuting period ends at the local date boundary on 2021-08-12.
The Jiaodong period begins that day and is certain through 2026-11-18.
[Owner policy](../../admission/default-continuity-v1/policy.json) ·
[Original evidence packet](admission-proposal.json)

## Production resolver results

| Local date | Result |
| --- | --- |
| 2000-01-01 | Qingdao Liuting International Airport |
| 2021-08-11 | Qingdao Liuting International Airport |
| 2021-08-12 | Qingdao Jiaodong International Airport |
| 2026-11-18 | Qingdao Jiaodong International Airport |
| 2026-11-19 | Outside the supported range |

The production resolver resolves all 9,819 supported TAO dates. It identifies
Liuting on 7,894 dates and Jiaodong on 1,925 dates. Compared with frozen 0.12.0,
6,098 dates gain a resolved answer and all previous answers retain their physical
site. The audit directly replays every supported TAO date.
[TAO resolver audit](audit.json) · [Global coverage receipt](../../admissions/0.13.0/coverage.json)

```sh
node scripts/evidence/tao_boundary_audit.ts --check
```
