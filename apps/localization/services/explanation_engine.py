class ExplanationEngine:
    def _build_idiom_replacements(self, idiom_adaptation):
        matches = (idiom_adaptation or {}).get("matches", [])
        return [
            {
                "original": match.get("original", ""),
                "replacement": match.get("replacement", ""),
                "strategy": match.get("strategy", "rule-based"),
                "semantic_preservation": "maintained",
            }
            for match in matches
        ]

    def _build_tone_changes(self, selected_tone, base_explanation, variations):
        base_tone_notes = [
            note for note in (base_explanation or [])
            if note.get("type") in {"tone", "audience", "diversity"}
        ]

        variation_tone_notes = []
        for item in variations or []:
            notes = [
                note for note in item.get("explanation", [])
                if note.get("type") in {"tone", "diversity"}
            ]
            variation_tone_notes.append(
                {
                    "variant": item.get("variant_name", ""),
                    "changes": notes,
                }
            )

        return {
            "selected_tone": selected_tone,
            "base_changes": base_tone_notes,
            "variant_changes": variation_tone_notes,
        }

    def _build_cultural_adaptations(self, cultural_review, target_region):
        review = cultural_review or {}
        return {
            "target_region": target_region,
            "risk_score": review.get("score", 0),
            "flags": review.get("flags", []),
            "recommendations": review.get("recommendations", []),
        }

    def build(self, selected_tone, target_region, idiom_adaptation, cultural_review, base_explanation, variations):
        idiom_replacements = self._build_idiom_replacements(idiom_adaptation)
        tone_changes = self._build_tone_changes(selected_tone, base_explanation, variations)
        cultural_adaptations = self._build_cultural_adaptations(cultural_review, target_region)

        return {
            "idiom_replacements": idiom_replacements,
            "tone_changes": tone_changes,
            "cultural_adaptations": cultural_adaptations,
            "summary": {
                "idiom_replacements_count": len(idiom_replacements),
                "tone_change_notes_count": len(tone_changes.get("base_changes", [])),
                "cultural_flags_count": len(cultural_adaptations.get("flags", [])),
            },
        }
