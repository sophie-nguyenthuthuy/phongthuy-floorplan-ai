import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import type { RootStackParamList } from "../../App";
import { api, ApiError } from "@/api/client";
import { COLORS } from "@/theme/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Upload">;

export function UploadScreen({ navigation }: Props) {
  const [uri, setUri] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.9,
    });
    if (!result.canceled && result.assets[0]) {
      setUri(result.assets[0].uri);
    }
  };

  const upload = async () => {
    if (!uri) return;
    setUploading(true);
    try {
      const filename = uri.split("/").pop() ?? "plan.png";
      const result = await api.uploadFloorPlan(uri, filename);
      navigation.replace("Analysis", { floorPlanId: result.id });
    } catch (err) {
      const msg = err instanceof ApiError ? `${err.message}` : "Tải lên thất bại";
      Alert.alert("Lỗi", msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.help}>
          Chọn ảnh bản vẽ mặt bằng (PNG/JPG). Để có kết quả tốt nhất, đảm bảo hướng Bắc rõ ràng
          và toàn bộ căn nhà nằm trong khung ảnh.
        </Text>

        <Pressable style={styles.imageBox} onPress={pickImage}>
          {uri ? (
            <Image source={{ uri }} style={styles.preview} resizeMode="contain" />
          ) : (
            <Text style={styles.imageBoxText}>Bấm để chọn ảnh</Text>
          )}
        </Pressable>

        <Pressable
          style={[styles.primary, (!uri || uploading) && styles.disabled]}
          disabled={!uri || uploading}
          onPress={upload}
        >
          {uploading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryText}>Phân tích</Text>
          )}
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1, padding: 24, gap: 16 },
  help: { color: COLORS.textMuted, fontSize: 14, lineHeight: 20 },
  imageBox: {
    flex: 1,
    minHeight: 280,
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderStyle: "dashed",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  imageBoxText: { color: COLORS.textMuted, fontSize: 16 },
  preview: { width: "100%", height: "100%" },
  primary: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  primaryText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  disabled: { opacity: 0.4 },
});
