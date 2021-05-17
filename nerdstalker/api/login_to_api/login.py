from .sensitive_data import callofduty_login
import callofduty, asyncio

async def callofduty_client():
    client = await callofduty.Login(callofduty_login['email'], callofduty_login['password'])
    return client