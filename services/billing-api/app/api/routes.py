from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/billing/webhook/stripe")
async def stripe_webhook(request: Request):
    data = await request.json()
    return {"received": data}


@router.post("/billing/webhook/razorpay")
async def razorpay_webhook(request: Request):
    data = await request.json()
    return {"received": data}
