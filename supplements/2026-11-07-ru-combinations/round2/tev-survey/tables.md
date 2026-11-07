# Опрос Тевса: описательные таблицы

Единица — ответ анкеты; ID — строка Excel. Данные мая 2026. Каждая строка входит в одну ячейку точного набора оплат × типа VPN.
Нулевые ячейки показаны в основных таблицах; срезы режима и стажа показывают все наблюдавшиеся ячейки. Полные ID и маски — results.json.
Это не риск бана, рейтинг безопасности или причинный эффект. Тип/режим VPN мог измениться после бана; общий стаж не равен сроку связки.

| Срез | n | ban_history | no_problems | contradictory | other_problem | unknown |
|---|---:|---:|---:|---:|---:|---:|
| all | 93 | 31 | 50 | 4 | 7 | 1 |
| russia | 89 | 30 | 47 | 4 | 7 | 1 |
| other_geography | 4 | 1 | 3 | 0 | 0 | 0 |
| strict_one_unchanged_payment | 36 | 8 | 28 | 0 | 0 | 0 |
| strict_with_mode | 36 | 8 | 28 | 0 | 0 | 0 |
| excluded | 57 | 23 | 22 | 4 | 7 | 1 |

## ru_payment_x_type

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| free | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| free | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| free | Платный коммерческий | — | 4 | 1 | 2 | 0 | 1 | 0 | ban_history: 67; no_problems: 45,70; other_problem: 36 |
| free | Свой VPS / собственный сервер | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 50 |
| free | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| gift | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| gift | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| gift | Платный коммерческий | — | 7 | 4 | 1 | 2 | 0 | 0 | ban_history: 10,43,58,60; no_problems: 29; contradictory: 12,51 |
| gift | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| gift | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| other | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| other | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| other | Платный коммерческий | — | 3 | 0 | 3 | 0 | 0 | 0 | no_problems: 34,61,66 |
| other | Свой VPS / собственный сервер | — | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 46,63 |
| other | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + gift | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + gift | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + gift | Платный коммерческий | — | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 9,44 |
| own_named_foreign + gift | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + gift | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + other | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + other | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + other | Платный коммерческий | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 19 |
| own_named_foreign + other | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + other | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller | Платный коммерческий | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 24 |
| own_named_foreign + reseller | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller + gift | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller + gift | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller + gift | Платный коммерческий | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller + gift | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign + reseller + gift | (пропуск) | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 13 |
| own_named_foreign | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign | Платный коммерческий | — | 14 | 1 | 12 | 1 | 0 | 0 | ban_history: 87; no_problems: 4,8,16,22,26,30,31,47,49,76,80,90; contradictory: 77 |
| own_named_foreign | Свой VPS / собственный сервер | — | 5 | 0 | 4 | 0 | 1 | 0 | no_problems: 14,23,38,89; other_problem: 64 |
| own_named_foreign | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| partner | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| partner | Корпоративный | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | — | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 21,32 |
| partner | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| partner | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller + gift | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller + gift | Корпоративный | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 86 |
| reseller + gift | Платный коммерческий | — | 7 | 6 | 1 | 0 | 0 | 0 | ban_history: 39,40,48,52,56,93; no_problems: 74 |
| reseller + gift | Свой VPS / собственный сервер | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 6 |
| reseller + gift | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller | Бесплатный | — | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 69 |
| reseller | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller | Платный коммерческий | — | 14 | 6 | 6 | 0 | 2 | 0 | ban_history: 15,17,72,73,78,91; no_problems: 7,11,62,79,82,83; other_problem: 5,25 |
| reseller | Свой VPS / собственный сервер | — | 3 | 1 | 2 | 0 | 0 | 0 | ban_history: 84; no_problems: 27,59 |
| reseller | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_foreign_service | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_foreign_service | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_foreign_service | Платный коммерческий | — | 4 | 3 | 1 | 0 | 0 | 0 | ban_history: 3,85,88; no_problems: 71 |
| virtual_foreign_service | Свой VPS / собственный сервер | — | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 54 |
| virtual_foreign_service | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + gift | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + gift | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + gift | Платный коммерческий | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 33 |
| virtual_russian_service + gift | Свой VPS / собственный сервер | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 28 |
| virtual_russian_service + gift | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + partner | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + partner | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + partner | Платный коммерческий | — | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 41; no_problems: 20 |
| virtual_russian_service + partner | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + partner | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + reseller | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + reseller | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + reseller | Платный коммерческий | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 94 |
| virtual_russian_service + reseller | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + reseller | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Платный коммерческий | — | 1 | 0 | 0 | 1 | 0 | 0 | contradictory: 37 |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service + virtual_foreign_service + reseller + partner | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service | Платный коммерческий | — | 4 | 0 | 4 | 0 | 0 | 0 | no_problems: 2,55,57,81 |
| virtual_russian_service | Свой VPS / собственный сервер | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 42 |
| virtual_russian_service | (пропуск) | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| (не отмечено) | Бесплатный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| (не отмечено) | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| (не отмечено) | Платный коммерческий | — | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 35 |
| (не отмечено) | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| (не отмечено) | (пропуск) | — | 1 | 0 | 0 | 0 | 0 | 1 | unknown: 75 |

