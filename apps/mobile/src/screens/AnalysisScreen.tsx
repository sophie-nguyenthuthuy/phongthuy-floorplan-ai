import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import type { RootStackParamList } from "../../App";
import { api, ApiError, type FloorPlanAnalyzeResponse, type RoomType } from "@/api/client";
import { COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Analysis">;

const ROOM_LABELS: Record<RoomType, string> = {
  phong_khach: "Phòng khách",
  phong_ngu: "Phòng ngủ",
  phong_bep: "Phòng bếp",
  phong_tam: "Phòng tắm",
  phong_an: "Phòng ăn",
  phong_tho: "Phòng thờ",
  san_gieng_troi: "Sân giếng trời",
  ban_cong: "Ban công",
  hanh_lang: "Hành lang",
  cau_thang: "Cầu thang",
  khong_xac_dinh: "Không xác định",
};

export function AnalysisScreen({ route }: Props) {
  const { floorPlanId } = route.params;
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<FloorPlanAnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    api
      .analyzeFloorPlan(floorPlanId)
      .then((res) => active && setData(res))
      .catch(
        (err) => active && setError(err instanceof ApiError ? err.message : "Không xác định"),
      )
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [floorPlanId]);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Phân tích bản vẽ</Text>
        <Text style={styles.muted}>ID: {floorPlanId}</Text>

        {loading && (
          <View style={styles.card}>
            <ActivityIndicator color={COLORS.primary} />
            <Text style={styles.muted}>Đang bóc tách tường, phòng và cửa…</Text>
          </View>
        )}

        {error && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Lỗi</Text>
            <Text style={styles.muted}>{error}</Text>
          </View>
        )}

        {data && (
          <>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>
                {data.floor_plan.rooms.length} phòng được nhận diện
              </Text>
              <Text style={styles.muted}>
                Ảnh {data.floor_plan.width_px}×{data.floor_plan.height_px}px
                {data.floor_plan.scale_m_per_px
                  ? ` · tỉ lệ ${(1 / data.floor_plan.scale_m_per_px).toFixed(1)} px/m`
                  : " · tỉ lệ chưa xác định"}
              </Text>
            </View>

            {data.floor_plan.rooms.map((room, i) => (
              <View key={`${room.type}-${i}`} style={styles.roomRow}>
                <Text style={styles.roomName}>{ROOM_LABELS[room.type] ?? room.type}</Text>
                <Text style={styles.roomMeta}>
                  {room.area_m2} m² · tin cậy {Math.round(room.confidence * 100)}%
                </Text>
              </View>
            ))}

            {data.notes.length > 0 && (
              <View style={styles.card}>
                <Text style={styles.cardTitle}>Lưu ý phong thủy</Text>
                {data.notes.map((n, i) => (
                  <Text key={i} style={styles.note}>
                    • {n}
                  </Text>
                ))}
              </View>
            )}
          </>
        )}
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
  roomRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  roomName: { fontSize: 16, fontWeight: "600", color: COLORS.text },
  roomMeta: { fontSize: 13, color: COLORS.textMuted },
  note: { fontSize: 14, color: COLORS.text, lineHeight: 20 },
});
