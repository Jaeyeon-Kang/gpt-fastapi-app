import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import axios from 'axios';

export default function RAGSearch({ onNotification }) {
  const { t } = useTranslation();
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(3);
  const [temperature, setTemperature] = useState(0.7);
  const [systemPrompt, setSystemPrompt] = useState('다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요.');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  const handleSubmit = async () => {
    if (!question.trim()) {
      onNotification(t('question_placeholder'), 'error');
      return;
    }

    setLoading(true);
    setResponse(null);

    try {
      const sessionId = typeof window !== 'undefined' ? (localStorage.getItem('session_id') || '') : '';
      const startTime = Date.now();

      const res = await fetch('http://localhost:8000/search-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Id': sessionId,
        },
        body: JSON.stringify({
          question,
          top_k: topK,
          temperature,
          system_prompt: systemPrompt,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let chunks = [];
      let answer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'chunks') {
              chunks = data.chunks;
            } else if (data.type === 'token') {
              answer += data.content;
              // Update UI in real-time
              setResponse({
                answer,
                chunks,
                metrics: {
                  responseTime: Date.now() - startTime,
                  topK,
                  temperature,
                },
              });
            } else if (data.type === 'error') {
              throw new Error(data.message);
            }
          }
        }
      }

      const responseTime = Date.now() - startTime;
      setResponse({
        answer,
        chunks,
        metrics: {
          responseTime,
          topK,
          temperature,
        },
      });
    } catch (error) {
      console.error('Error:', error);
      onNotification('오류가 발생했습니다: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('session_id');
    }
    onNotification('세션이 초기화되었습니다.', 'info');
  };

  return (
    <div>
      {/* Question Input */}
      <div className="mb-6">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={t('question_placeholder')}
          rows={4}
          className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-primary-700 focus:outline-none resize-none"
        />
      </div>

      {/* Advanced Settings */}
      <div className="mb-6">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition text-sm"
        >
          {showAdvanced ? t('hide_advanced') : t('advanced_settings')}
        </button>

        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('doc_count')}
              </label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded focus:border-primary-700 focus:outline-none"
              >
                <option value={3}>3개</option>
                <option value={5}>5개</option>
                <option value={8}>8개</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('answer_style')}
              </label>
              <select
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded focus:border-primary-700 focus:outline-none"
              >
                <option value={0.2}>{t('concise')}</option>
                <option value={0.5}>{t('balanced')}</option>
                <option value={0.8}>{t('creative')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('ai_role')}
              </label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder={t('ai_role_placeholder')}
                rows={2}
                className="w-full p-2 border border-gray-300 rounded focus:border-primary-700 focus:outline-none resize-none text-sm"
              />
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="px-6 py-3 bg-primary-700 text-white rounded-lg hover:bg-primary-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? t('loading') : t('ask_button')}
        </button>
        <button
          onClick={handleResetSession}
          className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition"
        >
          {t('reset_session')}
        </button>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="text-center text-gray-600 italic py-4">
          {t('loading')}
        </div>
      )}

      {/* Response Section */}
      {response && (
        <div className="space-y-6">
          {/* GPT Answer */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 pb-2 border-b-2 border-primary-700">
              {t('gpt_answer')}
            </h3>
            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
              {response.answer}
            </div>
            <div className="flex gap-4 mt-4 text-sm">
              <div className="bg-gray-200 px-3 py-1 rounded">
                응답 시간: {response.metrics.responseTime}ms
              </div>
              <div className="bg-gray-200 px-3 py-1 rounded">
                Top-k: {response.metrics.topK}
              </div>
              <div className="bg-gray-200 px-3 py-1 rounded">
                Temperature: {response.metrics.temperature}
              </div>
            </div>
          </div>

          {/* Referenced Documents */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 pb-2 border-b-2 border-primary-700">
              {t('referenced_docs')}
            </h3>
            <div className="space-y-3">
              {response.chunks.map((chunk, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="bg-primary-700 text-white px-3 py-1 rounded-full text-xs font-bold">
                      #{chunk.rank}
                    </span>
                    <span className="text-gray-500 text-xs">
                      거리: {chunk.distance.toFixed(4)}
                    </span>
                  </div>
                  <div className="text-gray-700 leading-relaxed text-sm">
                    {chunk.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