## strict_payment_x_type

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| gift | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| gift | Платный коммерческий | — | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 60; no_problems: 29 |
| gift | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| own_named_foreign | Платный коммерческий | — | 12 | 1 | 11 | 0 | 0 | 0 | ban_history: 87; no_problems: 8,16,22,26,30,31,47,49,76,80,90 |
| own_named_foreign | Свой VPS / собственный сервер | — | 4 | 0 | 4 | 0 | 0 | 0 | no_problems: 14,23,38,89 |
| partner | Корпоративный | — | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | — | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 21,32 |
| partner | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| reseller | Платный коммерческий | — | 9 | 3 | 6 | 0 | 0 | 0 | ban_history: 15,72,91; no_problems: 7,11,62,79,82,83 |
| reseller | Свой VPS / собственный сервер | — | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 84; no_problems: 59 |
| virtual_foreign_service | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_foreign_service | Платный коммерческий | — | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 85,88 |
| virtual_foreign_service | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service | Корпоративный | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| virtual_russian_service | Платный коммерческий | — | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 2,55 |
| virtual_russian_service | Свой VPS / собственный сервер | — | 0 | 0 | 0 | 0 | 0 | 0 | — |

## ru_by_mode

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| free | Платный коммерческий | Меняю страны и провайдеров | 4 | 1 | 2 | 0 | 1 | 0 | ban_history: 67; no_problems: 45,70; other_problem: 36 |
| free | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 50 |
| gift | Платный коммерческий | Меняю страны и провайдеров | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 10; no_problems: 29 |
| gift | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 5 | 3 | 0 | 2 | 0 | 0 | ban_history: 43,58,60; contradictory: 12,51 |
| other | Платный коммерческий | Меняю страны и провайдеров | 3 | 0 | 3 | 0 | 0 | 0 | no_problems: 34,61,66 |
| other | Свой VPS / собственный сервер | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 46 |
| other | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 63 |
| own_named_foreign + gift | Платный коммерческий | Меняю страны и провайдеров | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 44 |
| own_named_foreign + gift | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 9 |
| own_named_foreign + other | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 19 |
| own_named_foreign + reseller | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 24 |
| own_named_foreign + reseller + gift | (пропуск) | — | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 13 |
| own_named_foreign | Платный коммерческий | Меняю страны и провайдеров | 6 | 1 | 5 | 0 | 0 | 0 | ban_history: 87; no_problems: 8,16,22,47,76 |
| own_named_foreign | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 8 | 0 | 7 | 1 | 0 | 0 | no_problems: 4,26,30,31,49,80,90; contradictory: 77 |
| own_named_foreign | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 5 | 0 | 4 | 0 | 1 | 0 | no_problems: 14,23,38,89; other_problem: 64 |
| partner | Корпоративный | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 21 |
| partner | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 32 |
| reseller + gift | Корпоративный | Меняю страны и провайдеров | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 86 |
| reseller + gift | Платный коммерческий | Меняю страны и провайдеров | 4 | 4 | 0 | 0 | 0 | 0 | ban_history: 39,48,56,93 |
| reseller + gift | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 3 | 2 | 1 | 0 | 0 | 0 | ban_history: 40,52; no_problems: 74 |
| reseller + gift | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 6 |
| reseller | Бесплатный | Использую периодически | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 69 |
| reseller | Платный коммерческий | Использую периодически | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 91 |
| reseller | Платный коммерческий | Меняю страны и провайдеров | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 72; no_problems: 62 |
| reseller | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 11 | 4 | 5 | 0 | 2 | 0 | ban_history: 15,17,73,78; no_problems: 7,11,79,82,83; other_problem: 5,25 |
| reseller | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 3 | 1 | 2 | 0 | 0 | 0 | ban_history: 84; no_problems: 27,59 |
| virtual_foreign_service | Платный коммерческий | Меняю страны и провайдеров | 3 | 2 | 1 | 0 | 0 | 0 | ban_history: 85,88; no_problems: 71 |
| virtual_foreign_service | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 3 |
| virtual_foreign_service | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 54 |
| virtual_russian_service + gift | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 33 |
| virtual_russian_service + gift | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 28 |
| virtual_russian_service + partner | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 41; no_problems: 20 |
| virtual_russian_service + reseller | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 94 |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 0 | 0 | 1 | 0 | 0 | contradictory: 37 |
| virtual_russian_service | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 4 | 0 | 4 | 0 | 0 | 0 | no_problems: 2,55,57,81 |
| virtual_russian_service | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 42 |
| (не отмечено) | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 35 |
| (не отмечено) | (пропуск) | — | 1 | 0 | 0 | 0 | 0 | 1 | unknown: 75 |

