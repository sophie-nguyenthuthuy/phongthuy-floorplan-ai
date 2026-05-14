import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

import type { RootStackParamList } from "../../App";
import { COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Home">;

export function HomeScreen({ navigation }: Props) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.title}>Phong Thủy + Floor Plan AI</Text>
        <Text style={styles.subtitle}>
          Phân tích bản vẽ mặt bằng theo bát trạch, cung mệnh và ngũ hành.
        </Text>

        <Pressable
          style={styles.primaryButton}
          onPress={() => navigation.navigate("Upload")}
        >
          <Text style={styles.primaryButtonText}>Tải bản vẽ mặt bằng</Text>
        </Pressable>

        <Pressable
          style={styles.secondaryButton}
          onPress={() => navigation.navigate("CungMenh")}
        >
          <Text style={styles.secondaryButtonText}>Tra cứu cung mệnh</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.background },
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 32,
    gap: 16,
  },
  title: { fontSize: 28, fontWeight: "700", color: COLORS.text },
  subtitle: { fontSize: 16, color: COLORS.textMuted, marginBottom: 24 },
  primaryButton: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  primaryButtonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  secondaryButton: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  secondaryButtonText: { color: COLORS.text, fontSize: 16, fontWeight: "600" },
});
