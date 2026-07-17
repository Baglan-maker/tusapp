import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { useProfile } from '../hooks/useProfile';
import { useSession } from '../hooks/useSession';
import { setLocale } from '../i18n';

/**
 * Applies the saved profile language on every launch. Without this, i18n falls
 * back to the device locale — a Kazakh-first user on a Russian phone would keep
 * getting a Russian UI despite choosing kk. Renders nothing.
 */
export function LocaleSync() {
  const { session } = useSession();
  const { data: profile } = useProfile(Boolean(session));
  const { i18n } = useTranslation();

  useEffect(() => {
    if (profile?.locale && profile.locale !== i18n.language) {
      setLocale(profile.locale);
    }
  }, [profile?.locale, i18n.language]);

  return null;
}
