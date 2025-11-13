import { useState, useEffect } from 'react';
import { translations } from '@/lib/i18n';

export function useTranslation() {
  const [lang, setLang] = useState('ko');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('language') || 'ko';
      setLang(savedLang);
    }
  }, []);

  const changeLanguage = (newLang) => {
    setLang(newLang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('language', newLang);
    }
  };

  const t = (key) => {
    return translations[lang]?.[key] || key;
  };

  return { lang, changeLanguage, t, mounted };
}
