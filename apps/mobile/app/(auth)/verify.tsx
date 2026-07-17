import { useLocalSearchParams, useRouter } from 'expo-router';
import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, TextInput, View } from 'react-native';

import { Body, Display, GhostButton, GoldButton } from '../../src/components/ui';
import { Screen } from '../../src/components/Screen';
import { supabase } from '../../src/lib/supabase';
import { colors, fonts, radius, spacing } from '../../src/theme/tokens';

const CODE_LENGTH = 6;

export default function Verify() {
  const { t } = useTranslation();
  const router = useRouter();
  const { email } = useLocalSearchParams<{ email: string }>();
  const inputRef = useRef<TextInput>(null);
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  async function verify(token: string) {
    if (!email || token.length < CODE_LENGTH || verifying) return;
    setError(null);
    setVerifying(true);
    const { error } = await supabase.auth.verifyOtp({ email, token, type: 'email' });
    setVerifying(false);
    if (error) {
      console.error('[auth] verifyOtp failed', error);
      setCode('');
      setError(t('auth.verify.error'));
      inputRef.current?.focus();
      return;
    }
    // Session is now set; onAuthStateChange fires. Send the user back through
    // the gate in app/index.tsx, which routes to onboarding or the tabs.
    router.replace('/');
  }

  function onChange(next: string) {
    const digits = next.replace(/\D/g, '').slice(0, CODE_LENGTH);
    setCode(digits);
    if (error) setError(null);
    if (digits.length === CODE_LENGTH) void verify(digits);
  }

  async function resend() {
    if (!email) return;
    setError(null);
    setCode('');
    const { error } = await supabase.auth.signInWithOtp({ email });
    if (error) {
      console.error('[auth] resend signInWithOtp failed', error);
      setError(t('auth.sendError'));
      return;
    }
    inputRef.current?.focus();
  }

  return (
    <Screen style={styles.screen} stars={24}>
      <View style={styles.header}>
        <Display size={48}>{t('auth.verify.title')}</Display>
        <Body muted style={{ marginTop: spacing.sm }}>
          {t('auth.verify.subtitle', { email })}
        </Body>
      </View>

      <View style={styles.actions}>
        <View style={styles.codeWrap}>
          <View style={styles.boxes} pointerEvents="none">
            {Array.from({ length: CODE_LENGTH }).map((_, i) => {
              const active = i === code.length;
              return (
                <View key={i} style={[styles.box, (i < code.length || active) && styles.boxActive]}>
                  <Body size={22} style={styles.digit}>
                    {code[i] ?? ''}
                  </Body>
                </View>
              );
            })}
          </View>
          {/* Invisible input laid over the boxes: captures taps, keyboard and
              iOS one-time-code autofill while the boxes do the drawing. */}
          <Pressable style={styles.inputHit} onPress={() => inputRef.current?.focus()}>
            <TextInput
              ref={inputRef}
              value={code}
              onChangeText={onChange}
              autoFocus
              keyboardType="number-pad"
              textContentType="oneTimeCode"
              autoComplete="one-time-code"
              maxLength={CODE_LENGTH}
              caretHidden
              style={styles.hiddenInput}
            />
          </Pressable>
        </View>

        <GoldButton
          label={t('auth.verify.submit')}
          onPress={() => verify(code)}
          disabled={code.length < CODE_LENGTH || verifying}
        />

        {error && (
          <Body muted size={12} style={{ textAlign: 'center' }}>
            {error}
          </Body>
        )}

        <GhostButton label={t('auth.verify.resend')} onPress={resend} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between', paddingBottom: spacing.xxl },
  header: { marginTop: '30%' },
  actions: { gap: spacing.md },
  codeWrap: { position: 'relative' },
  boxes: { flexDirection: 'row', gap: spacing.sm },
  box: {
    flex: 1,
    height: 60,
    borderRadius: radius.chip,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  boxActive: { borderColor: colors.borderGold },
  digit: { fontFamily: fonts.semibold, color: colors.dawn },
  inputHit: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  hiddenInput: { flex: 1, opacity: 0 },
});