## strict_by_mode

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| gift | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 29 |
| gift | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 60 |
| own_named_foreign | Платный коммерческий | Меняю страны и провайдеров | 6 | 1 | 5 | 0 | 0 | 0 | ban_history: 87; no_problems: 8,16,22,47,76 |
| own_named_foreign | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 6 | 0 | 6 | 0 | 0 | 0 | no_problems: 26,30,31,49,80,90 |
| own_named_foreign | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 4 | 0 | 4 | 0 | 0 | 0 | no_problems: 14,23,38,89 |
| partner | Корпоративный | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | Меняю страны и провайдеров | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 21 |
| partner | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 32 |
| reseller | Платный коммерческий | Использую периодически | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 91 |
| reseller | Платный коммерческий | Меняю страны и провайдеров | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 72; no_problems: 62 |
| reseller | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 6 | 1 | 5 | 0 | 0 | 0 | ban_history: 15; no_problems: 7,11,79,82,83 |
| reseller | Свой VPS / собственный сервер | Постоянно одна и та же страна, один провайдер | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 84; no_problems: 59 |
| virtual_foreign_service | Платный коммерческий | Меняю страны и провайдеров | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 85,88 |
| virtual_russian_service | Платный коммерческий | Постоянно одна и та же страна, один провайдер | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 2,55 |

