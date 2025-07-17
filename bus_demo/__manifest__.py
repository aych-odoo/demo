{
    "name": "Bus Demo",
    "summary": "A tutorial to learn BUS module",
    "author": "Ayush Chauhan",
    "website": "https://www.github.com/aych-odoo",
    "category": "Demo/Bus",
    "version": "1.0",
    "application": True,
    "installable": True,
    "depends": ["base", "web", "bus"],
    "data": [
        "views/bus_demo_views.xml",
        "views/bus_demo_menus.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "bus_demo/static/src/**/*",
        ],
    },
    "license": "AGPL-3",
}
