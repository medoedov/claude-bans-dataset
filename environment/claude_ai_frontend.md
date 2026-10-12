# Что claude.ai знает о браузере: разбор фронтенда

Дата: 12.10.2026. Метод: браузер, страница https://claude.ai/login **без входа в аккаунт**. Скриптом в консоли страницы скачаны все JS-чанки приложения: начиная с загруженных страницей, по ссылкам на чанки внутри кода, с `https://assets-proxy.anthropic.com/claude-ai/v2/assets/v1/`. Получилось 2926 файлов, 116,6 МБ, это весь бандл приложения, включая код после входа. Сборка Datadog RUM `version: d40c622ef0`. По тексту чанков искались паттерны: WebRTC, часовой пояс, язык, canvas/WebGL/audio-отпечатки, антифрод-вендоры. Код минифицирован, имена функций ниже — из минифицированной сборки, они меняются от сборки к сборке.

Окружение браузера, в котором шла проверка: `navigator.languages = ["ru","en-US"]`, часовой пояс `Europe/Moscow`.

## Находки

| # | Что | Где в коде | Вывод |
|---|---|---|---|
| 1 | Каждое сообщение в чат уходит с полями `timezone` и `locale`: `Qv({prompt, parent_message_uuid, timezone: bt()?"UTC":R_(), locale: Fe.locale, model, ...})`; `R_()` = `Intl.DateTimeFormat().resolvedOptions().timeZone` с кэшем на 60 с | shared-1-DT-Mq-A-.js | Часовой пояс системы Anthropic получают с каждым сообщением. Условие, при котором вместо него уходит "UTC" (`bt()`), не расшифровано |
| 2 | `locale` в запросе — только из списка языков интерфейса, иначе `en-US`; список: en-US, de-DE, fr-FR, ko-KR, ja-JP, es-419, es-ES, it-IT, hi-IN, pt-BR, id-ID | shared-l-p-m-2-BqN7gGau.js (`V_`, `Y_`) | Русского в списке языков интерфейса этой сборки НЕТ (ru-RU встречается только в локалях компонента дат). Расходится со статьёй («6 октября появился русский язык интерфейса», источник metaratings) — проверить у автора в настройках |
| 3 | Datadog RUM: `sessionSampleRate: 100`, `trackingConsent: "granted"`, `service: claude-ai`, 11 запросов на `browser-intake-us5-datadoghq.com/api/v2/rum` уже со страницы входа. SDK кладёт в событие `device:{locale: navigator.language, locales: navigator.languages, time_zone}` | vendor-datadog-Cx_GiDCs.js; `DD_RUM.getInitConfiguration()` | Язык браузера (у нас `ru`) и часовой пояс уходят в мониторинг до входа в аккаунт, у 100% сессий. Это мониторинг производительности; использует ли его антифрод — из кода не видно |
| 4 | Собственная телеметрия страницы: `client_tz`, `client_utc_offset_min`, `device_memory_gb`, `hardware_concurrency`, тип сети, `max_touch_points`, userAgent, platform (+ high-entropy client hints, `platformVersion`) | shared-l-p-m-0-CbQFC6Wr.js (`qb`, `zb`, `Jb`, `Cx`) | Профиль устройства собирается в события загрузки страниц |
| 5 | Невидимая hCaptcha («client attestation»): сайт-ключи для оплаты (`claude_payments_hcaptcha_sitekey`), входа через Google, приглашения, вступления в организацию, удаления аккаунта. Токен `client_attestation` прикладывается к `/api/stripe/{org}/intent`, `/api/billing/stripe_region`, `/upgrade_to_max`, `/pro/switch_billing_interval`, `/setup_overage_billing`, `/api/auth/verify_phone_code`, `/api/auth/verify_magic_link`, `/api/account`. Ошибка `missing_client_attestation` → «Couldn’t verify your browser» | shared-l-p-m-0, shared-m-1-D72Z34ZU.js, shared-9-BzBpDFis.js, c8a1c88e2 | Браузер проверяют антибот-сервисом в двух точках: вход и оплата. Совпадает с наблюдением из статьи, что бан часто приходит сразу после оплаты |
| 6 | WebRTC: `RTCPeerConnection({iceServers: []})` только в голосовом режиме, транспорт `webrtc_media` за фича-флагом, иначе `socket_audio` | shared-15-CuxGJsr0.js, ccc68ce7f-BLSLMoit.js | Нет STUN-серверов → классическая «утечка WebRTC» (внешний IP через STUN) кодом claude.ai не выполняется. Других вызовов RTCPeerConnection в бандле нет |
| 7 | WebGL `UNMASKED_RENDERER_WEBGL` читается в 2 местах, результат — булево «программный рендер» (`swiftshader|llvmpipe|software`) | c6dd1f86a, c5f8d66e0 | Проверка, тянет ли устройство графику, а не хэш видеокарты |
| 8 | `toDataURL` в 13 местах — все про картинки (иконки, кроп, скетч, html-to-image, шум текстуры) | разные | Canvas-отпечатка нет |
| 9 | Не найдено: FingerprintJS, Arkose/FunCaptcha, Sift, Sardine, Persona, Segment, Cloudflare Turnstile, OfflineAudioContext, `navigator.webdriver` | — | Готовых библиотек отпечатка в бандле нет. Stripe.js (`js.stripe.com`) подключается для оплаты; что Stripe собирает сам — по документации Stripe: https://docs.stripe.com/disputes/prevention/advanced-fraud-detection |

| 10 | Cookies, видимые скрипту на странице входа (без входа в аккаунт; профиль браузера не чистый, сайт мог открываться в нем раньше): `anthropic-device-id`, `__ssid`, `activitySessionId`, `ajs_anonymous_id`, `_fbp`, `_dd_s_v2`, `g_state`; в localStorage `antalytics_anonymous_id` | `document.cookie`, `localStorage` | Постоянный ID устройства ставится до входа; по таблице cookies Anthropic `anthropic-device-id` и `__ssid` — категория Security: https://privacy.claude.com/en/articles/10023541-what-cookies-does-anthropic-use |

## Что из этого следует

- Рассинхрон окружения Anthropic видят и без отпечатка: часовой пояс уходит в каждом сообщении, язык браузера и часовой пояс — в мониторинг.
- Но видеть — не значит банить за это. Что из этого антифрод использует, код не показывает; ответ — только в исходах: results.md, разделы 1, 4 и 5.
- Утечки WebRTC через claude.ai нет в том виде, в каком её описывают продавцы антидетектов.
- Claude Code — CLI: браузерного отпечатка, Datadog RUM и hCaptcha у его запросов нет, браузер нужен только для OAuth-входа и оплаты. Трафик Claude Code не перехватывался, что он шлет о машине — по документации: https://code.claude.com/docs/en/data-usage.

## Ограничения

- Разобран фронтенд, а не сервер: что Anthropic делают с полученным, отсюда не видно.
- Сборка на 12.10.2026; часть кода за фича-флагами.
- Запросы не перехватывались, кроме списка URL ресурсов страницы входа (performance API); тела запросов Datadog не читались.
