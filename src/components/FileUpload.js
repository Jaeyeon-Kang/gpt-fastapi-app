import { useState, useRef } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import axios from 'axios';

export default function FileUpload({ onNotification }) {
  const { t } = useTranslation();
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [chunkSize, setChunkSize] = useState(512);
  const [chunkOverlap, setChunkOverlap] = useState(100);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (files) => {
    setSelectedFiles(Array.from(files));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeFile = (index) => {
    const newFiles = [...selectedFiles];
    newFiles.splice(index, 1);
    setSelectedFiles(newFiles);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      onNotification('업로드할 파일을 선택해주세요.', 'error');
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('chunk_size', chunkSize);
      formData.append('chunk_overlap', chunkOverlap);

      const sessionId = typeof window !== 'undefined'
        ? (localStorage.getItem('session_id') || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now())))
        : String(Date.now());
      formData.append('session_id', sessionId);

      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.session_id && typeof window !== 'undefined') {
        localStorage.setItem('session_id', response.data.session_id);
      }

      setUploadResult(response.data);
      setSelectedFiles([]);
      onNotification('파일 업로드 완료!', 'success');
    } catch (error) {
      console.error('Upload error:', error);
      onNotification('업로드 중 오류가 발생했습니다: ' + error.message, 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h3 className="text-2xl font-semibold text-gray-800 mb-4">{t('upload_title')}</h3>
      <p className="text-gray-600 mb-6">{t('upload_desc')}</p>

      {/* Drop Zone */}
      <div
        onClick={() => fileInputRef.current.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-4 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
          dragOver
            ? 'border-green-500 bg-green-50'
            : 'border-blue-400 bg-blue-50 hover:bg-blue-100'
        }`}
      >
        <div className="text-6xl mb-4">📄</div>
        <p className="text-lg text-gray-700 mb-2">{t('file_drop')}</p>
        <p className="text-sm text-gray-500">{t('supported_formats')}</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".txt,.pdf,.docx,.csv"
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
      />

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-3">{t('selected_files')}</h4>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-white p-3 rounded border">
                <div>
                  <span className="font-medium text-gray-700">{file.name}</span>
                  <span className="text-gray-500 text-sm ml-3">({formatFileSize(file.size)})</span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-sm"
                >
                  삭제
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('chunk_size')}
          </label>
          <select
            value={chunkSize}
            onChange={(e) => setChunkSize(Number(e.target.value))}
            className="w-full p-2 border border-gray-300 rounded focus:border-primary-700 focus:outline-none"
          >
            <option value={256}>256</option>
            <option value={512}>512</option>
            <option value={1024}>1024</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            청크 크기는 텍스트를 얼마나 큰 덩어리로 나눌지 결정합니다.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('chunk_overlap')}
          </label>
          <select
            value={chunkOverlap}
            onChange={(e) => setChunkOverlap(Number(e.target.value))}
            className="w-full p-2 border border-gray-300 rounded focus:border-primary-700 focus:outline-none"
          >
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            청크 겹침은 이전 청크의 끝부분을 다음 청크 앞에 일부 겹쳐 넣는 값입니다.
          </p>
        </div>
      </div>

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={selectedFiles.length === 0 || uploading}
        className="w-full px-6 py-3 bg-primary-700 text-white rounded-lg hover:bg-primary-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {uploading ? t('processing') : t('upload_button')}
      </button>

      {/* Upload Result */}
      {uploadResult && (
        <div className="mt-6 p-6 bg-green-50 border border-green-300 rounded-lg">
          <h4 className="text-lg font-semibold text-green-800 mb-3">
            ✅ {t('upload_done')}
          </h4>
          <div className="space-y-2 text-sm text-green-900">
            <p><strong>업로드된 파일:</strong> {uploadResult.files_processed}개</p>
            <p><strong>생성된 청크:</strong> {uploadResult.chunks_created}개</p>
            <p><strong>처리 시간:</strong> {uploadResult.processing_time}초</p>
            <p><strong>인덱스 크기:</strong> {uploadResult.index_size}MB</p>
          </div>
        </div>
      )}
    </div>
  );
}
