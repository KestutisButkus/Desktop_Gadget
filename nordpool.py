import asyncio
import datetime
import aiohttp
from pynordpool import NordPoolClient
from pynordpool.const import Currency

VAT_MULTIPLIER = 1.21
KWH_DIVISOR = 1000


async def _fetch_prices() -> dict:
    """Asinchroniškai gauna šiandienos ir rytojaus elektros kainas."""
    async with aiohttp.ClientSession() as session:
        client = NordPoolClient(session)

        today = datetime.datetime.now()
        output_today = await client.async_get_delivery_period(today, Currency.EUR, ["LT"])
        price_today = round(output_today.area_average["LT"] * VAT_MULTIPLIER / KWH_DIVISOR, 3)

        tomorrow = today + datetime.timedelta(days=1)
        try:
            output_tomorrow = await client.async_get_delivery_period(tomorrow, Currency.EUR, ["LT"])
            price_tomorrow = round(output_tomorrow.area_average["LT"] * VAT_MULTIPLIER / KWH_DIVISOR, 3)
            tomorrow_str = f"{price_tomorrow} €"
        except Exception:
            tomorrow_str = "duomenų dar nėra."

        return {
            "today": f"{price_today} €",
            "tomorrow": tomorrow_str,
        }


def get_nordpool_info() -> str:
    """Sinchroninis wrapper elektros kainų gavimui."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            prices = loop.run_until_complete(_fetch_prices())
        finally:
            loop.close()
    except Exception as e:
        print(f"NordPool klaida: {e}")
        return "NordPool duomenų nepavyko gauti."

    return (
        f"Vidutinė elektros kaina šiandien: {prices['today']}\n"
        f"Rytoj: {prices['tomorrow']}"
    )


if __name__ == "__main__":
    print(get_nordpool_info())
