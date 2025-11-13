import { useState, useEffect } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import axios from 'axios';

export default function FileStatusWidget({ onTabChange, onNotification, onFilesChange }) {
  const { t } = useTranslation();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const sessionId = typeof window !== 'undefined'
        ? (localStorage.getItem('session_id') || '')
        : '';

      console.log('🔍 [FileStatusWidget] Loading files...');
      console.log('   Session ID:', sessionId || '(none)');

      const response = await axios.get('http://localhost:8000/files', {
        params: { session_id: sessionId },
        headers: { 'X-Session-Id': sessionId },
      });

      console.log('📦 [FileStatusWidget] API Response:', response.data);
      console.log('   Files count:', response.data.files?.length || 0);
      console.log('   Files:', response.data.files);

      setFiles(response.data.files || []);
      if (onFilesChange) {
        onFilesChange(response.data.files || []);
      }
    } catch (error) {
      console.error('❌ [FileStatusWidget] Failed to load files:', error);
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const deleteFile = async (filename) => {
    if (!confirm(t('confirm_delete_file').replace('{filename}', filename))) {
      return;
    }

    try {
      const sessionId = typeof window !== 'undefined'
        ? (localStorage.getItem('session_id') || '')
        : '';

      await axios.delete(`http://localhost:8000/files/${encodeURIComponent(filename)}`, {
        headers: { 'X-Session-Id': sessionId },
      });

      onNotification(t('file_deleted_success'), 'success');
      await loadFiles();
    } catch (error) {
      onNotification(t('file_deleted_error'), 'error');
    }
  };

  const clearAllFiles = async () => {
    if (!confirm(t('confirm_clear_all'))) {
      return;
    }

    try {
      const sessionId = typeof window !== 'undefined'
        ? (localStorage.getItem('session_id') || '')
        : '';

      await axios.delete('http://localhost:8000/session', {
        headers: { 'X-Session-Id': sessionId },
      });

      if (typeof window !== 'undefined') {
        localStorage.removeItem('session_id');
      }

      onNotification(t('all_files_deleted'), 'success');
      await loadFiles();
    } catch (error) {
      onNotification(t('delete_failed'), 'error');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    return (bytes / 1024).toFixed(1) + ' KB';
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="mb-6 p-4 bg-gray-50 border-2 border-gray-200 rounded-lg">
        <p className="text-gray-500 text-center">{t('loading_files')}</p>
      </div>
    );
  }

  // Empty state
  if (files.length === 0) {
    return (
      <div className="mb-6 p-6 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-3">⚠️</div>
          <h3 className="text-yellow-800 font-bold text-lg mb-2">
            {t('no_files_uploaded')}
          </h3>
          <p className="text-yellow-700 mb-4">{t('upload_files_first')}</p>
          <button
            onClick={() => onTabChange('upload')}
            className="bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            📤 {t('go_to_upload')}
          </button>
        </div>
      </div>
    );
  }

  // Compact mode
  if (!expanded) {
    const fileNames = files.map(f => f.name).join(', ');
    const totalSize = files.reduce((sum, f) => sum + (f.size || 0), 0);
    const totalChunks = files.reduce((sum, f) => sum + (f.chunks || 0), 0);

    return (
      <div className="mb-6 p-4 bg-green-50 border-2 border-green-300 rounded-lg">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h3 className="text-green-800 font-bold">
                📂 {t('search_target_docs')} ({files.length}{t('count_unit')})
              </h3>
              <span className="text-green-600 text-sm">
                {t('total')}: {formatFileSize(totalSize)} · {totalChunks} {t('chunks')}
              </span>
            </div>
            <p className="text-green-700 text-sm truncate" title={fileNames}>
              {fileNames}
            </p>
          </div>
          <button
            onClick={() => setExpanded(true)}
            className="text-green-700 hover:text-green-900 font-medium text-sm whitespace-nowrap flex-shrink-0"
          >
            ▼ {t('expand')}
          </button>
        </div>
      </div>
    );
  }

  // Expanded mode
  return (
    <div className="mb-6 bg-green-50 border-2 border-green-300 rounded-lg">
      <div className="p-4 flex items-center justify-between border-b-2 border-green-200">
        <h3 className="text-green-800 font-bold">
          📂 {t('search_target_docs')} ({files.length}{t('count_unit')})
        </h3>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setExpanded(false)}
            className="text-green-700 hover:text-green-900 font-medium text-sm"
          >
            ▲ {t('collapse')}
          </button>
        </div>
      </div>

      <div className="p-4 space-y-2">
        {files.map((file, index) => (
          <div
            key={index}
            className="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors flex items-center justify-between"
          >
            <div className="flex-1">
              <div className="font-medium text-gray-900">📄 {file.name}</div>
              <div className="text-sm text-gray-500 mt-1">
                {formatFileSize(file.size)} · {file.chunks || 0} {t('chunks')} · {formatDate(file.uploaded_at)}
              </div>
            </div>
            <button
              onClick={() => deleteFile(file.name)}
              className="ml-4 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="p-4 border-t-2 border-green-200 flex gap-2">
        <button
          onClick={() => onTabChange('upload')}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          + {t('add_more_files')}
        </button>
        <button
          onClick={clearAllFiles}
          className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {t('clear_all')}
        </button>
      </div>
    </div>
  );
}
