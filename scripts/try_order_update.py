import json
import os
import sys

import httpx


def main() -> None:
    base_url = os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:8000")
    response = httpx.request(
        method="POST",
        url=f"{base_url}/order-updates",
        json={
            "order_id": "ord_1042",
            "transcript": "I paid at checkout. Please start packing my camera strap.",
            "current_stage": "checkout_pending",
        },
        timeout=20,
    )
    print(json.dumps(response.json(), indent=2))
    sys.exit(0 if response.is_success else 1)


if __name__ == "__main__":
    main()
