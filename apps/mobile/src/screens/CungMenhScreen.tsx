import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import type { RootStackParamList } from "../../App";
import { api, ApiError, type CungMenhResponse, type GioiTinh } from "@/api/client";
import { COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "CungMenh">;

export function CungMenhScreen({ navigation: _navigation }: Props) {
  const [namSinh, setNamSinh] = useState("");
  const [gioiTinh, setGioiTinh] = useState<GioiTinh>("nam");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CungMenhResponse | null>(null);

  const submit = async () => {
    const year = Number.parseInt(namSinh, 10);
    if (Number.isNaN(year) || year < 1900 || year > 2100) {
      Alert.alert("Năm sinh không hợp lệ", "Nhập năm trong khoảng 1900–2100.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.analyzeCungMenh({ nam_sinh: year, gioi_tinh: gioiTinh });
      setResult(res);
    } catch (err) {
      if (err instanceof ApiError && err.status === 501) {
        Alert.alert(
          "Chưa triển khai",
          "Công thức tính cung mệnh cần được chuyên gia phong thủy xác thực trước khi bật.",
        );
      } else {
        Alert.alert("Lỗi", err instanceof Error ? err.message : "Không xác định");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.label}>Năm sinh (dương lịch)</Text>
        <TextInput
          style={styles.input}
          keyboardType="number-pad"
          maxLength={4}
          value={namSinh}
          onChangeText={setNamSinh}
          placeholder="VD: 1990"
        />

        <Text style={styles.label}>Giới tính</Text>
        <View style={styles.row}>
          <Pressable
            style={[styles.choice, gioiTinh === "nam" && styles.choiceActive]}
            onPress={() => setGioiTinh("nam")}
          >
            <Text style={gioiTinh === "nam" ? styles.choiceTextActive : styles.choiceText}>
              Nam
            </Text>
          </Pressable>
          <Pressable
            style={[styles.choice, gioiTinh === "nu" && styles.choiceActive]}
            onPress={() => setGioiTinh("nu")}
          >
            <Text style={gioiTinh === "nu" ? styles.choiceTextActive : styles.choiceText}>
              Nữ
            </Text>
          </Pressable>
        </View>

        <Pressable style={styles.primary} disabled={loading} onPress={submit}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryText}>Tra cứu</Text>
          )}
        </Pressable>

        {result && (
          <View style={styles.result}>
            <Text style={styles.resultTitle}>
              Cung {result.label_vi} ({result.nhom === "dong_tu_menh" ? "Đông tứ" : "Tây tứ"})
            </Text>

            <Text style={styles.section}>Hướng tốt</Text>
            {result.huong_tot.map((h) => (
              <Text key={`g-${h.huong}`} style={styles.good}>
                {h.huong} — {h.quan_he} (+{h.diem})
              </Text>
            ))}

            <Text style={styles.section}>Hướng xấu</Text>
            {result.huong_xau.map((h) => (
              <Text key={`b-${h.huong}`} style={styles.bad}>
                {h.huong} — {h.quan_he} ({h.diem})
              </Text>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.background },
  container: { padding: 24, gap: 12 },
  label: { fontSize: 14, color: COLORS.textMuted, marginTop: 8 },
  input: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: COLORS.text,
  },
  row: { flexDirection: "row", gap: 12 },
  choice: {
    flex: 1,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: "center",
  },
  choiceActive: { backgroundColor: COLORS.primary, borderColor: COLORS.primary },
  choiceText: { color: COLORS.text, fontSize: 16 },
  choiceTextActive: { color: "#fff", fontSize: 16, fontWeight: "600" },
  primary: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 16,
  },
  primaryText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  result: { marginTop: 24, gap: 6 },
  resultTitle: { fontSize: 20, fontWeight: "700", color: COLORS.text },
  section: { fontSize: 14, fontWeight: "600", color: COLORS.textMuted, marginTop: 8 },
  good: { color: COLORS.good, fontSize: 15 },
  bad: { color: COLORS.bad, fontSize: 15 },
});
