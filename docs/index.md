# tess-utils

Shared converters for the Tesserae projects (`tess-shell`, Tesserae UI). tre, the rendering engine,
takes one standard form for each kind of value, and the forms a TDL file writes (colours,
four-sided values, corner radii, enum words, image files) are turned into that form here, once,
so no consumer repeats the conversion.

Import name `tess_utils`. Python 3.14 or later. MIT. The converters have no dependencies; only
`decode_image` and `decode_image_file` need Pillow, and import it inside the function.

```python
from tess_utils import expand_radius, expand_sides, parse_color, to_tre_order, to_tre_word

parse_color("#89b4fa80")                 # (137, 180, 250, 128)
to_tre_order(expand_sides({"Left": 24})) # (0.0, 0.0, 0.0, 24.0)
expand_radius([0, 0, 8, 8])              # (0.0, 0.0, 8.0, 8.0)
to_tre_word("SPACE_BETWEEN")             # "space_between"
```

## What belongs here

A function is added when at least two projects use it, it is a few lines of our own code (a mapped
library only for work that would be a project of its own), it imports no Tesserae package, it has
no dependency and no UI or schema meaning, and it has tests. Schema, typing and UI meaning stay in
the projects.

## Where to go next

- [Reference](reference.md): every public function, what it accepts and what it raises.
- [Distribution](distribution.md): how a release reaches a consumer (one compiled file, not PyPI).
- [Changelog](changelog.md).
