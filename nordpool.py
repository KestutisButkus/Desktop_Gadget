import asyncio
import datetime
import aiohttp
from pynordpool import NordPoolClient
from pynordpool.const import Currency

async def get_prices() -> dict:
    """Gaukite šiandienos ir rytojaus vidutines elektros kainas."""
    async with aiohttp.ClientSession() as session:
        client = NordPoolClient(session)
        # Gaukite šiandienos duomenis
        output_today = await client.async_get_delivery_period(
            datetime.datetime.now(), Currency.EUR, ["LT"]
        )
        average_price_today = output_today.area_average["LT"] * 1.21 / 1000
        price_today = round(average_price_today, 3)

        try:
            output_tomorrow = await client.async_get_delivery_period(
                datetime.datetime.now() + datetime.timedelta(days=1), Currency.EUR, ["LT"]
            )
            average_price_tomorrow = output_tomorrow.area_average["LT"] * 1.21 / 1000
            price_tomorrow = round(average_price_tomorrow, 3)
            return {
                "today": f"{price_today} €",
                "tomorrow": f"{price_tomorrow} €"
            }
        except:
            return {
                "today": f" {price_today} €",
                "tomorrow": " duomenų dar nėra."
            }

def get_nordpool_info():
    prices = asyncio.run(get_prices())
    nordpool_info = (
        f"Vidutinė elektros kaina šiandien: {prices['today']}\n"
        f"Rytoj: {prices['tomorrow']}"
    )
    return nordpool_info

if __name__ == "__main__":
    print(get_nordpool_info())
