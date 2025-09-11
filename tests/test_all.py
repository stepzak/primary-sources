import datetime
import string
import pytest
from main import get_voyager_launch_date, get_rfc_date, get_unicode, get_btc_generic_block_date, get_kr2_isbn10

YEAR = datetime.datetime.now().year


def check_date(res: str):
    return (
            len(res) == 8
            and
            1970 <= int(res[:4]) <= YEAR
            and
            0 < int(res[4:6]) <= 12
            and
            0 < int(res[6:]) <= 31
    )


@pytest.mark.asyncio
async def test_get_voyager_launch_date():
    res = await get_voyager_launch_date()
    assert check_date(res)

@pytest.mark.asyncio
async def test_get_rfc_date():
    res = await get_rfc_date()
    assert check_date(res)


@pytest.mark.asyncio
async def test_get_unicode():
    res = await get_unicode()
    assert all(c in string.hexdigits for c in res)


@pytest.mark.asyncio
async def test_get_btc_generic_block_date():
    res = await get_btc_generic_block_date()
    assert check_date(res)


@pytest.mark.asyncio
async def test_get_kr2_isbn10():
    res = await get_kr2_isbn10()
    assert "-" not in res and len(res)==10