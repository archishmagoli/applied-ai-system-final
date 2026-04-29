import anthropic
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("pawpal.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

_CATEGORIES = {"walk", "feed", "groom", "play", "medical", "other"}
_PRIORITIES = {"high", "medium", "low"}


def suggest_tasks(pet_name: str, species: str, age: int) -> dict:
    """Ask Claude to suggest daily care tasks for a pet.

    Returns:
        {
          "success": bool,
          "tasks": [{"name": str, "duration": int, "priority": str, "category": str}, ...],
          "confidence": float,  # 0.0–1.0, fraction of returned tasks that passed validation
          "error": str | None,
        }
    """
    client = anthropic.Anthropic()

    prompt = (
        "You are a veterinary assistant. Suggest 3-5 appropriate daily care tasks "
        f"for a {age}-year-old {species} named {pet_name}.\n\n"
        "Respond ONLY with a JSON object in this exact shape — no explanation, no markdown:\n"
        '{"tasks": [{"name": "...", "duration": <int minutes>, '
        '"priority": "high|medium|low", "category": "walk|feed|groom|play|medical|other"}]}'
    )

    logger.info("suggest_tasks | pet=%s species=%s age=%d", pet_name, species, age)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        logger.info("API response (%d chars): %s", len(raw), raw[:150])

        data = json.loads(raw)
        tasks = data.get("tasks", [])

        valid = []
        for t in tasks:
            if (
                isinstance(t.get("name"), str)
                and isinstance(t.get("duration"), int)
                and t.get("priority") in _PRIORITIES
                and t.get("category") in _CATEGORIES
            ):
                valid.append(t)
            else:
                logger.warning("Dropping malformed task: %s", t)

        confidence = round(len(valid) / max(len(tasks), 1), 2) if tasks else 0.0
        logger.info("Parsed %d/%d valid tasks, confidence=%.2f", len(valid), len(tasks), confidence)
        return {"success": True, "tasks": valid, "confidence": confidence, "error": None}

    except json.JSONDecodeError as exc:
        logger.error("JSON parse failed: %s", exc)
        return {"success": False, "tasks": [], "confidence": 0.0, "error": "AI returned invalid JSON"}
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        return {"success": False, "tasks": [], "confidence": 0.0, "error": str(exc)}
