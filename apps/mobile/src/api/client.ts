import Constants from "expo-constants";

const API_BASE_URL: string =
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ?? "http://localhost:8000";

export type GioiTinh = "nam" | "nu";

export type CungMenhRequest = {
  nam_sinh: number;
  gioi_tinh: GioiTinh;
};

export type HuongRelation = {
  huong: string;
  quan_he: string;
  diem: number;
};

export type CungMenhResponse = {
  cung_menh: string;
  label_vi: string;
  nhom: "dong_tu_menh" | "tay_tu_menh";
  huong_tot: HuongRelation[];
  huong_xau: HuongRelation[];
};

export type FloorPlanUploadResponse = {
  id: string;
  filename: string;
  size_bytes: number;
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
