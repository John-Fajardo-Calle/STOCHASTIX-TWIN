"""Backend entry point.

I keep a tiny `main()` wrapper so the service can be started via `python -m` or
as a module import by tools.
"""

from __future__ import annotations

import uvicorn


def main() -> None:
    """Launch the dev server with reload enabled."""

    uvicorn.run("backend.api.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
