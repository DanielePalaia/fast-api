import pytest
from unittest.mock import AsyncMock, patch

from fever_integration import FeverClient

VALID_XML_TWO_ONLINE = """
<planList>
  <output>
    <base_plan base_plan_id="bp1" sell_mode="online" title="Event One">
      <plan plan_start_date="2025-01-01T10:00:00" plan_end_date="2025-01-01T12:00:00" plan_id="1" sell_from="2024-01-01T00:00:00" sell_to="2025-01-01T09:00:00" sold_out="false">
        <zone zone_id="1" capacity="100" price="10.0" name="Zone 1" numbered="true" />
        <zone zone_id="2" capacity="200" price="20.0" name="Zone 2" numbered="false" />
      </plan>
    </base_plan>
    <base_plan base_plan_id="bp2" sell_mode="online" title="Event Two">
      <plan plan_start_date="2025-02-01T10:00:00" plan_end_date="2025-02-01T12:00:00" plan_id="2" sell_from="2024-02-01T00:00:00" sell_to="2025-02-01T09:00:00" sold_out="false">
        <zone zone_id="3" capacity="150" price="15.0" name="Zone 3" numbered="true" />
      </plan>
    </base_plan>
  </output>
</planList>
"""


@pytest.mark.asyncio
async def test_parse_two_online_events():
    client = FeverClient()
    plans = client._parse_plans(VALID_XML_TWO_ONLINE)

    assert len(plans) == 2

    event1 = next(p for p in plans if p.id.startswith("bp1"))
    event2 = next(p for p in plans if p.id.startswith("bp2"))

    assert event1.title == "Event One"
    assert event1.min_price == 10.0
    assert event1.max_price == 20.0

    assert event2.title == "Event Two"
    assert event2.min_price == 15.0
    assert event2.max_price == 15.0


@pytest.mark.asyncio
async def test_parse_malformed_xml_logs_error(caplog):
    client = FeverClient()
    malformed_xml = "<planList><output><base_plan></planList>"  # missing closing tags

    with caplog.at_level("ERROR"):
        plans = client._parse_plans(malformed_xml)

    assert plans == []
    assert "XML parsing failed" in caplog.text


def test_skips_base_plan_with_missing_fields(caplog):
    xml = """
    <planList>
      <output>
        <base_plan sell_mode="online">
          <plan plan_start_date="2025-01-01T10:00:00" plan_end_date="2025-01-01T12:00:00" plan_id="1">
            <zone price="10.0"/>
          </plan>
        </base_plan>
      </output>
    </planList>
    """
    client = FeverClient()
    with caplog.at_level("WARNING"):
        plans = client._parse_plans(xml)

    assert plans == []
    assert "Skipping base_plan with missing id or title" in caplog.text


@pytest.mark.asyncio
async def test_fetch_events_parses_xml():
    client = FeverClient()
    with patch(
        "fever_integration.client.httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = VALID_XML_TWO_ONLINE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        plans = await client.fetch_events()

    assert len(plans) == 2
    assert any(p.title == "Event One" for p in plans)