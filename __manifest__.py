# -*- coding: utf-8 -*-
{
    "name": "Autonsi Stock Adjustment",
    "summary": "",
    "description": "",
    "author": "Autonsi",
    "website": "http://www.yourcompany.com",
    "category": "Autonsi",
    "version": "0.1",
    "sequence": 0,
    "depends": [
        "autonsi_wms_dongjin",
        "autonsi_standard_dongjin"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/stock_check_order.xml",
        "views/stock_adjustment_order.xml"

    ],
    "assets": {
        "web.assets_backend": [
            "autonsi_stock_adjustment/static/src/js/stock_check_order_button.js",
            "autonsi_stock_adjustment/static/src/js/stock_check_save_order_button.js",
        ],
        'web.assets_qweb': [
            "autonsi_stock_adjustment/static/src/xml/stock_check_order_button.xml",
        ]
    },
}
