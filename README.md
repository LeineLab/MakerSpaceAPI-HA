# MakerSpaceAPI

Integrate your MakerSpaceAPI into Home Assistant.

List rented items, products and their prices as well as balances of booking targets.

The products-endpoint is public, so you can add the stock of your MakerSpace to your private Home Assistant.
Current prices are listed in the attributes.

Items and balances need an token, which can be granted in the admin interface of the MakerSpaceAPI.
Items are listed as presence sensors, so if they are rented, they show away, otherwise at home.