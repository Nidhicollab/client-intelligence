# Miro board (optional)

Only when the user said yes in Step 3 and the Miro connector's tools are available.

1. Follow the Miro connector's own instructions first. It asks for its canvas guide to be loaded before any board is drawn.
2. Create one board named `<Company> · <role label> maps`.
3. Add one frame per output whose visual is `mermaid`, titled with the output's title, and draw the same diagram in it. Keep the same labels, including `(inferred)` and `(SOW)` markers.
4. Add a text frame titled `About this board` with the as-of date, the role, and, if an SOW was used, `Contains confidential client material`.
5. Put the board's link in `hub.json` as `miro_url`.

If the connector is missing or a call fails, skip the board, set `miro_url` to `null`, and add a line to `notes` saying why.
