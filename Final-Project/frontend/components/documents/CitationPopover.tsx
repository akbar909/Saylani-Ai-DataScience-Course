export function CitationPopover({ page, text }: { page: number; text: string }) { return <span className="citation" title={text}>Source p. {page}</span>; }
