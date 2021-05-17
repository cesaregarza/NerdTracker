import asyncio, callofduty

async def retrieve_matches(profile):
    matches = await profile.matches(callofduty.Title.ModernWarfare, callofduty.Mode.Multiplayer, limit=50)
    return matches