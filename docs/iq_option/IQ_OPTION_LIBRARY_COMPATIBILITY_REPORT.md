# IQ Option Library Compatibility Report

## Scope

This report records the isolated compatibility probe for using the community IQ Option API in Friday Trade.

The probe was executed in a temporary environment only:

```text
.jarvis_cache/iq_option_probe_venv
```

The main project `.venv` was not modified.

## Selected Source

Repository:

```text
https://github.com/iqoptionapi/iqoptionapi.git
```

Pinned commit:

```text
8a903cc094a74af1ed935a56a2d6b5a9ed3319d7
```

Installed distribution:

```text
iqoptionapi==7.1.1
```

The old PyPI package `iqoptionapi==0.5` was reviewed but not selected because it was released in 2016 and does not represent the current community repository state.

## Source Notes

- The GitHub project identifies itself as a community and non-official API.
- The GitHub README warns against real-account usage and documents Python 3.7-era assumptions.
- The repository dependency set still pins `websocket-client==0.56.0`.
- The project includes order, balance, and account mutation APIs, so Friday Trade must keep a strict read-only wrapper.

## Isolated Environment

Python:

```text
Python 3.11.15
```

Pip:

```text
pip 26.1.2
```

Installed dependencies:

```text
iqoptionapi @ git+https://github.com/iqoptionapi/iqoptionapi.git@8a903cc094a74af1ed935a56a2d6b5a9ed3319d7
websocket-client==0.56.0
requests==2.34.2
urllib3==2.7.0
certifi==2026.6.17
charset-normalizer==3.4.9
idna==3.18
six==1.17.0
pylint==4.0.6
```

## Probe Results

Import:

```text
IMPORT_OK
```

Client construction with redacted placeholder credentials:

```text
CLIENT_CREATED
```

Network authorization:

```text
NETWORK_ALLOWED=False
```

Credential availability:

```text
CREDENTIALS_CONFIGURED=False
```

PRACTICE connection:

```text
NOT_EXECUTED
```

Reason:

```text
Network probe requires IQ_OPTION_PROBE_ALLOW_NETWORK=true and local practice credentials.
```

OTC asset list:

```text
NOT_EXECUTED
```

M1, M5, M15 candle requests:

```text
NOT_EXECUTED
```

Reason:

```text
Real market requests require a confirmed PRACTICE connection.
```

## Read-Only Evidence

Forbidden methods observed on the installed library surface include:

```text
buy
buy_by_raw_expirations
buy_digital
buy_digital_spot
buy_digital_spot_v2
buy_multi
buy_order
cancel_order
change_balance
change_order
close_position
close_position_v2
get_balance
get_balances
get_digital_position
get_order
get_position
reset_practice_balance
sell_digital_option
sell_option
```

The Friday Trade probe and provider tests use fake clients and a read-only guard to ensure those methods are not called.

## Compatibility Assessment

Current result:

```text
PARTIAL_OFFLINE_COMPATIBILITY
```

Confirmed:

- Installation from pinned GitHub commit works in an isolated Python 3.11 environment.
- Import works.
- Client construction works.
- The main `.venv` does not contain `iqoptionapi`.
- Offline mapping for OTC assets and M1/M5/M15 candle structures is covered by tests.

Not confirmed:

- PRACTICE login.
- Real OTC asset listing.
- Real M1 candles.
- Real M5 candles.
- Real M15 candles.
- Runtime stability of `websocket-client==0.56.0` under Python 3.11 and macOS.

## Conflicts and Risks

- `websocket-client==0.56.0` is very old and may conflict with newer websocket usage if installed into the main environment.
- The library exposes write/order and balance functions; Friday Trade must never expose the raw client to app code.
- Real connection validation remains blocked without local PRACTICE credentials and explicit network authorization.
- Integration into the main `.venv` should wait until the PRACTICE connection and candle fetch tests are executed successfully.

## Required Next Probe

Run a real PRACTICE-only probe from the isolated environment with:

```text
IQ_OPTION_PROBE_ALLOW_NETWORK=true
IQ_OPTION_EMAIL=<local ignored value>
IQ_OPTION_PASSWORD=<local ignored value>
```

The probe must not print credentials and must not call balance, order, payout, position, or account mutation methods.
