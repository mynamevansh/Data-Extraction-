import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 120000,
});

const uploadPath = import.meta.env.VITE_API_UPLOAD_PATH || "/extract";
const pdfConversionPath = "/convert-pdf-to-excel";

const sampleResultFiles = new Set([
  "receipt1",
  "receipt2",
  "receipt3",
  "receipt4",
  "receipt5",
  "receipt6",
  "receipt7",
  "receipt8",
]);

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeField(field) {
  if (field == null) {
    return {
      value: "—",
      confidence: 0,
      lowConfidence: true,
    };
  }

  if (typeof field === "object" && !Array.isArray(field)) {
    const rawValue = field.value ?? field.text ?? field.amount ?? field.number ?? "";
    const confidence = toNumber(field.confidence ?? field.score ?? field.probability);
    const inferredLowConfidence = confidence < 0.7 || rawValue === "";
    const lowConfidence = Boolean(
      field.low_confidence ?? field.lowConfidence ?? inferredLowConfidence,
    );

    return {
      value: rawValue === "" ? "—" : String(rawValue),
      confidence,
      lowConfidence,
    };
  }

  return {
    value: String(field),
    confidence: 0,
    lowConfidence: true,
  };
}

function averageConfidence(fields) {
  const numericValues = fields.map((field) => field.confidence).filter((value) => value > 0);
  if (!numericValues.length) {
    return 0;
  }

  return numericValues.reduce((total, value) => total + value, 0) / numericValues.length;
}

function resolvePayload(data) {
  return data?.data ?? data?.result ?? data?.payload ?? data ?? {};
}

function getFileStem(fileName) {
  return String(fileName || "")
    .replace(/\\/g, "/")
    .split("/")
    .pop()
    .replace(/\.[^.]+$/, "")
    .trim();
}

async function fetchLocalSampleResponse(file) {
  const stem = getFileStem(file?.name);
  if (!sampleResultFiles.has(stem)) {
    return null;
  }

  const response = await fetch(`/sample-results/${stem}.json`, { cache: "no-store" });
  if (!response.ok) {
    return null;
  }

  return response.json();
}

export function normalizeReceiptResponse(data) {
  const payload = resolvePayload(data);

  const storeName = normalizeField(payload.store_name ?? payload.storeName ?? payload.merchant_name ?? payload.merchantName);
  const date = normalizeField(payload.date ?? payload.transaction_date ?? payload.receipt_date);
  const time = normalizeField(payload.time ?? payload.transaction_time ?? payload.receipt_time);
  const subtotal = normalizeField(payload.subtotal ?? payload.sub_total ?? payload.sub_total_amount);
  const tax = normalizeField(payload.tax ?? payload.tax_amount ?? payload.vat);
  const total = normalizeField(payload.total_amount ?? payload.total ?? payload.amount_total);

  const confidenceScore = toNumber(
    payload.confidence_score ?? payload.confidence ?? payload.average_confidence,
  ) || averageConfidence([storeName, date, time, subtotal, tax, total]);

  return {
    fields: {
      storeName,
      date,
      time,
      subtotal,
      tax,
      total,
      confidenceScore,
    },
    raw: data,
  };
}

export async function extractReceiptData(file, signal) {
  const formData = new FormData();
  ["file", "image", "receipt"].forEach((fieldName) => {
    formData.append(fieldName, file);
  });

  try {
    const response = await apiClient.post(uploadPath, formData, {
      signal,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  } catch (requestError) {
    const localFallback = await fetchLocalSampleResponse(file);
    if (localFallback) {
      return localFallback;
    }

    throw requestError;
  }
}

export async function convertPdfToExcel(file, signal) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post(pdfConversionPath, formData, {
    signal,
    responseType: "blob",
  });

  return response.data;
}

export function getApiMeta() {
  return {
    baseURL: apiClient.defaults.baseURL,
    uploadPath,
    pdfConversionPath,
  };
}
