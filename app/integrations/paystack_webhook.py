from __future__ import annotations

import hashlib
import hmac


class PaystackWebhook:

    @staticmethod
    def verify_signature(
        payload: bytes,
        signature: str,
        secret_key: str,
    ) -> bool:

        computed_signature = hmac.new(
            secret_key.encode(),
            payload,
            hashlib.sha512,
        ).hexdigest()

        return hmac.compare_digest(
            computed_signature,
            signature,
        )