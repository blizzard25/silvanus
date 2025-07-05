
# Silvanus API (GreenChain MVP)

This API allows users to submit green energy activity data and receive $SVN token rewards on-chain. Hosted on **Render**, this system directly interacts with a smart contract deployed on Ethereum Sepolia Testnet.

---

## Authentication

All requests require an API key:

```
Header: X-API-Key: YOUR_API_KEY
```

---

## Green Activity Submission

### `POST /activities/submit`

Submit a green energy activity (e.g., solar export, EV charging, thermostat adjustment).

**Payload Example:**

```json
{
  "wallet_address": "0x1234567890abcdef...",
  "activity_type": "solar_export",
  "value": 5.0,
  "details": {
    "note": "Test event from Raspberry Pi solar tracker",
    "platform": "Linux arm64",
    "timestamp": "2025-07-05T15:20:12Z"
  }
}
```

**Response Example:**

```json
{
  "txHash": "0xabc123...",
  "status": "confirmed"
}
```

- The contract calculates and distributes token rewards using a log-based diminishing formula.
- `value` is the number of kilowatt-hours (kWh).
- `details` can include optional diagnostic info.

---

## Supported Activity Types

### `GET /activities/types`

Returns the current list of supported green activities and expected fields in `details`.

```json
[
  {
    "type": "ev_charging",
    "description": "Charging EV using solar or off-peak grid power",
    "expectedDetails": ["kWhUsed", "chargingDuration", "offPeak"]
  },
  {
    "type": "regen_braking",
    "description": "Energy recovered through regenerative braking",
    "expectedDetails": ["kWhRecovered"]
  },
  {
    "type": "thermostat_adjustment",
    "description": "Smart thermostat behavior changes to save energy",
    "expectedDetails": ["targetTemp", "ecoMode"]
  },
  {
    "type": "solar_export",
    "description": "Power exported to grid from solar array",
    "expectedDetails": ["kWhExported"]
  }
]
```

---

## On-Chain Reward Logic

Smart contract: `GreenRewardDistributor.sol` on Sepolia

```solidity
adjustedReward = (score * baseReward) / log10(totalEvents + 10)
```

- Score = raw kWh value
- `baseReward` is set in the contract (e.g., 1 $SVN = 1e18 wei)
- `log10` penalty increases as more events are submitted

---

## Deprecated Routes (No Longer Used)

- `POST /devices/`
- `GET /wallets/{wallet}/score`
- `GET /wallets/{wallet}/events`
- `POST /wallets/{wallet}/claim`

These routes were part of a temporary in-memory scoring system and are now obsolete.

---

## 🚦 Health Check

### `GET /healthz`

Returns `200 OK` if the API is online.

---

## Contact & Support

Questions or issues? Please contact the administrator at **support@silvanusproject.com** or file a GitHub issue.