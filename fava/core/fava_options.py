"""Fava's options.

Options for Fava can be specified through Custom entries in the Beancount file.
This module contains a list of possible options, the defaults and the code for
parsing the options.

"""

import copy
from collections import namedtuple
import re

OptionError = namedtuple("OptionError", "source message entry")
InsertEntryOption = namedtuple("InsertEntryOption", "date re filename lineno")

DEFAULTS = {
    "account-journal-include-children": True,
    "currency-column": 61,
    "collapse-pattern": [],
    "conversion-currencies": [
        # ISO 4217 https://www.currency-iso.org/en/home/tables/table-a1.html
        "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
        "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV",
        "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF",
        "CHW", "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE",
        "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD",
        "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD",
        "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK",
        "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD",
        "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL",
        "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN",
        "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR",
        "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD",
        "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLL",
        "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT",
        "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USN",
        "UYI", "UYU", "UYW", "UZS", "VES", "VND", "VUV", "WST", "XAF", "XAG",
        "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XDR", "XOF", "XPD", "XPF",
        "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWL",
    ],
    "auto-reload": False,
    "default-file": None,
    "fiscal-year-end": "12-31",
    "import-config": None,
    "import-dirs": [],
    "insert-entry": [],
    "interval": "month",
    "journal-show": [
        "transaction",
        "balance",
        "note",
        "document",
        "custom",
        "budget",
        "query",
    ],
    "journal-show-document": ["discovered", "statement"],
    "journal-show-transaction": ["cleared", "pending"],
    "language": None,
    "locale": None,
    "show-accounts-with-zero-balance": True,
    "show-accounts-with-zero-transactions": True,
    "show-closed-accounts": False,
    "sidebar-show-queries": 5,
    "unrealized": "Unrealized",
    "upcoming-events": 7,
    "uptodate-indicator-grey-lookback-days": 60,
    "use-external-editor": False,
}

BOOL_OPTS = [
    "account-journal-include-children",
    "auto-reload",
    "show-accounts-with-zero-balance",
    "show-accounts-with-zero-transactions",
    "show-closed-accounts",
    "use-external-editor",
]

INT_OPTS = [
    "currency-column",
    "sidebar-show-queries",
    "upcoming-events",
    "uptodate-indicator-grey-lookback-days",
]

LIST_OPTS = [
    "conversion-currencies",
    "import-dirs",
    "journal-show",
    "journal-show-document",
    "journal-show-transaction",
]

STR_OPTS = [
    "collapse-pattern",
    "fiscal-year-end",
    "import-config",
    "interval",
    "language",
    "locale",
    "unrealized",
]

# options that can be specified multiple times
MULTI_OPTS = ["collapse-pattern"]


# pylint: disable=too-many-branches
def parse_options(custom_entries):
    """Parse custom entries for Fava options.

    The format for option entries is the following:

        2016-04-01 custom "fava-option" "[name]" "[value]"

    Args:
        custom_entries: A list of Custom entries.

    Returns:
        A tuple (options, errors) where options is a dictionary of all options
        to values, and errors contains possible parsing errors.

    """

    options = copy.deepcopy(DEFAULTS)
    errors = []

    for entry in custom_entries:
        if entry.type == "fava-option":
            try:
                key = entry.values[0].value
                assert key in DEFAULTS.keys()

                if key == "default-file":
                    options[key] = entry.meta["filename"]
                elif key == "insert-entry":
                    opt = InsertEntryOption(
                        entry.date,
                        re.compile(entry.values[1].value),
                        entry.meta["filename"],
                        entry.meta["lineno"],
                    )
                    options[key].append(opt)
                else:
                    value = entry.values[1].value
                    assert isinstance(value, str)

                processed_value = None
                if key in STR_OPTS:
                    processed_value = value
                elif key in BOOL_OPTS:
                    processed_value = value.lower() == "true"
                elif key in INT_OPTS:
                    processed_value = int(value)
                elif key in LIST_OPTS:
                    processed_value = str(value).strip().split(" ")

                if processed_value is not None:
                    if key in MULTI_OPTS:
                        options[key].append(processed_value)
                    else:
                        options[key] = processed_value

            except (IndexError, TypeError, AssertionError):
                errors.append(
                    OptionError(
                        entry.meta, "Failed to parse fava-option entry", entry
                    )
                )

    return options, errors
