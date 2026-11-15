# ExploreTable

The landing page: every car in one sortable table, used and new prices side by side.

- Headers: plain label (`evs-label`) with the technical term below (`evs-term`). The header row is sticky, and so is the first column when scrolling sideways.
- Numbers are right-aligned, bold, tabular, with units ("330 km", "€15,500–19,000").
- Sorting: the header is a button, the column carries `aria-sort`, and an arrow shows direction.
- The last column holds the icon ShortlistButton, so people can tick cars without leaving the table.
- Rows highlight on hover (`paper-sea`); the whole row links to the car page.
- Simple shows 5 columns, Detailed 9, Nerd all. New columns appear on the right.
- Under 768px the default is CarCard view. The table still works with sideways scroll.
- No zebra stripes, except in Nerd mode for very wide tables (`surface-sunk`).
