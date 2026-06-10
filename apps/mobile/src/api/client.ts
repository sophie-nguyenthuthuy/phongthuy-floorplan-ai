import Constants from "expo-constants";

const API_BASE_URL: string =
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ?? "http://localhost:8000";

export type GioiTinh = "nam" | "nu";

export type CungMenhRequest = {
  nam_sinh: number;
  thang_sinh: number;
  ngay_sinh: number;
  gioi_tinh: GioiTinh;
};

export type HuongRelation = {
  huong: string;
  huong_label_vi: string;
  quan_he: string;
  diem: number;
};

export type CungMenhResponse = {
  cung_menh: string;
  label_vi: string;
  label_en: string;
  element: "kim" | "moc" | "thuy" | "hoa" | "tho";
  nhom: "dong_tu_menh" | "tay_tu_menh";
  huong_chinh: string;
  huong_tot: HuongRelation[];
  huong_xau: HuongRelation[];
};

export type FloorPlanUploadResponse = {
  id: string;
  filename: string;
  size_bytes: number;
};

export type RoomType =
  | "phong_khach"
  | "phong_ngu"
  | "phong_bep"
  | "phong_tam"
  | "phong_an"
  | "phong_tho"
  | "san_gieng_troi"
  | "ban_cong"
  | "hanh_lang"
  | "cau_thang"
  | "khong_xac_dinh";

export type Point = { x: number; y: number };

export type Room = {
  type: RoomType;
  polygon: Point[];
  area_m2: number;
  confidence: number;
};

export type FloorPlan = {
  width_px: number;
  height_px: number;
  scale_m_per_px: number | null;
  walls: unknown[];
  doors: unknown[];
  rooms: Room[];
  north_angle_deg: number | null;
};

export type FloorPlanAnalyzeResponse = {
  id: string;
  floor_plan: FloorPlan;
  notes: string[];
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(`API ${response.status} on ${path}`, response.status, body);
  }
  return body as T;
}

export const api = {
  baseUrl: API_BASE_URL,

  health: () => request<{ status: string; version: string }>("/health"),

  analyzeCungMenh: (payload: CungMenhRequest) =>
    request<CungMenhResponse>("/analyses/cung-menh", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  analyzeFloorPlan: (id: string) =>
    request<FloorPlanAnalyzeResponse>(`/floor-plans/${id}/analyze`),

  uploadFloorPlan: async (uri: string, filename: string): Promise<FloorPlanUploadResponse> => {
    const form = new FormData();
    // React Native FormData accepts this shape — TS types are a bit loose.
    form.append("file", {
      uri,
      name: filename,
      type: "image/png",
    } as unknown as Blob);

    const response = await fetch(`${API_BASE_URL}/floor-plans`, {
      method: "POST",
      body: form,
    });
    const body: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      throw new ApiError(`Upload failed (${response.status})`, response.status, body);
    }
    return body as FloorPlanUploadResponse;
  },
};
