"use client";

import { useState } from "react";

export function useDocuments() {
  const [files, setFiles] = useState<File[]>([]);
  return { files, addFiles: (next: FileList | null) => next && setFiles((current) => [...current, ...Array.from(next)]) };
}
