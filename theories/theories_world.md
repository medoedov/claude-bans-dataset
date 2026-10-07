# Теория «банят за выжимание лимитов»: мировые площадки

Дата: 07.10.2026. Охват: 628 кейсов из reddit.csv, github.csv, hn.csv, x.csv, oct1_world.csv; 418 тредов, из которых они взяты (329 на Reddit, 50 issues на GitHub, 39 на HN).

## Метод

1. **Кейсы.** Текст каждого кейса заново скачан: пост или коммент и все реплики того же автора в треде. Reddit брался через Arctic Shift, GitHub через `gh issue view`, HN через Algolia, X из локальных fx_*.json. Для каждого кейса размечено два поля.
   - `theory`: yes — автор связывает свой бан с интенсивностью использования; rejected — упоминает эту версию и отвергает; no — тема не затронута.
   - `anth_usage_reason`: yes — автор пишет, что Anthropic в письме или поддержка прямо назвали причиной объём.
   Разметка лежит в scratchpad, в итоговый recode_world.csv эти поля не входят.
2. **Треды.** Скачаны все комментарии 418 тредов, всего 27 721 текст. Отобраны тексты, где одновременно встречается слово про объём (limits, power user, 24/7, overnight, parallel sessions, high volume и т. п.) и слово про бан. Таких нашлось 156, каждый прочитан вручную. Метки:
   - S — забаненный связывает свой бан со своим объёмом;
   - G — общее утверждение «банят тех, кто много использует»;
   - E — «банят за обход лимитов» (ротация аккаунтов, автопродолжение после сброса);
   - R — опровержение: выжимает лимиты, и бана нет;
   - N — забаненный подчёркивает, что лимиты не выжимал;
   - A — письмо Anthropic называет объём.
   Поиск идёт по словарю, поэтому формулировки без ключевых слов («было слишком много работы») могли не попасть. Значит, тредовые числа — нижняя граница.

## Итог в цифрах

**Кейсы (628).**
- theory = yes — 41 кейс в 37 тредах. Из них 32 размечены usage=heavy, 3 normal, 2 light, 4 unknown. 40 забанены, 1 разбанен.
- theory = rejected — 28 кейсов. Человек сам отводит версию с объёмом: «never hit the limits», «I've only used about 12% of my weekly limit».
- По сути 41 кейс с yes делятся на пять групп:

| Группа | Кейсов | Что говорят |
|---|---|---|
| Объём по собственной воле | 19 | «сжёг кредиты слишком быстро», «too active», «used it heavily», «выжимал недельный лимит» |
| Объём из-за бага или взлома | 7 | расширение VS Code или `--continue` жгло лимит в фоне, утёк ключ, лимит сгорал сам |
| Автоматизация | 7 | `claude -p` в конвейерах, GitHub Actions, ночные прогоны с плагином, параллельные CLI-сессии |
| Мультиаккаунт, обход лимитов, шеринг | 6 | 13 подписок Max 20x со скриптом балансировки, два Pro «из-за нехватки квоты», команда на одном аккаунте |
| Расплывчато | 2 | «multiple requests» в одном ряду с другими догадками |

Пять из 19 случаев «объёма по собственной воле» — один эпизод ноября 2025 года: промо с $1000 кредитов Claude Code web. Люди быстро тратили кредиты и получали бан (reddit-056, 057, 059, 060, 061).

**Треды (418).**
- Хотя бы одна реплика, связывающая бан с интенсивным использованием (S или G), есть в 29 тредах: 22 реплики S в 21 треде и 11 реплик G в 10 тредах.
- Вместе с тредами кейсов theory=yes набирается 53 треда из 418, то есть 13 %. Если добавить версию «за обход лимитов» (E, 5 реплик в 4 тредах), получится 55.
- Опровержения от самих тяжёлых пользователей (R) встречаются в 5 тредах. Реплик «я лимиты не выжимал, а меня всё равно забанили» (N) — 10 в 8 тредах, и это не считая 28 кейсов rejected.

