import logging
from datetime import datetime
from typing import List
from xml.etree import ElementTree as ET

import httpx

from .config import settings
from .models import Plan

logger = logging.getLogger(__name__)


class FeverClient:

    async def fetch_events(self) -> List[Plan]:
        """Fetches and parses plans from the external provider"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    settings.PROVIDER_URL, headers={"Accept": "application/xml"}
                )
                response.raise_for_status()
                return self._parse_plans(response.text)

            except httpx.HTTPStatusError as e:
                logger.error(f"Provider API error: {e.response.status_code}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                return []

    def _parse_plans(self, xml_data: str) -> List[Plan]:
        """Converts XML to SQLAlchemy Plan objects"""
        plans = []
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            return []

        for base_plan in root.findall(".//base_plan"):
            # Only consider base_plans with sell_mode 'online'
            if base_plan.get("sell_mode") != "online":
                continue

            base_plan_id = base_plan.get("base_plan_id")
            base_plan_title = base_plan.get("title")
            if base_plan_id is None or base_plan_title is None:
                logger.warning("Skipping base_plan with missing id or title")
                continue

            for plan in base_plan.findall(".//plan"):
                plan_start_date = plan.get("plan_start_date")
                plan_end_date = plan.get("plan_end_date")
                if plan_start_date is None or plan_end_date is None:
                    logger.warning("Skipping plan with missing start or end date")
                    continue

                # Gather prices from zones
                prices = []
                for zone in plan.findall("zone"):
                    price_str = zone.get("price")
                    if price_str:
                        try:
                            prices.append(float(price_str))
                        except ValueError:
                            logger.warning(f"Invalid price value: {price_str}")

                if not prices:
                    min_price = 0.0
                    max_price = 0.0
                else:
                    min_price = min(prices)
                    max_price = max(prices)

                try:
                    plan_obj = Plan(
                        id=f"{base_plan_id}-{plan.get('plan_id')}",  # unique composite id
                        base_plan_id=base_plan_id,
                        title=base_plan_title,
                        start_datetime=datetime.fromisoformat(plan_start_date),
                        end_datetime=datetime.fromisoformat(plan_end_date),
                        last_seen=datetime.now(),
                        min_price=min_price,
                        max_price=max_price,
                    )
                    plans.append(plan_obj)
                except Exception as e:
                    logger.error(f"Plan parse error: {e}", exc_info=True)
        return plans
