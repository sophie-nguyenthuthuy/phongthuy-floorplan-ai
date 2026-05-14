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
import { COLORS, NGU_HANH_COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "CungMenh">;

export function CungMenhScreen({ navigation: _navigation }: Props) {
  const [day, setDay] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [gioiTinh, setGioiTinh] = useState<GioiTinh>("nam");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CungMenhResponse | null>(null);

  const submit = async () => {
    const d = Number.parseInt(day, 10);
    const m = Number.parseInt(month, 10);
    const y = Number.parseInt(year, 10);
    if (
      Number.isNaN(d) ||
      Number.isNaN(m) ||
      Number.isNaN(y) ||
      d < 1 ||
      d > 31 ||
      m < 1 ||
      m > 12 ||
      y < 1900 ||
      y > 2100
    ) {
      Alert.alert("Ngày sinh không hợp lệ", "Nhập ngày, tháng, năm dương lịch hợp lệ.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.analyzeCungMenh({
        nam_sinh: y,
        thang_sinh: m,
        ngay_sinh: d,
        gioi_tinh: gioiTinh,
      });
      setResult(res);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Không xác định";
      Alert.alert("Lỗi", msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.help}>
          Năm phong thủy tính theo Lập Xuân (~4/2). Sinh trước Lập Xuân được tính sang năm trước.
        </Text>

        <Text style={styles.label}>Ngày sinh dương lịch</Text>
        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.flex1]}
            keyboardType="number-pad"
            maxLength={2}
            placeholder="Ngày"
            value={day}
            onChangeText={setDay}
          />
          <TextInput
            style={[styles.input, styles.flex1]}
            keyboardType="number-pad"
            maxLength={2}
            placeholder="Tháng"
            value={month}
            onChangeText={setMonth}
          />
          <TextInput
            style={[styles.input, styles.flex2]}
            keyboardType="number-pad"
            maxLength={4}
            placeholder="Năm"
            value={year}
            onChangeText={setYear}
          />
        </View>

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
              Cung {result.label_vi}{" "}
              <Text style={{ color: NGU_HANH_COLORS[result.element] }}>
                ({result.element.toUpperCase()})
              </Text>
            </Text>
            <Text style={styles.muted}>
              {result.nhom === "dong_tu_menh" ? "Đông tứ mệnh" : "Tây tứ mệnh"} · hướng chính:{" "}
              {result.huong_chinh}
            </Text>

            <Text style={styles.section}>Hướng tốt</Text>
            {result.huong_tot.map((h) => (
              <Text key={`g-${h.huong}`} style={styles.good}>
                {h.huong_label_vi} — {h.quan_he} (+{h.diem})
              </Text>
            ))}

            <Text style={styles.section}>Hướng xấu</Text>
            {result.huong_xau.map((h) => (
              <Text key={`b-${h.huong}`} style={styles.bad}>
                {h.huong_label_vi} — {h.quan_he} ({h.diem})
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
  help: { color: COLORS.textMuted, fontSize: 13, fontStyle: "italic" },
  label: { fontSize: 14, color: COLORS.textMuted, marginTop: 8 },
  row: { flexDirection: "row", gap: 12 },
  flex1: { flex: 1 },
  flex2: { flex: 2 },
  input: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: COLORS.text,
  },
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
  resultTitle: { fontSize: 22, fontWeight: "700", color: COLORS.text },
  muted: { color: COLORS.textMuted, fontSize: 14 },
  section: { fontSize: 14, fontWeight: "600", color: COLORS.textMuted, marginTop: 8 },
  good: { color: COLORS.good, fontSize: 15 },
  bad: { color: COLORS.bad, fontSize: 15 },
});