**Как это выглядит в разметке usage_new.** Среди забаненных, у кого интенсивность известна (347 кейсов), heavy — 65 (19 %), normal — 185 (53 %), light — 97 (28 %). Среди переживших волну, которые пишут об этом (26 кейсов), heavy — 9. То есть люди, которые выжимают лимиты и не забанены, в выборке есть.

## Называли ли Anthropic объём причиной

Прямых случаев, где Anthropic назвали причиной именно объём использования, — 5 из 628. Все они нетипичные:

| Кейс | Что в письме, по словам автора | Оговорка |
|---|---|---|
| github-096 — https://github.com/anthropics/claude-code/issues/39492 | suspended for «high volume exchanges» | Объём, по словам автора, дало расширение VS Code, которое слало запросы в фоне |
| github-097 — https://github.com/anthropics/claude-code/issues/41046 | suspended due to «high volume exchanges» | То же: после обновления расширения лимит кончался за минуты |
| reddit-305 — https://www.reddit.com/r/Anthropic/comments/1vbf3w9/ | «detected a high volume of requests from my account» | Бан в секунду оплаты Team, аккаунтом ещё не пользовались. Реального объёма не было, оплата шла виртуальной картой Mercury |
| reddit-291 — https://www.reddit.com/r/Anthropic/comments/1v48qe8/ | «banned for violating usage limits» | Пересказ автора, письмо не процитировано. Лимиты, по его словам, сгорали сами, и он подозревает взлом |
| hn-027 — https://news.ycombinator.com/item?id=47082249 | Поддержка в ответе на апелляцию: автоматизация подписки запрещена; автопродолжение после сброса 5-часового окна и несколько аккаунтов для обхода лимита — «banable» | Здесь причина — обход лимитов автоматизацией, а не сам объём. Исходное письмо стандартное: «suspicious signals … violation of our Usage Policy» |

**Ложный след: «high volume of signals».** У Anthropic есть стандартное письмо: «Our automated systems detected a high volume of signals associated with your account which violate our Usage Policy». Его читают как «забанили за большой объём». Пример — пост «banned my pro account because of high usage?»: https://www.reddit.com/r/Anthropic/comments/1sdqjcp/ (reddit-106). Ещё два: https://www.reddit.com/r/Anthropic/comments/1s2str8/ (reddit-096, бан через минуту после апгрейда) и https://www.reddit.com/r/ClaudeCode/comments/1ruyhmg/comment/oirb0dv/. На деле в письме речь о числе сигналов нарушения, а не о числе запросов.

Во всех остальных письмах, которые процитированы в выборке, стоят формулировки «violation of our Usage Policy», «suspicious signals», «unusual activity» и «user well-being». Объём в них не назван.

## Примеры

### Забаненный связывает бан со своим объёмом
- Признаёт, что часто выжимает квоты, но говорит, что это не должно быть причиной бана: https://www.reddit.com/r/ClaudeCode/comments/1v05fnr/ (reddit-276, Max 20x). Сам больше подозревает смену IP.
- Спрашивает другого забаненного, выжимал ли тот лимиты; о себе: «I definatly OFTEN maxed out my weekly usage on the max 5x»: https://www.reddit.com/r/ClaudeCode/comments/1uzykzl/ (reddit-275).
- «The extra coding the last couple days was the drop got me banned»: https://www.reddit.com/r/ClaudeCode/comments/1whi7rn/ (reddit-336, Max 5x).
- «It seems I was too active», несколько параллельных сессий в ночь 1 октября: https://www.reddit.com/r/ClaudeAI/comments/1wujje8/comment/pd644ok/ (reddit-392).
- Промо с кредитами Claude Code web, «I guess I used the credit too fast?»: https://www.reddit.com/r/ClaudeCode/comments/1ox23zl/ (reddit-056 и 057, два аккаунта Max 20x). Ещё: https://www.reddit.com/r/ClaudeCode/comments/1p1vo3q/ (reddit-061).
- «using the allowed limits to their fullest extent» как одна из версий: https://news.ycombinator.com/item?id=46733743 (hn-016, Max 20x).
- 13 подписок Max 20x и 10–15 терминалов одновременно: «my cost was higher than my subscription fees, and that was probably enough». https://news.ycombinator.com/item?id=48903047 (hn-059). На Reddit есть та же история с 13 подписками Max 20x и скриптом балансировки между ними: https://www.reddit.com/r/ClaudeCode/comments/1uouvo8/ (reddit-266).
- Объём из-за бага клиента: https://github.com/anthropics/claude-code/issues/18806 (`--continue`, github-091), https://github.com/anthropics/claude-code/issues/99413 (около 156 млн токенов за ночь в фоне, github-131).

