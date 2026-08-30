import { AgentChatWindow } from "../../../components/agent/AgentChatWindow";

export default function AgentPage() {
  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Pro workspace</span>
          <h1>AI agent</h1>
          <p>Ask about fraud risk, model health, or which parts of the workspace are ready.</p>
        </div>
      </section>
      <article className="panel">
        <AgentChatWindow />
      </article>
    </div>
  );
}
