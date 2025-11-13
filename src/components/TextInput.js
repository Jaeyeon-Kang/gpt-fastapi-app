import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import axios from 'axios';

export default function TextInput({ onNotification }) {
  const { t } = useTranslation();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [chunkSize, setChunkSize] = useState(512);
  const [chunkOverlap, setChunkOverlap] = useState(100);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const charCount = content.length;
  const maxChars = 1000000;

  const getCharCountColor = () => {
    if (charCount > maxChars * 0.8) return 'text-red-600';
    if (charCount > maxChars * 0.6) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      onNotification('문서 제목을 입력해주세요.', 'error');
      return;
    }

    if (!content.trim()) {
      onNotification('문서 내용을 입력해주세요.', 'error');
      return;
    }

    const contentSize = new Blob([content]).size;
    if (contentSize > 1024 * 1024) {
      onNotification('문서 내용이 너무 큽니다. 1MB 이하로 입력해주세요.', 'error');
      return;
    }

    setProcessing(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      formData.append('chunk_size', chunkSize);
      formData.append('chunk_overlap', chunkOverlap);

      const sessionId = typeof window !== 'undefined'
        ? (localStorage.getItem('session_id') || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now())))
        : String(Date.now());
      formData.append('session_id', sessionId);

      console.log('📝 [TextInput] Submitting text...');
      console.log('   Title:', title);
      console.log('   Content length:', content.length);
      console.log('   Session ID:', sessionId);

      const response = await axios.post('http://localhost:8000/add-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('✅ [TextInput] Response:', response.data);

      if (response.data.session_id && typeof window !== 'undefined') {
        localStorage.setItem('session_id', response.data.session_id);
        console.log('💾 [TextInput] Saved session ID:', response.data.session_id);
      }

      setResult(response.data);
      setTitle('');
      setContent('');
      onNotification('텍스트 추가 완료!', 'success');
    } catch (error) {
      console.error('❌ [TextInput] Text addition error:', error);
      onNotification('텍스트 추가 중 오류가 발생했습니다: ' + error.message, 'error');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <h3 className="text-2xl font-semibold text-gray-800 mb-4">📝 {t('text_title')}</h3>
      <p className="text-gray-600 mb-6">{t('text_desc')}</p>

      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 space-y-6">
        {/* Document Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('doc_title')}
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="문서의 제목을 입력하세요 (예: 인공지능 개요)"
            className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-primary-700 focus:outline-none"
          />
        </div>

        {/* Document Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('doc_content')}
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={t('content_placeholder')}
            rows={15}
            className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-primary-700 focus:outline-none resize-none"
          />
          <div className={`text-xs text-right mt-1 ${getCharCountColor()}`}>
            {charCount.toLocaleString()} / {maxChars.toLocaleString()} 글자
          </div>
        </div>

        {/* Upload Options */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                청크 크기는 텍스트를 나누는 덩어리의 크기입니다.
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
                청크 겹침은 청크 사이의 공통 구간 길이입니다.
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={processing}
          className="w-full px-6 py-3 bg-primary-700 text-white rounded-lg hover:bg-primary-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {processing ? t('processing') : t('add_text')}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="mt-6 p-6 bg-green-50 border border-green-300 rounded-lg">
          <h4 className="text-lg font-semibold text-green-800 mb-3">
            ✅ {t('text_added')}
          </h4>
          <div className="space-y-2 text-sm text-green-900">
            <p><strong>문서 제목:</strong> {result.title}</p>
            <p><strong>생성된 청크:</strong> {result.chunks_created}개</p>
            <p><strong>처리 시간:</strong> {result.processing_time}초</p>
            <p><strong>인덱스 크기:</strong> {result.index_size}MB</p>
          </div>
        </div>
      )}
    </div>
  );
}
