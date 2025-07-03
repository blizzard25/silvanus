# Silvanus API

Silvanus is a RESTful API designed to track and reward eco-friendly behaviors from devices such as electric vehicles, smart thermostats, solar systems, and more. This API enables registration of devices, submission of green activities, and the claiming of rewards.

## Live API URL

The API is live and accessible at:

**https://silvanus-a4nt.onrender.com**

Interactive documentation (Swagger UI) is available at:

**https://silvanus-a4nt.onrender.com/docs**

## Setup Instructions (Local Use Optional)

### Prerequisites

- Python 3.10+
- `pip` for managing packages

### Installation (Local Dev Only)

1. Clone the repository:

```bash
git clone https://github.com/blizzard25/silvanus.git
cd silvanus
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r api/requirements.txt
```

### Running the API Server Locally

Only required for development:

```bash
uvicorn api.main:app --reload
```

## API Endpoints

All endpoints require an API key to be sent in the header:  
`X-API-Key: your-api-key`

### Device Management

- `POST /devices/`: Register a device
- `GET /devices/`: List all registered devices

### Activity Submission

- `POST /activities/`: Submit a green activity

### Wallet Management

- `GET /wallets/{wallet}/score`: Retrieve green score for a wallet
- `GET /wallets/{wallet}/events`: List all claim events for a wallet
- `POST /wallets/{wallet}/claim`: Trigger a reward claim

### Activity Metadata

- `GET /activities/types`: Retrieve metadata and expected fields for activity types

### Health Check

- `GET /healthz`: Simple endpoint for health monitoring

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

## Running Tests

A test script is included in the `python` subdirectory:

```bash
python test_greenchain_api.py
```

Make sure the base URL and `X-API-Key` are set correctly in the script.

## License

This project is licensed under the MIT License.
