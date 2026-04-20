import datetime
import logging
import requests

VAT_MULTIPLIER = 1.21
KWH_DIVISOR = 1000
API_URL = "https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices"


def _fetch_price(date: datetime.date) -> float | None:
    params = {
        "date": date.strftime("%Y-%m-%d"),
        "market": "DayAhead",
        "deliveryArea": "LT",
        "currency": "EUR",
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        if resp.status_code == 204:
            return None
        resp.raise_for_status()
        rows = resp.json().get("multiAreaEntries", [])
        prices = [r["entryPerArea"]["LT"] for r in rows if "LT" in r.get("entryPerArea", {})]
        if not prices:
            return None
        return round(sum(prices) / len(prices) * VAT_MULTIPLIER / KWH_DIVISOR, 3)
    except Exception as e:
        logging.error(f"NordPool klaida ({date}): {e}", exc_info=True)
        return None


def get_nordpool_info() -> str:
    today = datetime.date.today()
    price_today = _fetch_price(today)

    if price_today is None:
        return "NordPool duomenų nepavyko gauti."

    tomorrow = today + datetime.timedelta(days=1)
    price_tomorrow = _fetch_price(tomorrow)
    tomorrow_str = f"{price_tomorrow} €" if price_tomorrow is not None else "duomenų dar nėra."

    return (
        f"Vidutinė elektros kaina šiandien: {price_today} €\n"
        f"Rytoj: {tomorrow_str}"
    )


if __name__ == "__main__":
    print(get_nordpool_info())