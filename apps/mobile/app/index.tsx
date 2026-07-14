import { Redirect } from 'expo-router';
import { View } from 'react-native';

import { useProfile } from '../src/hooks/useProfile';
import { useSession } from '../src/hooks/useSession';
import { colors } from '../src/theme/tokens';

/**
 * The gate. No session -> auth. Session but not onboarded -> onboarding.
 * Otherwise -> the tabs.
 */
export default function Index() {
  const { session, loading } = useSession();
  const { data: profile, isPending } = useProfile(Boolean(session));

  if (loading) return <Splash />;
  if (!session) return <Redirect href="/(auth)/sign-in" />;
  if (isPending || !profile) return <Splash />;
  if (!profile.onboarding_completed) return <Redirect href="/(onboarding)/language" />;
  return <Redirect href="/(tabs)" />;
}

function Splash() {
  return <View style={{ flex: 1, backgroundColor: colors.midnight }} />;
}
