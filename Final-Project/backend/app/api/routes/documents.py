from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.document import UploadedDocument
from app.models.user import User
from app.rag.chat import answer_question
from app.rag.ingest import chunk_text, extract_text
from app.rag.retriever import Retriever
from app.schemas.document import Citation, DocumentAnswer, DocumentQuestion, DocumentRead


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    settings = get_settings()
    upload_root = settings.upload_root
    upload_root.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename).suffix
    unique_name = f"{uuid4().hex}{extension}"
    target_path = upload_root / unique_name

    try:
        contents = await file.read()
        target_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to store file: {exc}")

    document = await UploadedDocument(
        organization_id=current_user.organization_id,
        filename=file.filename,
        file_path=str(target_path),
        file_url=f"/uploads/{unique_name}",
        uploaded_by=current_user.email,
        status="indexed",
    ).insert()
    return DocumentRead(
        id=str(document.id),
        filename=document.filename,
        status=document.status,
        created_at=document.created_at,
        file_url=document.file_url,
    )


@router.get("", response_model=list[DocumentRead])
async def list_documents(current_user: User = Depends(get_current_user)) -> list[DocumentRead]:
    return [
        DocumentRead(
            id=str(document.id),
            filename=document.filename,
            status=document.status,
            created_at=document.created_at,
            file_url=document.file_url,
        )
        for document in await UploadedDocument.find().sort("-created_at").to_list()
    ]


@router.post("/chat", response_model=DocumentAnswer)
async def document_chat(payload: DocumentQuestion, current_user: User = Depends(get_current_user)) -> DocumentAnswer:
    document = await UploadedDocument.get(payload.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "indexed":
        return DocumentAnswer(
            answer="Document is still being processed. Please wait until indexing is complete.",
            citations=[],
        )

    # Extract real text from the uploaded file
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Uploaded file not found on disk: {file_path}")

    full_text = extract_text(file_path)
    if not full_text.strip() or full_text.startswith("[Could not"):
        return DocumentAnswer(
            answer=f"Could not extract text from '{document.filename}'. {full_text}",
            citations=[],
        )

    # Chunk and retrieve relevant passages
    chunks = chunk_text(full_text, chunk_size=1000)
    retriever = Retriever(chunks)

    # Generate answer via Gemini
    result = await answer_question(payload.question, retriever)
    citations = [
        Citation(chunk_text=c["chunk_text"], page=c["page"], score=c["score"])  # type: ignore[arg-type]
        for c in result["citations"]  # type: ignore[index]
    ]
    return DocumentAnswer(answer=str(result["answer"]), citations=citations)
