'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, Play, Trash2, Database, Brain, Check, X, AlertCircle } from 'lucide-react';

interface AnalysisResults {
  [key: string]: string;
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isCreatingDatabase, setIsCreatingDatabase] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== selectedFiles.length) {
      setError('Only PDF files are allowed');
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
      files.forEach(file => formData.append('files', file));
      
      const response = await fetch('http://localhost:8000/upload-files', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setUploadedFiles(data.files);
        setFiles([]);
        setSuccess(`Successfully uploaded ${data.files.length} files`);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setError(data.detail || 'Upload failed');
      }
    } catch (err) {
      setError('Failed to upload files. Make sure the backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/files');
      const data = await response.json();
      if (response.ok) {
        setUploadedFiles(data.files);
      }
    } catch (err) {
      console.error('Failed to fetch files:', err);
    }
  };

  const deleteFile = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000/files/${filename}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setUploadedFiles(files => files.filter(f => f !== filename));
        setSuccess(`File ${filename} deleted successfully`);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to delete file');
      }
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  const createDatabase = async () => {
    setIsCreatingDatabase(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/create-database', {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccess('Database created/updated successfully');
      } else {
        setError(data.detail || 'Failed to create database');
      }
    } catch (err) {
      setError('Failed to create database. Make sure the backend is running.');
    } finally {
      setIsCreatingDatabase(false);
    }
  };

  const analyzeDocuments = async () => {
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResults(null);
    
    try {
      const response = await fetch('http://localhost:8000/analyze-documents', {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setAnalysisResults(data.analysis_results);
        setSuccess('Document analysis completed successfully');
      } else {
        setError(data.detail || 'Failed to analyze documents');
      }
    } catch (err) {
      setError('Failed to analyze documents. Make sure the backend is running.');
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Briefly
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered legal document analysis tool for paralegals. Upload PDF documents and extract key information automatically.
          </p>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <X className="h-5 w-5 text-red-500 mr-3" />
            <span className="text-red-700">{error}</span>
            <button onClick={clearMessages} className="ml-auto text-red-500 hover:text-red-700">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
            <Check className="h-5 w-5 text-green-500 mr-3" />
            <span className="text-green-700">{success}</span>
            <button onClick={clearMessages} className="ml-auto text-green-500 hover:text-green-700">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Upload className="h-5 w-5 mr-2" />
                Upload Documents
              </h2>
              
              <div className="space-y-4">
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>

                {files.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Selected files:</p>
                    <ul className="space-y-1">
                      {files.map((file, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          {file.name}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={uploadFiles}
                  disabled={files.length === 0 || isUploading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-md transition-colors flex items-center justify-center"
                >
                  {isUploading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Files
                    </>
                  )}
                </button>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Uploaded Files</h3>
                  <ul className="space-y-2">
                    {uploadedFiles.map((filename, index) => (
                      <li key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700 flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          {filename}
                        </span>
                        <button
                          onClick={() => deleteFile(filename)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-6 space-y-3">
                <button
                  onClick={createDatabase}
                  disabled={uploadedFiles.length === 0 || isCreatingDatabase}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-md transition-colors flex items-center justify-center"
                >
                  {isCreatingDatabase ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Database className="h-4 w-4 mr-2" />
                      Create Database
                    </>
                  )}
                </button>

                <button
                  onClick={analyzeDocuments}
                  disabled={isAnalyzing}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-md transition-colors flex items-center justify-center"
                >
                  {isAnalyzing ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      Analyze Documents
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Analysis Results
              </h2>

              {!analysisResults && !isAnalyzing && (
                <div className="text-center py-12 text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No analysis results yet. Upload documents and run analysis to see results here.</p>
                </div>
              )}

              {isAnalyzing && (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Analyzing documents... This may take a few minutes.</p>
                </div>
              )}

              {analysisResults && (
                <div className="space-y-6">
                  {Object.entries(analysisResults).map(([field, value]) => (
                    <div key={field} className="border-b border-gray-200 pb-4 last:border-b-0">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">{field}</h3>
                      <div className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded-md">
                        {value || 'Unknown'}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}