### Общая теория «режут power users»
- «They are banning accounts that use too much quota sometimes … trying to get rid of power users»: https://www.reddit.com/r/ClaudeCode/comments/1whi7rn/comment/pa2o9tz/
- «Especially if you are a max 20x user that's costing them too much»: https://www.reddit.com/r/ClaudeCode/comments/1uzykzl/comment/oyfbf1v/
- «everyone getting banned because their account keep hitting weekly limit? … to save cost»: https://www.reddit.com/r/ClaudeCode/comments/1tcrxi1/comment/olsqdue/
- «they are losing money on the pro plan, so they are quick to ban»: https://www.reddit.com/r/Anthropic/comments/1u0q2ll/comment/or56hf8/
- «Theoretically you can max out every 5 hour window, but they lose money on that. This typically results in a ban»: https://news.ycombinator.com/item?id=47637281

### Опровержения: выжимают и не забанены
- Тут же, в ответ на предыдущую реплику: «I have maxed out my 5 hour limits and my weekly limits fairly regularly … I neither got a warning or a ban»: https://news.ycombinator.com/item?id=47637670
- «I used --prompt 100s of times per day and most of my usage comes from running Ralph loops overnight … so that's definitely not why you got banned»: https://www.reddit.com/r/Anthropic/comments/1r4c0t4/comment/o5b8z8j/
- Несколько аккаунтов Max 20x «running full tilt hitting limits every week». Часть аккаунтов забанили, но, по словам автора, из-за прокси, который сливал nginx-заголовки: https://news.ycombinator.com/item?id=46735897 (hn-022 и hn-023).
- «12 месяцев подряд выжигает Max до нуля каждую неделю» — пережил волну: https://www.reddit.com/r/ClaudeCode/comments/1wd1jwg/ (reddit-335).
- «once you hit the limit, they will just reject your call. You will not get ban»: https://www.reddit.com/r/ClaudeCode/comments/1p2br10/comment/npx8hqm/

### Забаненные, которые лимиты не выжимали
- «I've only used about 12% of my weekly limit»: https://www.reddit.com/r/Anthropic/comments/1wrk7wd/ (reddit-344)
- «I was on the 20x plan and was still within my limits when I got banned»: https://www.reddit.com/r/Anthropic/comments/1p36lxg/ (reddit-065)
- «I was not maxing out usage limits, I was not running things 24/7»: https://news.ycombinator.com/item?id=49530298 (hn-064)
- «Only roughly 30% of my weekly usage quota had been consumed»: https://github.com/anthropics/claude-code/issues/5088#issuecomment-5856934822 (github-072)
- «Never hit any session limits, never hit even 60% of my weekly limits»: https://www.reddit.com/r/ClaudeAI/comments/1pneatv/comment/nuby9bb/

## Вывод

Теорию «банят за выжимание лимитов» высказывают 41 кейс из 628 (7 %) и примерно каждый восьмой тред: 53 из 418. Прямого подтверждения со стороны Anthropic в выборке нет.

Объём как причину Anthropic назвали в пяти письмах. В двух из них объём создал баг расширения. В одном аккаунтом ещё не пользовались. Ещё одно известно только в пересказе. В последнем поддержка назвала причиной обход лимитов автоматизацией и несколькими аккаунтами.

Против теории говорят три вещи:
- 9 из 26 переживших волну сами пишут, что выжимают лимиты;
- 28 забаненных прямо говорят, что лимиты не выжимали;
- среди забаненных с известной интенсивностью heavy только 19 %, а light — 28 %.

Устойчивое ядро теории — не объём, а форма использования. Автоматизация, скрипты ротации аккаунтов, шеринг и автопродолжение после сброса окна вместе дают 13 из 41 кейса с yes. Это совпадает с единственным подробным ответом поддержки (hn-027).
