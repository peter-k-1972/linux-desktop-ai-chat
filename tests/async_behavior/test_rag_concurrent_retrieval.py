"""
Async Test: Konkurrente RAG-Retrieval-Aufrufe ohne Race.

Regression für INC-20260315-002 (async_race, RAG).
Verhindert: Race Condition bei parallelen augment_if_enabled-Aufrufen –
jeder Aufruf muss sein eigenes Ergebnis zurückgeben, keine Kreuzkontamination.
"""

import asyncio
import pytest

from app.rag.service import RAGService


class QuerySpecificPipeline:
    """
    Mock-Pipeline: Gibt query-spezifische Ergebnisse zurück.
    Gemeinsame Instanz für alle Aufrufe – bei async_race könnte Ergebnis
    von Aufruf A bei Aufruf B landen (shared state).
    """

    async def augment_prompt(self, user_prompt, top_k=None):
        await asyncio.sleep(0.02)  # Verzögerung für Race-Exposition
        return f"augmented:{user_prompt}", True


@pytest.mark.async_behavior
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rag_concurrent_augment_no_race():
    """
    Konkurrente augment_if_enabled-Aufrufe liefern jeweils korrektes Ergebnis.
    Regression INC-20260315-002: async_race in RAG-Subsystem.
    Verhindert: Kreuzkontamination bei parallelen Retrieval-Anfragen.
    """
    shared_pipeline = QuerySpecificPipeline()
    service = RAGService()
    service.get_pipeline = lambda **kw: shared_pipeline

    queries = [f"query_{i}" for i in range(10)]
    results = await asyncio.gather(
        *[
            service.augment_if_enabled(q, enabled=True, space="default", top_k=5)
            for q in queries
        ]
    )

    for i, (text, used) in enumerate(results):
        assert used is True, f"Aufruf {i}: rag_used muss True sein"
        assert f"augmented:{queries[i]}" == text, (
            f"Race: Aufruf {i} erwartete augmented:{queries[i]}, bekam {text}"
        )
