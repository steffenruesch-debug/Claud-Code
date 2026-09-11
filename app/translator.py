"""Uebersetzung von Transkripten via GPT-Modell."""
from openai import OpenAI

from app.config import TRANSLATE_MODEL

_LANGUAGE_NAMES = {
    "de": "Deutsch",
    "en": "Englisch",
}

_SYSTEM_PROMPT = (
    "Du bist ein professioneller Uebersetzer fuer Video-Transkripte. "
    "Uebersetze den gegebenen Text originalgetreu in die Zielsprache. "
    "Erhalte den Sinn, den Ton und die Aussage exakt, formuliere aber "
    "natuerlich in der Zielsprache. Gib ausschliesslich die Uebersetzung "
    "zurueck, ohne Einleitung, Anmerkungen oder Anfuehrungszeichen."
)


def translate(text: str, target_lang: str, client: OpenAI) -> str:
    """Uebersetzt `text` nach target_lang ('de' oder 'en')."""
    if not text.strip():
        return ""

    target_name = _LANGUAGE_NAMES.get(target_lang, target_lang)
    response = client.chat.completions.create(
        model=TRANSLATE_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Zielsprache: {target_name}\n\nText:\n{text}",
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
