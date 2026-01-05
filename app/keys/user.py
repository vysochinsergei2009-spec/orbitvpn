from .common import kb
from ._callbacks import (
    BUY_SUB,
    ADD_FUNDS,
    MY_VPN,
)

def main_menu_kb(t):
    return kb([
        (t("my_vpn"), MY_VPN),
        (t("buy_sub"), BUY_SUB),
        (t("add_funds"), ADD_FUNDS),
    ], row=1)


def subscriptions_kb(t):
    return kb([
        (t("sub_1m"), "sub_1m"),
        (t("sub_3m"), "sub_3m"),
        (t("sub_6m"), "sub_6m"),
        (t("sub_12m"), "sub_12m"),
    ])
