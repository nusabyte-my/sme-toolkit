import { useEffect } from "react";

export function useUnsavedChanges(dirty: boolean) {
  useEffect(() => {
    if (!dirty) return;
    const unload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    const navigate = (event: Event) => {
      if (!window.confirm("Leave this page and discard unsaved changes?"))
        event.preventDefault();
    };
    window.addEventListener("beforeunload", unload);
    window.addEventListener("sme-before-navigate", navigate);
    return () => {
      window.removeEventListener("beforeunload", unload);
      window.removeEventListener("sme-before-navigate", navigate);
    };
  }, [dirty]);
}
