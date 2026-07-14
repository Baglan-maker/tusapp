import * as Localization from 'expo-localization';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import kk from './kk.json';
import ru from './ru.json';

export type AppLocale = 'ru' | 'kk';

/** Kazakh if the device says so, Russian otherwise. The onboarding's first
 * screen lets the user override it, and that choice is saved to the profile. */
function deviceLocale(): AppLocale {
  const tag = Localization.getLocales()[0]?.languageCode ?? 'ru';
  return tag === 'kk' ? 'kk' : 'ru';
}

void i18n.use(initReactI18next).init({
  resources: { ru: { translation: ru }, kk: { translation: kk } },
  lng: deviceLocale(),
  fallbackLng: 'ru',
  interpolation: { escapeValue: false },
});

export function setLocale(locale: AppLocale): void {
  void i18n.changeLanguage(locale);
}

export default i18n;