## ru_by_tenure

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| free | Платный коммерческий | 1–6 месяцев | 2 | 0 | 1 | 0 | 1 | 0 | no_problems: 70; other_problem: 36 |
| free | Платный коммерческий | Меньше месяца | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 67; no_problems: 45 |
| free | Свой VPS / собственный сервер | Больше года | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 50 |
| gift | Платный коммерческий | 1–6 месяцев | 5 | 2 | 1 | 2 | 0 | 0 | ban_history: 43,60; no_problems: 29; contradictory: 12,51 |
| gift | Платный коммерческий | 6–12 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 58 |
| gift | Платный коммерческий | Меньше месяца | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 10 |
| other | Платный коммерческий | Больше года | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 34,61 |
| other | Платный коммерческий | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 66 |
| other | Свой VPS / собственный сервер | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 63 |
| other | Свой VPS / собственный сервер | Больше года | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 46 |
| own_named_foreign + gift | Платный коммерческий | 6–12 месяцев | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 9,44 |
| own_named_foreign + other | Платный коммерческий | 6–12 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 19 |
| own_named_foreign + reseller | Платный коммерческий | Больше года | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 24 |
| own_named_foreign + reseller + gift | (пропуск) | 1–6 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 13 |
| own_named_foreign | Платный коммерческий | 1–6 месяцев | 8 | 0 | 7 | 1 | 0 | 0 | no_problems: 8,22,30,49,76,80,90; contradictory: 77 |
| own_named_foreign | Платный коммерческий | 6–12 месяцев | 3 | 0 | 3 | 0 | 0 | 0 | no_problems: 4,16,31 |
| own_named_foreign | Платный коммерческий | Больше года | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 26 |
| own_named_foreign | Платный коммерческий | Меньше месяца | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 87; no_problems: 47 |
| own_named_foreign | Свой VPS / собственный сервер | 1–6 месяцев | 3 | 0 | 3 | 0 | 0 | 0 | no_problems: 14,23,38 |
| own_named_foreign | Свой VPS / собственный сервер | Меньше месяца | 2 | 0 | 1 | 0 | 1 | 0 | no_problems: 89; other_problem: 64 |
| partner | Корпоративный | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 21 |
| partner | Платный коммерческий | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 32 |
| reseller + gift | Корпоративный | 1–6 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 86 |
| reseller + gift | Платный коммерческий | 1–6 месяцев | 5 | 4 | 1 | 0 | 0 | 0 | ban_history: 40,48,52,56; no_problems: 74 |
| reseller + gift | Платный коммерческий | 6–12 месяцев | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 39,93 |
| reseller + gift | Свой VPS / собственный сервер | 6–12 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 6 |
| reseller | Бесплатный | Меньше месяца | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 69 |
| reseller | Платный коммерческий | 1–6 месяцев | 7 | 2 | 4 | 0 | 1 | 0 | ban_history: 78,91; no_problems: 7,11,62,83; other_problem: 25 |
| reseller | Платный коммерческий | 6–12 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 79 |
| reseller | Платный коммерческий | Больше года | 2 | 2 | 0 | 0 | 0 | 0 | ban_history: 17,73 |
| reseller | Платный коммерческий | Меньше месяца | 4 | 2 | 1 | 0 | 1 | 0 | ban_history: 15,72; no_problems: 82; other_problem: 5 |
| reseller | Свой VPS / собственный сервер | 1–6 месяцев | 3 | 1 | 2 | 0 | 0 | 0 | ban_history: 84; no_problems: 27,59 |
| virtual_foreign_service | Платный коммерческий | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 71 |
| virtual_foreign_service | Платный коммерческий | 6–12 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 85 |
| virtual_foreign_service | Платный коммерческий | Больше года | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 3 |
| virtual_foreign_service | Платный коммерческий | Меньше месяца | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 88 |
| virtual_foreign_service | Свой VPS / собственный сервер | Больше года | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 54 |
| virtual_russian_service + gift | Платный коммерческий | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 33 |
| virtual_russian_service + gift | Свой VPS / собственный сервер | 1–6 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 28 |
| virtual_russian_service + partner | Платный коммерческий | 6–12 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 20 |
| virtual_russian_service + partner | Платный коммерческий | Меньше месяца | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 41 |
| virtual_russian_service + reseller | Платный коммерческий | 6–12 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 94 |
| virtual_russian_service + virtual_foreign_service + reseller + partner | Платный коммерческий | Больше года | 1 | 0 | 0 | 1 | 0 | 0 | contradictory: 37 |
| virtual_russian_service | Платный коммерческий | 1–6 месяцев | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 2,57 |
| virtual_russian_service | Платный коммерческий | Меньше месяца | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 55,81 |
| virtual_russian_service | Свой VPS / собственный сервер | Больше года | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 42 |
| (не отмечено) | Платный коммерческий | 6–12 месяцев | 1 | 0 | 0 | 0 | 1 | 0 | other_problem: 35 |
| (не отмечено) | (пропуск) | 1–6 месяцев | 1 | 0 | 0 | 0 | 0 | 1 | unknown: 75 |

