# Silvanus API

Silvanus is a RESTful API designed to track and reward eco-friendly behaviors from devices such as electric vehicles, smart thermostats, solar systems, and more. This API enables registration of devices, submission of green activities, and the claiming of rewards.

## Project Structure

```
silvanus/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       ├── activities.py
│       ├── activity_types.py
│       ├── devices.py
│       └── wallets.py
├── test_greenchain_api.py
├── requirements.txt
└── README.md
```

## Features

- Register and manage green activity tracking devices
- Submit green activities (e.g., EV charging, regen braking, thermostat adjustments)
- Query green activity scores and event logs
- Claim rewards based on accumulated score

## Setup Instructions

### Prerequisites

- Python 3.10+
- `pip` for managing packages

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/silvanus.git
cd silvanus
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the API Server

```bash
uvicorn api.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the automatically generated Swagger UI.

## API Endpoints

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

A simple test script is included:

```bash
python test_greenchain_api.py
```

## License

This project is licensed under the MIT License.
