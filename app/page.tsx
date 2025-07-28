"use client";

import { useState, useRef } from "react";
import {
  Upload,
  FileText,
  Trash2,
  Pencil,
  Check,
  X,
  AlertCircle,
  Sparkle,
} from "lucide-react";

interface AnalysisResults {
  [key: string]: string;
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isCreatingDatabase, setIsCreatingDatabase] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] =
    useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    const pdfFiles = selectedFiles.filter(
      (file) => file.type === "application/pdf"
    );

    if (pdfFiles.length !== selectedFiles.length) {
      setError("Only PDF files are allowed");
      return;
    }

    setFiles(pdfFiles);
    setError(null);
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const response = await fetch("http://localhost:8000/upload-files", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Add new files to existing uploaded files, avoiding duplicates
        setUploadedFiles((prevFiles) => {
          const newFiles = data.files.filter(
            (file) => !prevFiles.includes(file)
          );
          return [...prevFiles, ...newFiles];
        });
        setFiles([]);
        setSuccess(`Successfully uploaded ${data.files.length} files`);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } else {
        setError(data.detail || "Upload failed");
      }
    } catch (err) {
      setError("Failed to upload files. Make sure the backend is running.");
    } finally {
      setIsUploading(false);
    }
  };

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/files");
      const data = await response.json();
      if (response.ok) {
        setUploadedFiles(data.files);
      }
    } catch (err) {
      console.error("Failed to fetch files:", err);
    }
  };

  const deleteFile = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000/files/${filename}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setUploadedFiles((files) => files.filter((f) => f !== filename));
        setSuccess(`File ${filename} deleted successfully`);
      } else {
        const data = await response.json();
        setError(data.detail || "Failed to delete file");
      }
    } catch (err) {
      setError("Failed to delete file");
    }
  };

  const createDatabase = async () => {
    setIsCreatingDatabase(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/create-database", {
        method: "POST",
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("Documents(s) processed successfully");
      } else {
        setError(data.detail || "Failed to create database");
      }
    } catch (err) {
      setError("Couldn't process document(s). Make sure the backend is running.");
    } finally {
      setIsCreatingDatabase(false);
    }
  };

  const analyzeDocuments = async () => {
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResults(null);

    try {
      const response = await fetch("http://localhost:8000/analyze-documents", {
        method: "POST",
      });

      const data = await response.json();

      if (response.ok) {
        setAnalysisResults(data.analysis_results);
        setSuccess("Document analysis completed successfully");
      } else {
        setError(data.detail || "Failed to analyze documents");
      }
    } catch (err) {
      setError(
        "Failed to analyze documents. Make sure the backend is running."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Load files on component mount
  useState(() => {
    fetchUploadedFiles();
  });

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black text-gray-100 font-mono">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 tracking-wider">
                BRIEFLY
              </h1>
            </div>
          </div>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed font-light tracking-wide">
            Next-generation AI-powered legal document analysis platform.
            <br />
            <span className="text-cyan-400 font-semibold">
              Upload. Process. Analyze.
            </span>
          </p>
          <div className="flex items-center justify-center mt-6 space-x-6">
            <div className="flex items-center text-sm text-gray-400">
              Secure Processing &mdash;&mdash; AI-Powered &mdash;&mdash; Smart
              Analysis
            </div>
          </div>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="mb-8 p-4 bg-red-900/30 border border-red-500/50 rounded-xl backdrop-blur-sm flex items-center">
            <span className="text-red-300 font-medium">{error}</span>
            <button
              onClick={clearMessages}
              className="ml-auto text-red-400 hover:text-red-300 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {success && (
          <div className="mb-8 p-4 bg-green-900/30 border border-green-500/50 rounded-xl backdrop-blur-sm flex items-center">
            <Check className="h-5 w-5 text-green-400 mr-3" />
            <span className="text-green-300 font-medium">{success}</span>
            <button
              onClick={clearMessages}
              className="ml-auto text-green-400 hover:text-green-300 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center tracking-wide">
                <Upload className="h-6 w-6 mr-3 text-blue-400" />
                UPLOAD DOCS
              </h2>

              <div className="space-y-6">
                <div className="relative">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-300 
                             file:mr-4 file:py-3 file:px-6 
                             file:rounded-full file:border-0 
                             file:text-sm file:font-bold
                             file:bg-gradient-to-r file:from-blue-600 file:to-purple-600
                             file:text-white file:shadow-lg
                             hover:file:from-blue-500 hover:file:to-purple-500
                             file:transition-all file:duration-300
                             file:cursor-pointer cursor-pointer"
                  />
                </div>

                {files.length > 0 && (
                  <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-700/30">
                    <p className="text-sm text-gray-400 mb-3 font-semibold uppercase tracking-wider">
                      Selected Files:
                    </p>
                    <ul className="space-y-2">
                      {files.map((file, index) => (
                        <li
                          key={index}
                          className="text-sm text-gray-300 flex items-center bg-gray-800/30 rounded-lg p-2"
                        >
                          <FileText className="h-4 w-4 mr-3 text-cyan-400" />
                          <span className="truncate">{file.name}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={uploadFiles}
                  disabled={files.length === 0 || isUploading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 
                           disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed
                           text-white py-4 px-6 rounded-xl transition-all duration-300 
                           flex items-center justify-center font-bold text-sm tracking-wide uppercase
                           shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {isUploading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Upload className="h-5 w-5 mr-2" />
                      Upload Files
                    </>
                  )}
                </button>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-bold text-white mb-4 uppercase tracking-wider">
                    Uploaded Files
                  </h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {uploadedFiles.map((filename, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-900/40 rounded-lg border border-gray-700/30 hover:border-gray-600/50 transition-all duration-200"
                      >
                        <span className="text-sm text-gray-300 flex items-center">
                          <FileText className="h-4 w-4 mr-3 text-cyan-400" />
                          <span className="truncate">{filename}</span>
                        </span>
                        <button
                          onClick={() => deleteFile(filename)}
                          className="text-red-400 hover:text-red-300 transition-colors p-1 hover:bg-red-900/20 rounded"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-8 space-y-4">
                <button
                  onClick={createDatabase}
                  disabled={uploadedFiles.length === 0 || isCreatingDatabase}
                  className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500
                           disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed
                           text-white py-4 px-6 rounded-xl transition-all duration-300 
                           flex items-center justify-center font-bold text-sm tracking-wide uppercase
                           shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {isCreatingDatabase ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Sparkle className="h-5 w-5 mr-2" />
                      Process Documents
                    </>
                  )}
                </button>

                <button
                  onClick={analyzeDocuments}
                  disabled={isAnalyzing}
                  className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500
                           disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed
                           text-white py-4 px-6 rounded-xl transition-all duration-300 
                           flex items-center justify-center font-bold text-sm tracking-wide uppercase
                           shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {isAnalyzing ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Pencil className="h-5 w-5 mr-2" />
                      Analyze Documents
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center tracking-wide">
                <FileText className="h-6 w-6 mr-3 text-cyan-400" />
                ANALYSIS RESULTS
              </h2>

              {!analysisResults && !isAnalyzing && (
                <div className="text-center py-16 text-gray-400">
                  <div className="relative">
                    {/* Weird exclamation circle */}
                    <AlertCircle className="h-16 w-16 mx-auto mb-6 opacity-30" />
                  </div>
                  <p className="text-lg font-light">
                    Awaiting document analysis...
                  </p>
                  <p className="text-sm mt-2 opacity-70">
                    Upload documents and run analysis to see results here.
                  </p>
                </div>
              )}

              {isAnalyzing && (
                <div className="text-center py-16">
                  <div className="relative mb-8">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-cyan-400 mx-auto"></div>
                    <div className="absolute inset-0 rounded-full border-4 border-gray-700/30"></div>
                  </div>
                  <p className="text-cyan-400 text-lg font-semibold mb-2">
                    Analyzing Documents...
                  </p>
                  <p className="text-gray-400 text-sm">
                    AI is processing your documents. This may take a few
                    minutes.
                  </p>
                </div>
              )}

              {analysisResults && (
                <div className="space-y-6">
                  {Object.entries(analysisResults).map(([field, value]) => (
                    <div
                      key={field}
                      className="border-b border-gray-700/50 pb-6 last:border-b-0"
                    >
                      <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wider flex items-center">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3"></div>
                        {field}
                      </h3>
                      <div className="text-gray-300 whitespace-pre-wrap bg-gray-900/40 p-6 rounded-xl border border-gray-700/30 font-mono text-sm leading-relaxed">
                        {value || (
                          <span className="text-gray-500 italic">Unknown</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(55, 65, 81, 0.3);
          border-radius: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(56, 189, 248, 0.5);
          border-radius: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(56, 189, 248, 0.7);
        }
      `}</style>
    </div>
  );
}
