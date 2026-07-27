from __future__ import annotations

import httpx

from fastapi import HTTPException, status

from app.core.config import settings


class PaystackClient:

    async def initialize_transaction(
        self,
        email: str,
        amount: int,
        reference: str,
        metadata: dict | None = None,
    ) -> dict:

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
                headers={
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "email": email,
                    "amount": amount,
                    "reference": reference,
                    "metadata": metadata,
                }   
            )

        response.raise_for_status()

        payload = response.json()

        if not payload.get("status"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=payload.get(
                    "message",
                    "Unable to initialize payment.",
                ),
            )

        return payload["data"]

    async def verify_transaction(
        self,
        reference: str,
    ) -> dict:

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
                headers={
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                },
            )

        response.raise_for_status()

        payload = response.json()

        if not payload.get("status"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=payload.get(
                    "message",
                    "Unable to verify payment.",
                ),
            )

        return payload["data"]