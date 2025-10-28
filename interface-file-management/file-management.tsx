"use client";

import React, { useState, useEffect } from "react";
import {
  Upload,
  RefreshCw,
  Check,
  Clock,
  Server,
  FileText,
  X as XIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import LogTerminal from "@/components/ui/LogTerminal";

type FileStatus = "server" | "waiting" | "pending-approval";

interface FileItem {
  id: string;
  name: string;
  size: string;
  status: FileStatus;
  uploadDate?: string;
  fileObject?: File;
}

export default function FileManagement() {
  const [serverFiles, setServerFiles] = useState<FileItem[]>([]);
  const [waitingFiles, setWaitingFiles] = useState<FileItem[]>([]);
  const [pendingApproval, setPendingApproval] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState({ server: false, pending: false });
  const [isUploading, setIsUploading] = useState(false);

  // resolve API_URL: primeiro env, depois host atual
  const API_URL =
    process.env.NEXT_PUBLIC_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "");

  async function loadServerFiles() {
    setIsLoading((prev) => ({ ...prev, server: true }));
    try {
      const res = await fetch(`${API_URL}/files?type=media`);
      const data = await res.json();
      const items = data.media_data.map((name: string) => ({
        id: name,
        name,
        size: "-",
        status: "server" as FileStatus,
        uploadDate: "-",
      }));
      setServerFiles(items);
    } finally {
      setIsLoading((prev) => ({ ...prev, server: false }));
    }
  }

  async function loadPending() {
    setIsLoading((prev) => ({ ...prev, pending: true }));
    try {
      const res = await fetch(`${API_URL}/files?type=upload`);
      const data = await res.json();
      const items = data.upload_files.map((name: string) => ({
        id: name,
        name,
        size: "-",
        status: "pending-approval" as FileStatus,
        uploadDate: "-",
      }));
      setPendingApproval(items);
    } finally {
      setIsLoading((prev) => ({ ...prev, pending: false }));
    }
  }

  useEffect(() => {
    loadServerFiles();
    loadPending();
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const arr = Array.from(files).map((file, idx) => ({
      id: `waiting-${Date.now()}-${idx}`,
      name: file.name,
      size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
      status: "waiting" as FileStatus,
      fileObject: file,
    }));
    setWaitingFiles((prev) => [...prev, ...arr]);
    e.target.value = "";
  };

  const removeFromWaiting = (id: string) => {
    setWaitingFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const sendFiles = async () => {
    if (waitingFiles.length === 0) return;
    setIsUploading(true);
    try {
      for (const item of waitingFiles) {
        const form = new FormData();
        form.append("file", item.fileObject as Blob);
        await fetch(`${API_URL}/upload`, { method: "POST", body: form });
      }
      await loadPending();
      setWaitingFiles([]);
    } finally {
      setIsUploading(false);
    }
  };

  const processAll = async (approve: boolean) => {
    for (const file of pendingApproval) {
      await fetch(`${API_URL}/files/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, approve }),
      });
    }
    await Promise.all([loadPending(), loadServerFiles()]);
  };

  const getStatusBadge = (status: FileStatus) => {
    switch (status) {
      case "server":
        return (
          <Badge
            variant="default"
            className="bg-green-100 text-green-700 text-xs"
          >
            <Server className="w-3 h-3 mr-1" />
            <span className="hidden sm:inline">Servidor</span>
          </Badge>
        );
      case "waiting":
        return (
          <Badge variant="secondary" className="text-xs">
            <Clock className="w-3 h-3 mr-1" />
            <span className="hidden sm:inline">Aguardando</span>
          </Badge>
        );
      case "pending-approval":
        return (
          <Badge
            variant="outline"
            className="border-orange-200 text-orange-700 text-xs"
          >
            <Clock className="w-3 h-3 mr-1" />
            <span className="hidden sm:inline">Pendente</span>
          </Badge>
        );
    }
  };

  // Função para baixar logs via fetch+Blob
  async function downloadLog(type: "supervisor" | "app" | "critical") {
    try {
      const res = await fetch(`${API_URL}/download-log/${type}`);
      if (!res.ok) throw new Error("Falha ao baixar log");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Erro ao baixar log!");
    }
  }

  // Função para baixar métricas via fetch+Blob
  async function handleDownloadMetrics() {
    try {
      const res = await fetch(`${API_URL}/api/metrics/download`);
      if (!res.ok) throw new Error("Falha ao baixar métricas");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "metrics_envio.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Erro ao baixar métricas!");
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6 max-w-4xl">
      <div className="text-center space-y-1">
        <h1 className="text-2xl md:text-3xl font-bold">
          Gerenciamento de Arquivos
        </h1>
        <p className="text-sm text-muted-foreground">
          Gerencie uploads, aprovações e arquivos do servidor
        </p>
      </div>

      {/* Arquivos no Servidor */}
      <Card>
        <CardHeader className="flex items-center justify-between pb-3">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Server className="w-4 h-4 text-green-600" />
              Arquivos no Servidor
            </CardTitle>
            <CardDescription className="text-xs">
              Arquivos já aprovados e disponíveis
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={loadServerFiles}
            disabled={isLoading.server}
          >
            <RefreshCw
              className={`w-3 h-3 mr-1 ${
                isLoading.server ? "animate-spin" : ""
              }`}
            />
            <span className="hidden sm:inline">Atualizar</span>
          </Button>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="max-h-64 overflow-y-auto space-y-2">
            {serverFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-2 border rounded-lg bg-green-50/50"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="w-4 h-4 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p
                      className="font-medium text-sm truncate"
                      title={file.name}
                    >
                      {file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">{file.size}</p>
                  </div>
                </div>
                {getStatusBadge(file.status)}
              </div>
            ))}
            {serverFiles.length === 0 && (
              <p className="text-center py-6 text-sm text-muted-foreground">
                Nenhum arquivo no servidor
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Lista de Espera */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Upload className="w-4 h-4 text-blue-600" />
            Lista de Espera
          </CardTitle>
          <CardDescription className="text-xs">
            Adicione arquivos para envio
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 pt-0">
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center hover:border-blue-300 transition-colors">
            <Input
              id="file-upload"
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="w-6 h-6 mx-auto mb-1" />
              <p className="text-xs text-muted-foreground">
                Clique para selecionar arquivos
              </p>
            </label>
          </div>

          <div className="space-y-2">
            {waitingFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-2 border rounded-lg bg-blue-50/50"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="w-4 h-4 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p
                      className="font-medium text-sm truncate"
                      title={file.name}
                    >
                      {file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">{file.size}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {getStatusBadge(file.status)}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFromWaiting(file.id)}
                    className="h-7 w-7 p-0"
                  >
                    <XIcon className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
            {waitingFiles.length === 0 && (
              <p className="text-center py-3 text-sm text-muted-foreground">
                Nenhum arquivo na lista de espera
              </p>
            )}
          </div>

          <Button
            onClick={sendFiles}
            disabled={waitingFiles.length === 0 || isUploading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-sm"
          >
            {isUploading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Enviar {waitingFiles.length > 0 && `(${waitingFiles.length})`}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      <Separator />

      {/* Aprovações Pendentes */}
      <Card>
        <CardHeader className="flex items-center justify-between pb-3">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Clock className="w-4 h-4 text-orange-600" />
              Aprovações Pendentes
            </CardTitle>
            <CardDescription className="text-xs">
              Arquivos aguardando aprovação
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={loadPending}
            disabled={isLoading.pending}
          >
            <RefreshCw
              className={`w-3 h-3 mr-1 ${
                isLoading.pending ? "animate-spin" : ""
              }`}
            />
            <span className="hidden sm:inline">Atualizar</span>
          </Button>
        </CardHeader>
        <CardContent className="space-y-3 pt-0">
          <div className="max-h-64 overflow-y-auto space-y-2">
            {pendingApproval.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-2 border rounded-lg bg-orange-50/50"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="w-4 h-4 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p
                      className="font-medium text-sm truncate"
                      title={file.name}
                    >
                      {file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">{file.size}</p>
                  </div>
                </div>
                {getStatusBadge(file.status)}
              </div>
            ))}
            {pendingApproval.length === 0 && (
              <p className="text-center py-6 text-sm text-muted-foreground">
                Nenhuma aprovação pendente
              </p>
            )}
          </div>
          {pendingApproval.length > 0 && (
            <div className="flex flex-col sm:flex-row gap-2">
              <Button
                onClick={() => processAll(true)}
                className="flex-1 bg-green-600 hover:bg-green-700 text-sm"
              >
                <Check className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Aprovar Todos</span>
                <span className="sm:hidden">Aprovar</span>
                <span className="ml-1">({pendingApproval.length})</span>
              </Button>
              <Button
                onClick={() => processAll(false)}
                variant="destructive"
                className="flex-1 text-sm"
              >
                <XIcon className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Reprovar Todos</span>
                <span className="sm:hidden">Reprovar</span>
                <span className="ml-1">({pendingApproval.length})</span>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logs do Sistema */}
      <Card>
        <CardHeader>
          <CardTitle>Logs do Sistema</CardTitle>
          <CardDescription>
            Baixe os logs individuais do sistema para análise ou suporte.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4 flex-wrap">
            <Button variant="outline" onClick={() => downloadLog("supervisor")}>
              Baixar Supervisor
            </Button>
            <Button variant="outline" onClick={() => downloadLog("app")}>
              Baixar Aplicação
            </Button>
            <Button variant="outline" onClick={() => downloadLog("critical")}>
              Baixar Erros Críticos
            </Button>
            <Button variant="outline" onClick={handleDownloadMetrics}>
              Baixar Métricas
            </Button>
          </div>
          <LogTerminal />
        </CardContent>
      </Card>

      <div className="flex gap-2 mt-2"></div>
    </div>
  );
}
