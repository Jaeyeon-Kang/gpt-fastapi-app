import { useTranslation } from '@/hooks/useTranslation';

export default function Layout({ children }) {
  const { lang, changeLanguage, t } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">VectorMind</h1>
            <div className="flex gap-2">
              <button
                onClick={() => changeLanguage('ko')}
                className={`px-4 py-2 rounded text-sm transition ${
                  lang === 'ko'
                    ? 'bg-primary-700 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                한국어
              </button>
              <button
                onClick={() => changeLanguage('en')}
                className={`px-4 py-2 rounded text-sm transition ${
                  lang === 'en'
                    ? 'bg-primary-700 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                English
              </button>
            </div>
          </div>

          {/* Hero Section */}
          <div className="mb-8 p-6 bg-gradient-to-r from-purple-600 to-purple-800 text-white rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">{t('hero_title')}</h2>
            <p className="text-purple-100 leading-relaxed">{t('hero_description')}</p>
          </div>

          {/* Guide Section */}
          <div className="mb-8 p-6 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('guide_title')}</h3>
            <div className="space-y-2">
              <div className="text-sm text-gray-700">
                <strong className="text-blue-600">1</strong> {t('step1')}
              </div>
              <div className="text-sm text-gray-700">
                <strong className="text-blue-600">2</strong> {t('step2')}
              </div>
              <div className="text-sm text-gray-700">
                <strong className="text-blue-600">3</strong> {t('step3')}
              </div>
            </div>
          </div>

          {/* Main Content */}
          {children}
        </div>
      </div>
    </div>
  );
}
