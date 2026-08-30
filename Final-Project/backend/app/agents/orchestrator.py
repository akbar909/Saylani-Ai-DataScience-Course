from typing import Any

from app.agents.memory import AgentMemory
from app.core.model_registry import ModelRegistry


class FinanceAgent:
    def __init__(self, registry: ModelRegistry | None = None, memory: AgentMemory | None = None) -> None:
        self.memory = memory or AgentMemory()
        self.registry = registry

    async def answer(self, message: str) -> str:
        self.memory.add("user", message)
        prompt = message.lower()

        if "credit" in prompt or "card" in prompt:
            answer = self._credit_summary()
        elif "paysim" in prompt or "sim" in prompt:
            answer = self._paysim_summary()
        elif "forecast" in prompt or "revenue" in prompt or "expense" in prompt:
            answer = "Forecasting is pending training. Check the forecasting readiness page to see whether forecasts are available."
        elif "report" in prompt or "dashboard" in prompt:
            answer = "Your workspace has fraud model health available, plus transaction and signal summaries from the overview endpoint."
        else:
            answer = self._workspace_summary()

        self.memory.add("assistant", answer)
        return answer

    def _metrics(self, artifact_name: str) -> dict[str, Any]:
        if self.registry is None:
            return {}
        artifact = self.registry.load(artifact_name)
        return artifact.metrics

    def _format_metric(self, value: Any) -> str:
        return f"{value:.3f}" if isinstance(value, (float, int)) else str(value)

    def _credit_summary(self) -> str:
        metrics = self._metrics("creditcard_baseline")
        if not metrics:
            return "Credit-card fraud detection is available, but detailed metrics are not loaded yet."
        return (
            "Credit-card fraud detection is online. "
            f"The baseline model has ROC-AUC {self._format_metric(metrics.get('roc_auc'))} "
            f"and recall {self._format_metric(metrics.get('recall'))}."
        )

    def _paysim_summary(self) -> str:
        metrics = self._metrics("paysim_baseline")
        if not metrics:
            return "PaySim fraud detection is available, but detailed metrics are not loaded yet."
        return (
            "PaySim fraud detection is online. "
            f"The baseline model has ROC-AUC {self._format_metric(metrics.get('roc_auc'))} "
            f"and recall {self._format_metric(metrics.get('recall'))}."
        )

    def _workspace_summary(self) -> str:
        return (
            "The finance workspace is connected to fraud model artifacts and ready to accept questions about model health, risk scores, and operational signals. "
            "Forecasting and full document retrieval are available as soon as their training and ingest pipelines are configured."
        )
