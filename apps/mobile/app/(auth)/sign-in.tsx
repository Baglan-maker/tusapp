import * as AppleAuthentication from 'expo-apple-authentication';
import { makeRedirectUri } from 'expo-auth-session';
import { useRouter } from 'expo-router';
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
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [sending, setSending] = useState(false);
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
    const address = email.trim();
    setError(null);
    setSending(true);
    // No emailRedirectTo: we want a 6-digit OTP code, not a magic link.
    const { error } = await supabase.auth.signInWithOtp({ email: address });
    setSending(false);
    if (error) {
      console.error('[auth] signInWithOtp failed', error);
      return setError(t('auth.sendError'));
    }
    router.push({ pathname: '/(auth)/verify', params: { email: address } });
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
          label={t('auth.emailSend')}
          onPress={signInWithEmail}
          disabled={!email.includes('@') || sending}
        />

        {error && (
          <Body muted size={12} style={{ marginTop: spacing.sm, textAlign: 'center' }}>
            {error}
          </Body>
        )}
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
});
