import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Terminal } from "lucide-react";

const LOG_TYPES = [
  { key: "supervisor", label: "Supervisor" },
  { key: "app", label: "Aplicação" },
  { key: "critical", label: "Erros Críticos" },
];

export default function LogTerminal() {
  const [logType, setLogType] = useState("all");
  const [lines, setLines] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const API_URL =
    process.env.NEXT_PUBLIC_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "");

  async function fetchLog() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/preview-log/${logType}`);
      const data = await res.json();
      setLines(data.lines || []);
    } catch {
      setLines(["Erro ao carregar log."]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLog();
    // eslint-disable-next-line
  }, [logType]);

  return (
    <div className="rounded-lg border border-zinc-700 bg-gradient-to-br from-zinc-900 via-zinc-950 to-black p-0 shadow-lg max-h-80 overflow-hidden">
      <div className="flex flex-wrap items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-950 gap-2">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-green-400" />
          <span className="font-bold text-green-400 text-sm">
            Terminal de Logs
          </span>
        </div>
        <div className="flex flex-col gap-2 w-full sm:w-auto">
          <Button
            size="sm"
            variant="outline"
            onClick={fetchLog}
            disabled={loading}
          >
            {loading ? "Atualizando..." : "Atualizar"}
          </Button>
        </div>
      </div>
      <div
        className="overflow-y-auto px-4 py-2 font-mono text-xs text-green-300 custom-scrollbar resize-y rounded-md"
        style={{ minHeight: "12rem", maxHeight: "40rem", background: "transparent", width: "100%" }}
      >
        <pre style={{ whiteSpace: "pre-wrap", margin: 0, lineHeight: "1.4" }}>{lines.join("")}</pre>
      </div>
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #222;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .resize-y {
          resize: vertical;
        }
      `}</style>
    </div>
  );
}
