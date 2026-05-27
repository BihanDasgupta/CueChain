# CueChain Local Setup

CueChain runs with a Flask backend and a Vite React frontend.

## Backend Setup

From the project root:

```bash
pip install flask flask-cors tensorflow solana solders numpy
```

The backend expects the saved model file:

```text
transition_model.keras
```

If it is missing, regenerate it with:

```bash
python song_compare_model_UPDATED.py
```

For Solana devnet writes, create or use a local wallet at:

```text
~/.config/solana/id.json
```

Fund that wallet with devnet SOL using a faucet such as:

```text
https://faucet.solana.com/
```

## Frontend Setup

From the project root:

```bash
npm --prefix ./frontend install
```

## Run Locally

Start the backend from the project root:

```bash
python app.py
```

The backend runs at:

```text
http://localhost:5000
```

Start the frontend from the project root:

```bash
npm --prefix ./frontend run dev
```

The frontend runs at:

```text
http://localhost:5173
```

## Quick Test

Open the frontend and search for a song in `songs.py`, such as:

```text
2U
```

Recommendations should appear, high-scoring transitions should store on Solana devnet, and the transition memory chain should update as you click recommended tracks.
