import { Tabs } from 'expo-router';
import { useTranslation } from 'react-i18next';

import { BookIcon, ChartIcon, MoonIcon, UserIcon } from '../../src/components/Icons';
import { colors, fonts } from '../../src/theme/tokens';

export default function TabsLayout() {
  const { t } = useTranslation();
  const tint = (focused: boolean) => (focused ? colors.gold : colors.lilacDim);

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: 'rgba(18,13,44,0.94)',
          borderTopColor: 'rgba(167,155,200,0.14)',
          borderTopWidth: 1,
          height: 84,
          paddingTop: 10,
        },
        tabBarLabelStyle: { fontFamily: fonts.semibold, fontSize: 10.5 },
        tabBarActiveTintColor: colors.gold,
        tabBarInactiveTintColor: colors.lilacDim,
        sceneStyle: { backgroundColor: colors.midnight },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t('tabs.dream'),
          tabBarIcon: ({ focused }) => <MoonIcon color={tint(focused)} />,
        }}
      />
      <Tabs.Screen
        name="journal"
        options={{
          title: t('tabs.journal'),
          tabBarIcon: ({ focused }) => <BookIcon color={tint(focused)} />,
        }}
      />
      <Tabs.Screen
        name="insights"
        options={{
          title: t('tabs.insights'),
          tabBarIcon: ({ focused }) => <ChartIcon color={tint(focused)} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: t('tabs.profile'),
          tabBarIcon: ({ focused }) => <UserIcon color={tint(focused)} />,
        }}
      />
    </Tabs>
  );
}
