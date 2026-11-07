# Сравнение вариантов: описательная статистика

Числитель — banned; знаменатель — banned+active+survived. Остальные исходы и ID лежат в JSON. Доля среди рассказавших не является вероятностью бана.

| Срез | Сбор | Сравнение A/B | A: бан/известный исход | B: бан/известный исход | Разница, п.п. |
|---|---|---|---|---|---|
| recorded_RU | all | network | 10/23 | 9/16 | -12.8 |
| recorded_RU | all | plan | 28/30 | 11/17 | 28.6 |
| recorded_RU | all | payment | 10/22 | 15/22 | -22.7 |
| recorded_RU | all | usage | 6/8 | 11/19 | 17.1 |
| recorded_RU | all | stable | 11/27 | 8/20 | 0.7 |
| recorded_RU | all | appstore_vs_reseller | 1/4 | 15/22 | -43.2 |
| recorded_RU | all | virtual_vs_bank | 9/10 | 10/22 | 44.5 |
| recorded_RU | all | young_vs_old | 18/21 | 3/4 | 10.7 |
| recorded_RU | legacy | network | 10/22 | 9/16 | -10.8 |
| recorded_RU | legacy | plan | 27/28 | 11/16 | 27.7 |
| recorded_RU | legacy | payment | 10/22 | 15/21 | -26.0 |
| recorded_RU | legacy | usage | 6/8 | 11/19 | 17.1 |
| recorded_RU | legacy | stable | 11/27 | 8/20 | 0.7 |
| recorded_RU | legacy | appstore_vs_reseller | 1/4 | 15/21 | -46.4 |
| recorded_RU | legacy | virtual_vs_bank | 9/10 | 10/22 | 44.5 |
| recorded_RU | legacy | young_vs_old | 18/21 | 3/4 | 10.7 |
| recorded_RU | addition | network | 0/1 | 0/0 | нет |
| recorded_RU | addition | plan | 1/2 | 0/1 | 50.0 |
| recorded_RU | addition | payment | 0/0 | 0/1 | нет |
| recorded_RU | addition | usage | 0/0 | 0/0 | нет |
| recorded_RU | addition | stable | 0/0 | 0/0 | нет |
| recorded_RU | addition | appstore_vs_reseller | 0/0 | 0/1 | нет |
| recorded_RU | addition | virtual_vs_bank | 0/0 | 0/0 | нет |
| recorded_RU | addition | young_vs_old | 0/0 | 0/0 | нет |
| context_compatible | all | network | 34/67 | 15/25 | -9.3 |
| context_compatible | all | plan | 88/106 | 49/92 | 29.8 |
| context_compatible | all | payment | 32/49 | 23/31 | -8.9 |
| context_compatible | all | usage | 32/45 | 25/37 | 3.5 |
| context_compatible | all | stable | 29/65 | 25/53 | -2.6 |
| context_compatible | all | appstore_vs_reseller | 6/14 | 23/31 | -31.3 |
| context_compatible | all | virtual_vs_bank | 16/24 | 32/49 | 1.4 |
| context_compatible | all | young_vs_old | 33/39 | 17/23 | 10.7 |
| context_compatible | legacy | network | 27/55 | 13/23 | -7.4 |
| context_compatible | legacy | plan | 79/84 | 30/46 | 28.8 |
| context_compatible | legacy | payment | 31/47 | 19/25 | -10.0 |
| context_compatible | legacy | usage | 27/34 | 22/33 | 12.7 |
| context_compatible | legacy | stable | 26/60 | 21/40 | -9.2 |
| context_compatible | legacy | appstore_vs_reseller | 5/11 | 19/25 | -30.5 |
| context_compatible | legacy | virtual_vs_bank | 15/22 | 31/47 | 2.2 |
| context_compatible | legacy | young_vs_old | 33/39 | 15/19 | 5.7 |
| context_compatible | addition | network | 7/12 | 2/2 | -41.7 |
| context_compatible | addition | plan | 9/22 | 19/46 | -0.4 |
| context_compatible | addition | payment | 1/2 | 4/6 | -16.7 |
| context_compatible | addition | usage | 5/11 | 3/4 | -29.5 |
| context_compatible | addition | stable | 3/5 | 4/13 | 29.2 |
| context_compatible | addition | appstore_vs_reseller | 1/3 | 4/6 | -33.3 |
| context_compatible | addition | virtual_vs_bank | 1/2 | 1/2 | 0.0 |
| context_compatible | addition | young_vs_old | 0/0 | 2/4 | нет |
