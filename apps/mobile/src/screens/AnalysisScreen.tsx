import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

import type { RootStackParamList } from "../../App";
import { COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Analysis">;

export function AnalysisScreen({ route }: Props) {
  const { floorPlanId } = route.params;

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Phân tích bản vẽ</Text>
        <Text style={styles.muted}>ID: {floorPlanId}</Text>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Đang xử lý…</Text>
          <Text style={styles.muted}>
            Pipeline CV sẽ phân tích tường, phòng và cửa, sau đó overlay bát quái lên bản vẽ.
            Tính năng này chưa được triển khai trong scaffold ban đầu.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.background },
  container: { padding: 24, gap: 12 },
  title: { fontSize: 24, fontWeight: "700", color: COLORS.text },
  muted: { color: COLORS.textMuted, fontSize: 14 },
  card: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: 8,
    marginTop: 16,
  },
  cardTitle: { fontSize: 18, fontWeight: "600", color: COLORS.text },
});
