# MakerSpaceAPI

Integrate your MakerSpaceAPI into Home Assistant.

List rented items, products and their prices as well as balances of booking targets.

The products-endpoint is public, so you can add the stock of your MakerSpace to your private Home Assistant.
Current prices are listed in the attributes.

Items and balances need an token, which can be granted in the admin interface of the MakerSpaceAPI.
Items are listed as presence sensors, so if they are rented, they show away, otherwise at home.
The filament stock summary (`/filament/rolls/summary`) is public as well: one sensor per brand/type/weight/color
shows how many rolls are in stock (0 once the last roll is checked out).

Filament sensors also expose `rgb_color` (`[r, g, b]`) when the roll color is a `#RRGGBB` value, e.g. for a Mushroom card:
`icon_color: "rgb({{ state_attr(entity, 'rgb_color') | join(',') }})"`.
