import json
from pathlib import Path
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.transaction import Transaction
from solders.message import Message

DEVNET_URL = "https://api.devnet.solana.com"
MEMO_PROGRAM_ID = Pubkey.from_string(
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
)
DEFAULT_WALLET_PATH = Path.home() / ".config" / "solana" / "id.json"

def load_wallet(wallet_path=DEFAULT_WALLET_PATH):
    wallet_path = Path(wallet_path).expanduser()
    if not wallet_path.exists():
        raise FileNotFoundError(
            f"Could not find wallet file at {wallet_path}. "
            "Make sure your Solana wallet exists locally."
        )
    with open(wallet_path, "r", encoding="utf-8") as file:
        secret_key = json.load(file)
    return Keypair.from_bytes(bytes(secret_key))

def serialize_transition(transition):
    required_fields = ["songA", "songB", "score"]
    for field in required_fields:
        if field not in transition:
            raise ValueError(f"Missing required transition field: {field}")
    song_a = transition["songA"]
    song_b = transition["songB"]
    score = transition["score"]
    return f"{song_a}|{song_b}|{score}"

def store_transition(transition, wallet_path=DEFAULT_WALLET_PATH):
    client = Client(DEVNET_URL)
    payer = load_wallet(wallet_path)
    transition_text = serialize_transition(transition)
    transition_bytes = transition_text.encode("utf-8")
    instruction = Instruction(
        program_id=MEMO_PROGRAM_ID,
        accounts=[],
        data=transition_bytes
    )
    latest_blockhash = client.get_latest_blockhash().value.blockhash
    message = Message.new_with_blockhash(
        [instruction],
        payer.pubkey(),
        latest_blockhash
    )
    transaction = Transaction.new_unsigned(message)
    transaction.sign(
        [payer],
        latest_blockhash
    )
    response = client.send_transaction(transaction)
    signature = response.value
    return signature
if __name__ == "__main__":
    sample_transition = {
        "songA": "Titanium",
        "songB": "Clarity",
        "score": 0.91
    }
    signature = store_transition(sample_transition)
    print("Stored transition on Solana devnet.")
    print("Transaction signature:", signature)