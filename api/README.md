# Silvanus API Documentation

This API allows devices and applications to report green activities and earn rewards in $SVN tokens. Hosted on **Render**, this REST API provides endpoints to register devices, submit activities, check wallet scores, view events, and claim token rewards.

---

## Authentication

All requests must include an API key:

**Header:**
```
x-api-key: YOUR_API_KEY_HERE
```

---

## API Endpoints

### `POST /devices/`

Register a device.

**Payload:**
```json
{
  "device_id": "RewardTestSolar2",
  "owner_wallet": "0x1234567890abcdef...",
  "location": "Tennessee"
}
```

**Response:** `200 OK`
```json
{
  "device_id": "RewardTestSolar2",
  "owner_wallet": "0x1234567890abcdef...",
  "location": "Tennessee"
}
```

---

### `POST /activities/`

Submit a green activity (e.g. EV miles, solar charging, regeneration).

**Payload:**
```json
{
  "device_id": "RewardTestSolar2",
  "activity_type": "solar_export",
  "value": 100.0,
  "timestamp": "2025-07-03T23:22:14.913181Z"
}
```

**Response:** `200 OK`

---

### `GET /wallets/{wallet}/score`

Returns the current reward score for a wallet.

**Example:**
```
GET /wallets/0x123...abcd/score
```

**Response:**
```json
{
  "wallet": "0x123...abcd",
  "score": 150.0
}
```

---

### `GET /wallets/{wallet}/events`

Returns all green activity events submitted for a wallet.

**Example:**
```
GET /wallets/0x123...abcd/events
```

**Response:**
```json
[
  {
    "activity": "solar_export",
    "value": 100.0,
    "timestamp": "2025-07-03T23:22:14.913181Z",
    "details": {}
  }
]
```

---

### `POST /wallets/{wallet}/claim`

Submit a claim to receive $SVN tokens based on your score.

**Example:**
```
POST /wallets/0x123...abcd/claim
```

**Response on success:**
```json
{
  "txHash": "0xabc123...",
  "status": "submitted"
}
```

**Error (Nothing to claim):**
```json
{
  "detail": "Nothing to claim"
}
```

**Error (Blockchain issue):**
```json
{
  "detail": "Error submitting transaction: ..."
}
```

---

## Activity Types (Example)

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

## Reward Calculation

1. **Score = activity_value × activity_weight**
    - e.g., `solar_export` has a weight of `1.5`
    - 100.0 solar_export → 150 score
2. **Reward = (score × baseReward) / log10(totalEvents + 10)`**
    - Rewards reduce over time as total events increase.
    - baseReward is currently `1e18` (1 $SVN in wei).

---

## Example Usage Flow

1. `POST /devices/` → register your device
2. `POST /activities/` → log green activity
3. `GET /wallets/{wallet}/score` → check updated score
4. `POST /wallets/{wallet}/claim` → claim rewards ($SVN tokens)

---

## Health Check

```
GET /healthz
```

Returns `200 OK` if the API is up.

---

## Support

If you encounter issues using the API or have questions about reward mechanics, please contact the system administrator.