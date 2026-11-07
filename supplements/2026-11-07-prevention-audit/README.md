# Source audit: Russian context, account histories and prevention claims

Audited 7 November 2026. This supplement adds source-level corrections and follow-ups to the existing dataset. It does not add ten new accounts and does not change the v2 row count.

`prevention-audit.json` contains:

- ten audit records covering existing histories, owner series and one unmerged candidate;
- five corrections or scope qualifications;
- one duplicate assessment;
- five series whose Russian citizenship or physical-location basis remains unresolved.

## Additional Telegram source

`dashi-candidates.json` preserves 43 candidate reports/owner series from comments under [dashi_agent/464](https://t.me/dashi_agent/464), including short reports of working accounts and unknown outcomes. These are not 43 new accounts or 43 confirmed Russian users. Six records have explicit Russian context: three Moscow statements and three Russian-document reports. The remaining records are not automatically classified as Russian.

`dashi-collection.json` records coverage and hashes: 166 unique comments retrieved against the widget's reported169, with all available backward-pagination pages exhausted. The reason for the gap is unknown. The post dates to2October and comments run through30October2026; these dates must not be relabeled as events of the29October wave. Two photo comments were inspected locally, including a generic appeal rejection and a self-reported token figure inside a ChatGPT prompt. The latter is not a Claude usage-meter screenshot, and the model-generated price table is not treated as a pricing source. Raw media and messages are not published.

Six Russian-context records were independently checked. A corrected detail: one owner describes a project with500+issues, not an established pending queue or completed task count. Cross-platform account/owner deduplication remains open; v2 is unchanged.

Russian citizenship, a Russian document, use from Russia and Russian-language discussion are distinct. A source-language group alone is insufficient to classify a person as Russian. These records retain the actual basis for each comparison.

Key corrections:

- `vcru-030`: the original says two accounts were blocked about ten seconds **after payment**. It does not establish registration dates or usage before payment. The previously coded age of zero is unsupported. The report is aggregate; do not create extra account IDs by counting every mention.
- `telegram-228`: a Cypriot card obtained through a friend is not proof of ownership. The earlier `own_card_foreign` label is unsupported.
- `telegram-a013`: a same-owner follow-up supports working access on 6 October rather than only 1 October.
- `v2-0073`: a Russian-language source describes residence abroad and citizenship of a supported country. Russian citizenship has not been established.

Owner comparisons preserve concurrent changes and observation periods. A replacement working on Pro has not necessarily passed the upgrade that preceded a previous account's block. Different outcomes on the same IP do not measure the effect of IP stability. May observations are historical context, not new events in the late-October wave.

User reports remain self-reports. Some original Telegram/vc.ru pages were reviewed through saved source archives when live retrieval failed. Private raw messages and identities are not included. The private correction is linked only to an existing public dataset ID.

No causal effect, population ban rate, safe utilization threshold or experimentally validated prevention configuration is estimated by this supplement. The existing v1/v2 snapshots remain unchanged so the corrections can be audited separately.
