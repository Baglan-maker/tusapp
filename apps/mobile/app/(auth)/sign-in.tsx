import * as AppleAuthentication from 'expo-apple-authentication';
import { makeRedirectUri } from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Platform, StyleSheet, TextInput, View } from 'react-native';

import { Body, Display, GhostButton, GoldButton } from '../../src/components/ui';
import { Screen } from '../../src/components/Screen';
import { supabase } from '../../src/lib/supabase';
import { colors, fonts, radius, spacing } from '../../src/theme/tokens';

WebBrowser.maybeCompleteAuthSession();

export default function SignIn() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function signInWithApple() {
    try {
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [AppleAuthentication.AppleAuthenticationScope.EMAIL],
      });
      if (!credential.identityToken) throw new Error('no identity token');
      const { error } = await supabase.auth.signInWithIdToken({
        provider: 'apple',
        token: credential.identityToken,
      });
      if (error) setError(error.message);
    } catch {
      // User cancelled the sheet — not an error worth showing.
    }
  }

  async function signInWithGoogle() {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: makeRedirectUri({ scheme: 'tus' }), skipBrowserRedirect: true },
    });
    if (error) return setError(error.message);
    if (data.url) await WebBrowser.openAuthSessionAsync(data.url, makeRedirectUri({ scheme: 'tus' }));
  }

  async function signInWithEmail() {
    setError(null);
    const { error } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: makeRedirectUri({ scheme: 'tus' }) },
    });
    if (error) return setError(error.message);
    setSent(true);
  }

  return (
    <Screen style={styles.screen} stars={24}>
      <View style={styles.header}>
        <Display size={64}>{t('auth.title')}</Display>
        <Body muted style={{ marginTop: spacing.sm }}>
          {t('auth.subtitle')}
        </Body>
      </View>

      <View style={styles.actions}>
        {Platform.OS === 'ios' && (
          <AppleAuthentication.AppleAuthenticationButton
            buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN}
            buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.WHITE}
            cornerRadius={radius.button}
            style={styles.apple}
            onPress={signInWithApple}
          />
        )}

        <GhostButton label={t('auth.google')} onPress={signInWithGoogle} />

        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder={t('auth.emailPlaceholder')}
          placeholderTextColor={colors.lilacDim}
          autoCapitalize="none"
          keyboardType="email-address"
          inputMode="email"
          style={styles.input}
        />
        <GoldButton
          label={sent ? t('auth.emailSent') : t('auth.emailSend')}
          onPress={signInWithEmail}
          disabled={!email.includes('@') || sent}
        />

        {error && (
          <Body muted size={12} style={{ marginTop: spacing.sm, textAlign: 'center' }}>
            {error}
          </Body>
        )}
        <Body muted size={11} style={styles.note}>
          {t('auth.devOnly')}
        </Body>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between', paddingBottom: spacing.xxl },
  header: { marginTop: '30%' },
  actions: { gap: spacing.sm },
  apple: { height: 56, marginBottom: spacing.xs },
  input: {
    height: 56,
    borderRadius: radius.button,
    paddingHorizontal: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.dawn,
    fontFamily: fonts.medium,
    fontSize: 15,
  },
  note: { textAlign: 'center', marginTop: spacing.xs },
});
