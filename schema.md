# Схема кейсов банов Claude

Один кейс — одна история одного аккаунта, рассказанная самим владельцем (или коллегой с подробностями). Файл — CSV в UTF-8, разделитель запятая, все текстовые поля в двойных кавычках. Имена и ники не записываем: только ссылку на пост.

Кодируем и забаненных, и тех, кто пишет «меня не тронули» с подробностями: без них нельзя сравнить, чем забаненные отличаются.

Если поле в истории не названо — `unknown`. Не додумываем: «оплачивал казахской картой» — это `own_card_foreign` + `KZ`, а «оплачивал как обычно» — `unknown`.

## Колонки (порядок строгий)

```
case_id,source,url,post_date,ban_date,wave,user_region,outcome,account_age_months,plan,payment_method,payment_country,access_ip,ip_stable,kyc,usage,automation,refund,appeal,new_account,notes
```

| Колонка | Значения |
|---|---|
| case_id | `<source>-<номер>`, например `reddit-017` |
| source | reddit, x, hn, github, habr, vcru, telegram, v2ex, linuxdo, zhihu, pikabu, dtf, 4pda, other |
| url | прямая ссылка на пост или комментарий, который ты открыл |
| post_date | ГГГГ-ММ-ДД |
| ban_date | ГГГГ-ММ-ДД, если названа или следует из поста («сегодня ночью»); иначе пусто |
| wave | метка волны, если бан совпал с известной массовой волной, например `2026-10-01`; иначе пусто |
| user_region | где физически находится пользователь: RU, CN, HK, IR, BY, UA, KZ, US, EU, other, unknown |
| outcome | banned (аккаунт отключён), locked (временная блокировка / on hold), survived (пережил волну, пишет об этом), kyc_prompt (попросили верификацию, бана нет), unbanned (вернули после апелляции или массово) |
| account_age_months | число месяцев от регистрации до бана; «аккаунт 2023 года» при бане в 10.2026 → 33; пусто, если неизвестно |
| plan | free, pro, max5, max20, team, enterprise, api, unknown |
| payment_method | own_card_foreign (своя карта зарубежного банка), own_card_local (карта банка страны, где живёт, если страна поддерживается), virtual_card (виртуальная карта сервиса), reseller (подписку оформил перекупщик / посредник / «по токену»), app_store (App Store / Google Play), gift, crypto, unknown |
| payment_country | страна банка карты: KZ, KG, GE, AM, US, TR, AE, EU, other, unknown |
| access_ip | home_native (домашний IP поддерживаемой страны без VPN), residential_vpn (резидентный прокси / домашний IP знакомых), commercial_vpn (общий платный VPN), datacenter_vps (свой VPN/прокси на VPS, хостинг, сервер в ДЦ), mobile, corporate, unknown |
| ip_stable | yes (всегда один IP / одна страна), no (менял страны, разные VPN на разных устройствах), unknown |
| kyc | passed (проходил верификацию личности), requested (просили, не прошёл / не стал), none, unknown |
| usage | heavy (выжигает лимиты, Max на полную, сутками агенты), normal, light, unknown |
| automation | claude_code, claude_p_headless (`claude -p`, скрипты, CI), third_party_harness (OpenCode, Cline и др. через подписку), api_proxy (проксирует подписку в API), multi_account (несколько аккаунтов, переключается), none, unknown; несколько значений — через `;` |
| refund | full, partial, none, pending, unknown |
| appeal | none, pending, rejected, accepted, unknown |
| new_account | что стало с новым аккаунтом после бана: none (не заводил), banned_fast (забанили за часы/дни), alive, kyc_required, unknown |
| notes | пересказ по-русски до 200 знаков: главное, что не влезло в поля (страна VPN, «только что оплатил», «забанили при смене карты»). Без имён |

## Правила

- Только истории от первого лица или с подробностями о конкретном аккаунте. Общие реплики «всех банят» — не кейс.
- Один человек с двумя аккаунтами — два кейса (у каждого свой исход).
- Дубликаты (тот же человек на двух площадках) — один кейс, вторую ссылку в notes.
- Дата поста обязательна: без неё нельзя привязать к волне.
