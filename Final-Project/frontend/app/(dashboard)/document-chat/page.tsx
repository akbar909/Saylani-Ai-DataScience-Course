import { DocumentChat } from "../../../components/documents/DocumentChat";
import { DocumentUpload } from "../../../components/documents/DocumentUploader";

export default function DocumentChatPage() {
  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Knowledge workspace</span>
          <h1>Document chat</h1>
          <p>Upload documents and ask questions over the indexed content.</p>
        </div>
      </section>
      <article className="panel document-workspace">
        <DocumentUpload />
        <DocumentChat />
      </article>
    </div>
  );
}
