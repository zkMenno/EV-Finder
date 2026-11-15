# RangeRoute

The signature component: real range drawn as a holiday-map route from the visitor's town to real places.

- Ground: `sea` with `meadow` land (decorative). A white `surface` road underlay; summer range as a solid `sky` line, winter range as a dotted `ink` line.
- Pins: white circles with an ink ring. Estimated charge stops: sunflower squares (`radius-sm`). Place names in Atkinson bold 14px; handwritten notes in `map-note` (Patrick Hand) for the fun line ("no stop needed").
- The legend underneath (`evs-route__legend`) is the text equivalent: summer km, winter km, symbol key, ABRP hand-off link. The SVG also has a title and a desc.
- Start town: typed by the user or the country capital. No geolocation without asking.
- Charge stops are estimates from range and typical motorway charger spacing: we hold no charger map. Say "Estimated charge stop".
- Motion: the line draws once on first view (600ms), then stays still. Reduced motion shows it already drawn.
- Builders provide: start town, place list with distances, summer and winter range, source and date. The geo approach (illustrated base map or open tiles) is the web-app chat's decision.
