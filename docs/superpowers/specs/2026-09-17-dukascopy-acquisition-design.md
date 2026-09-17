# Quant_Lab Dukascopy Acquisition Design

## Objective

Acquire immutable Dukascopy historical tick data and derive canonical M1 bars for nine approved instruments over `[2019-01-02, 2026-09-01)` UTC.

## Source contract

Dukascopy `.bi5` tick files use zero-indexed months. The current hourly path is `https://www.dukascopy.com/datafeed/{symbol}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5`. Records are 20 bytes, big-endian, with milliseconds, ask, bid, ask volume and bid volume. Missing files can represent no data for non-trading periods. These facts are verified against Dukascopy documentation.

## Data path

Request -> plan -> download -> immutable raw -> hash -> manifest -> LZMA decode -> tick validation -> M1 aggregation -> session/gap validation -> Parquet.

## Failure policy

No certificate bypass, no synthetic values, no silent gap repair, no silent price scaling. Retry transient transport failures; classify 404 as `NO_DATA`; reject malformed, truncated, invalid, duplicated, or unexplained data.

## Instrument registry

`usa30idxusd`, `usa500idxusd`, `usatechidxusd`, `deuidxeur`, `gbridxgbp`, `jpnidxjpy`, `xauusd`, `dollaridxusd`, `volidxusd`.

Price scale is registry data and must be verified per instrument before production acquisition; it is not inferred from a generic FX rule.