## strict_by_tenure

| Оплаты | Тип VPN | Срез | n | Бан | Без проблем | Противоречие | Иная проблема | Неизвестно | ID по исходам |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| gift | Платный коммерческий | 1–6 месяцев | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 60; no_problems: 29 |
| own_named_foreign | Платный коммерческий | 1–6 месяцев | 7 | 0 | 7 | 0 | 0 | 0 | no_problems: 8,22,30,49,76,80,90 |
| own_named_foreign | Платный коммерческий | 6–12 месяцев | 2 | 0 | 2 | 0 | 0 | 0 | no_problems: 16,31 |
| own_named_foreign | Платный коммерческий | Больше года | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 26 |
| own_named_foreign | Платный коммерческий | Меньше месяца | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 87; no_problems: 47 |
| own_named_foreign | Свой VPS / собственный сервер | 1–6 месяцев | 3 | 0 | 3 | 0 | 0 | 0 | no_problems: 14,23,38 |
| own_named_foreign | Свой VPS / собственный сервер | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 89 |
| partner | Корпоративный | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 68 |
| partner | Платный коммерческий | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 21 |
| partner | Платный коммерческий | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 32 |
| reseller | Платный коммерческий | 1–6 месяцев | 5 | 1 | 4 | 0 | 0 | 0 | ban_history: 91; no_problems: 7,11,62,83 |
| reseller | Платный коммерческий | 6–12 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 79 |
| reseller | Платный коммерческий | Меньше месяца | 3 | 2 | 1 | 0 | 0 | 0 | ban_history: 15,72; no_problems: 82 |
| reseller | Свой VPS / собственный сервер | 1–6 месяцев | 2 | 1 | 1 | 0 | 0 | 0 | ban_history: 84; no_problems: 59 |
| virtual_foreign_service | Платный коммерческий | 6–12 месяцев | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 85 |
| virtual_foreign_service | Платный коммерческий | Меньше месяца | 1 | 1 | 0 | 0 | 0 | 0 | ban_history: 88 |
| virtual_russian_service | Платный коммерческий | 1–6 месяцев | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 2 |
| virtual_russian_service | Платный коммерческий | Меньше месяца | 1 | 0 | 1 | 0 | 0 | 0 | no_problems: 55 |

## Проверки

Причины строгих исключений пересекаются:
- missing_vpn_type: 2; исходы {'ban_history': 1, 'no_problems': 0, 'contradictory': 0, 'other_problem': 0, 'unknown': 1}.
- not_exactly_one_defined_paid_method: 32; исходы {'ban_history': 15, 'no_problems': 13, 'contradictory': 1, 'other_problem': 2, 'unknown': 1}.
- not_russia: 4; исходы {'ban_history': 1, 'no_problems': 3, 'contradictory': 0, 'other_problem': 0, 'unknown': 0}.
- not_two_main_outcomes: 12; исходы {'ban_history': 0, 'no_problems': 0, 'contradictory': 4, 'other_problem': 7, 'unknown': 1}.
- payment_not_explicitly_unchanged: 31; исходы {'ban_history': 14, 'no_problems': 11, 'contradictory': 1, 'other_problem': 4, 'unknown': 1}.

Точные дубли всей исходной строки: [].
Сверка ChatGPT/апелляций (не меняет основной исход): {"ban_history_but_chat_says_no_ban": [], "no_problems_but_chat_event_answer": [4, 11, 55], "no_problems_but_chat_claude_not": [], "no_problems_but_appeal_submitted": []}.
«Другое» в событиях, без публикации текста: [36, 92].
