# API Usage

Base URL (local): `http://localhost:8000`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/card/{id}` | Fetch a card by numeric identifier |
| GET | `/card/{id}/image` | Fetch card image (webp) |

## Examples

```bash
curl -s http://localhost:8000/card/597 | jq
```

```bash
curl -o card.webp http://localhost:8000/card/597/image
```
